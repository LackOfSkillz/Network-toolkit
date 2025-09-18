"""LLDP collector service (SNMP-first).

This module provides a small helper to collect LLDP neighbor records via
SNMP. The implementation is intentionally light-weight so tests can exercise
the normalization logic without relying on a full SNMP environment. The
collector prefers SNMP-based LLDP (higher confidence) and returns a list of
normalized neighbor dicts.
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def _build_snmp_engine_and_target(snmp_params: Dict[str, Any]):
    # Lazy import pysnmp to avoid hard dependency at module import time
    try:
        from pysnmp.hlapi import CommunityData, UsmUserData, UdpTransportTarget, SnmpEngine
    except Exception as e:
        raise RuntimeError("pysnmp is required for SNMP collection") from e

    engine = SnmpEngine()

    version = snmp_params.get("version", "2c")
    if str(version).startswith("3"):
        # Minimal v3 support: expects dict with 'user', optional 'authKey'/'privKey', and auth/priv protocols
        user = snmp_params.get("user")
        authKey = snmp_params.get("authKey")
        privKey = snmp_params.get("privKey")
        user_data = UsmUserData(user, authKey, privKey)
    else:
        community = snmp_params.get("community", "public")
        user_data = CommunityData(community)

    target = UdpTransportTarget((snmp_params.get("host"), int(snmp_params.get("port", 161))))
    return engine, user_data, target


def collect_lldp_snmp(device: Dict[str, Any], snmp_params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Collect LLDP neighbors via SNMP for the given device.

    Supports SNMP v2c (community) and minimal SNMPv3 user fields. Returns a
    list of normalized neighbor dicts. The normalization maps common LLDP
    fields to a consistent schema that the rest of the app expects.
    """
    # OIDs (from LLDP-MIB): lldpRemChassisId, lldpRemPortId, lldpRemSysName,
    # lldpRemSysDesc, lldpRemManAddr, lldpRemPortDesc
    # We'll query these base OIDs and build records keyed by the instance suffix.
    try:
        from pysnmp.hlapi import ObjectType, ObjectIdentity, nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData
    except Exception:
        raise RuntimeError("pysnmp is required for SNMP collection; please install pysnmp")

    host = device.get("ip_address") or snmp_params.get("host")
    params = dict(snmp_params)
    params.setdefault("host", host)
    params.setdefault("port", 161)

    logger.info("collect_lldp_snmp: device=%s snmp_params=%s", host, {k: v for k, v in params.items() if k not in ("authKey", "privKey")})

    engine, user_data, target = _build_snmp_engine_and_target(params)

    oids = {
        "chassis": "1.0.8802.1.1.2.1.4.1.1.4",  # lldpRemChassisId
        "port": "1.0.8802.1.1.2.1.4.1.1.7",     # lldpRemPortId
        "sysName": "1.0.8802.1.1.2.1.4.1.1.9",   # lldpRemSysName
        "sysDesc": "1.0.8802.1.1.2.1.4.1.1.10",  # lldpRemSysDesc
        "mgmt": "1.0.8802.1.1.2.1.4.2.1.4",      # lldpRemManAddrIfSubtype? (approx)
        "portDesc": "1.0.8802.1.1.2.1.4.1.1.8",  # lldpRemPortDesc
    }

    # Walk each OID and collect values indexed by instance suffix
    results = {}

    for key, oid in oids.items():
        try:
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                engine,
                user_data,
                target,
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
            ):
                if errorIndication:
                    logger.debug("SNMP error: %s", errorIndication)
                    break
                elif errorStatus:
                    logger.debug("SNMP status error: %s at %s", errorStatus.prettyPrint(), errorIndex)
                    break
                else:
                    for varBind in varBinds:
                        name, val = varBind
                        # instance suffix is the remainder of the OID after the base OID
                        inst = name.prettyPrint().replace(oid + ".", "") if name.prettyPrint().startswith(oid + ".") else name.prettyPrint()
                        entry = results.setdefault(inst, {})
                        entry[key] = val.prettyPrint()
        except Exception as e:
            logger.debug("failed to walk %s: %s", oid, e)

    # Build normalized records
    records = []
    for inst, data in results.items():
        rec = {
            "local_device_id": device.get("id"),
            "local_interface": None,
            "remote_chassis_id": data.get("chassis"),
            "remote_port_id": data.get("port"),
            "remote_sys_name": data.get("sysName"),
            "remote_sys_descr": data.get("sysDesc"),
            "remote_mgmt_ips": [data.get("mgmt")] if data.get("mgmt") else [],
            "capabilities": None,
            "source": "snmp_lldp",
            "raw_tlvs": {k: data.get(k) for k in ("portDesc",)},
            "confidence": 0.9,
        }
        # Attempt to infer local interface from instance string (may vary by agent)
        if "." in inst:
            # common pattern: localPort.localIndex or similar; try last numeric component
            parts = inst.split('.')
            rec["local_interface"] = parts[-1]
        else:
            rec["local_interface"] = inst

        records.append(rec)

    return records
