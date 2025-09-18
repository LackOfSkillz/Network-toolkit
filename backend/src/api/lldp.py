from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.src import db as dbmod
from backend.src.services.lldp_collector import collect_lldp_snmp
from backend.src.models.network_device import NetworkDevice
from backend.src.models.lldp import CollectorRun, NeighborRecord
from backend.src.models.topology import TopologyLink
from backend.src.models.audit_log import AuditLog
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

"""
Endpoints for LLDP/CDP discovery and neighbor management.

These routes are used by the frontend to trigger SNMP-based collection of
neighbor information, inspect discovered neighbors, accept or reject
discovered entries (which creates topology links and/or new devices), and
toggle collection on devices.

Design notes for non-developers:
- Each route receives a database session from the shared `db.get_db()`
    dependency so the handler only focuses on business logic.
- The `accept_neighbor` flow will try management-IP matching first, then
    chassis/mac matching, and will create a new `NetworkDevice` if no match
    is found.
"""

router = APIRouter(prefix="/lldp", tags=["lldp"])

@router.post("/collect/{device_id}")
def collect_for_device(device_id: int, db: Session = Depends(dbmod.get_db)):
    device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device not found")

    if not getattr(device, 'enable_lldp', 0):
        raise HTTPException(status_code=403, detail="LLDP collection is disabled for this device")

    # SNMP params would normally come from DB/credentials store; for now use a placeholder
    snmp_params = {"version": "2c", "community": "public", "host": device.ip_address}

    try:
        records = collect_lldp_snmp({"id": device.id, "ip_address": device.ip_address}, snmp_params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SNMP collection failed: {e}")

    # Persist collector run and neighbor records
    collector = CollectorRun(source="snmp_lldp", device_id=device.id)
    db.add(collector)
    db.flush()  # assign id

    saved = 0
    try:
        for r in records:
            nr = NeighborRecord(
                collector_run_id=collector.id,
                local_device_id=r.get("local_device_id"),
                local_interface=r.get("local_interface"),
                remote_chassis_id=r.get("remote_chassis_id"),
                remote_port_id=r.get("remote_port_id"),
                remote_sys_name=r.get("remote_sys_name"),
                remote_sys_descr=r.get("remote_sys_descr"),
                remote_mgmt_ips=r.get("remote_mgmt_ips"),
                capabilities=r.get("capabilities"),
                source=r.get("source"),
                raw_tlvs=r.get("raw_tlvs"),
                confidence=r.get("confidence", 0.0),
            )
            db.add(nr)
            saved += 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return {"device_id": device.id, "collector_run_id": collector.id, "saved": saved}


@router.post('/devices/{device_id}/enable')
def enable_lldp(device_id: int, enable: bool = True, db: Session = Depends(dbmod.get_db)):
    device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    device.enable_lldp = 1 if enable else 0
    db.add(device)
    db.commit()
    return {"device_id": device.id, "enable_lldp": bool(device.enable_lldp)}


@router.get('/devices/{device_id}/neighbors')
def get_neighbors(device_id: int, run: int | None = None, limit: int = 50, db: Session = Depends(dbmod.get_db)):
    device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device not found")

    q = db.query(NeighborRecord).filter(NeighborRecord.local_device_id == device_id)
    if run:
        q = q.filter(NeighborRecord.collector_run_id == run)
    rows = q.order_by(NeighborRecord.last_seen.desc()).limit(limit).all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "collector_run_id": r.collector_run_id,
            "local_interface": r.local_interface,
            "remote_chassis_id": r.remote_chassis_id,
            "remote_port_id": r.remote_port_id,
            "remote_sys_name": r.remote_sys_name,
            "remote_sys_descr": r.remote_sys_descr,
            "remote_mgmt_ips": r.remote_mgmt_ips,
            "confidence": r.confidence,
            "raw_tlvs": r.raw_tlvs,
            "last_seen": r.last_seen.isoformat() if r.last_seen else None,
        })
    return {"device_id": device_id, "neighbors": out}


@router.post('/devices/{device_id}/neighbors/accept')
def accept_neighbor(device_id: int, payload: dict, db: Session = Depends(dbmod.get_db)):
    """Accept a discovered neighbor: create NetworkDevice if not exists and create a TopologyLink.

    payload expected to contain either neighbor_id or the normalized neighbor dict.
    """
    device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device not found")

    neighbor_id = payload.get('neighbor_id')
    neighbor_data = payload.get('neighbor')
    if neighbor_id and not neighbor_data:
        nr = db.query(NeighborRecord).filter(NeighborRecord.id == neighbor_id).first()
        if not nr:
            raise HTTPException(status_code=404, detail="neighbor not found")
        neighbor_data = {
            'remote_mgmt_ips': nr.remote_mgmt_ips or [],
            'remote_chassis_id': nr.remote_chassis_id,
            'remote_sys_name': nr.remote_sys_name,
        }

    if not neighbor_data:
        raise HTTPException(status_code=400, detail='missing neighbor payload')

    # Try to match by management IP first
    mgmt_ips = neighbor_data.get('remote_mgmt_ips') or []
    found = None
    if mgmt_ips:
        for ip in mgmt_ips:
            found = db.query(NetworkDevice).filter(NetworkDevice.ip_address == ip).first()
            if found: break

    # Next try chassis/mac
    if not found and neighbor_data.get('remote_chassis_id'):
        found = db.query(NetworkDevice).filter(NetworkDevice.mac_address == neighbor_data.get('remote_chassis_id')).first()

    created = False
    if not found:
        # create a new device
        nd = NetworkDevice(
            name = neighbor_data.get('remote_sys_name') or f"discovered-{int(__import__('time').time())}",
            ip_address = mgmt_ips[0] if mgmt_ips else None,
            mac_address = neighbor_data.get('remote_chassis_id'),
            config = None,
            # inherit enable_lldp from parent device so discovery preserves toggle
            enable_lldp = getattr(device, 'enable_lldp', 0),
            # inherit configuration association from parent device if present
            configuration_id = getattr(device, 'configuration_id', None),
        )
        db.add(nd)
        db.flush()
        found = nd
        created = True

    # create topology link
    link = TopologyLink(source_device_id=device.id, target_device_id=found.id, link_type='lldp')
    db.add(link)
    db.commit()

    return {"accepted": True, "device_id": found.id, "created": created, "link_id": link.id}


@router.post('/devices/{device_id}/neighbors/{neighbor_id}/reject')
def reject_neighbor(device_id: int, neighbor_id: int, reason: str | None = None, db: Session = Depends(dbmod.get_db), user=None):
    # record the rejection in AuditLog for auditing
    device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    nr = db.query(NeighborRecord).filter(NeighborRecord.id == neighbor_id).first()
    if not nr:
        raise HTTPException(status_code=404, detail="neighbor not found")

    entry = AuditLog(user_id = None, action='reject_neighbor', entity='NeighborRecord', entity_id=neighbor_id, changes={'reason': reason})
    db.add(entry)
    db.commit()
    return {"rejected": True, "neighbor_id": neighbor_id}
