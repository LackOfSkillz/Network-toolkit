from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base


"""
ORM models used to store LLDP/CDP collector runs and discovered neighbors.

CollectorRun: records a single collection attempt (when it started, finished,
and which device/source triggered it). NeighborRecord: the normalized
per-neighbor output of a collector run.

These models are intentionally straightforward so the collector logic can
persist results without complex joins.
"""


class CollectorRun(Base):
    __tablename__ = "collector_runs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    # When the collector started and finished. Server_default uses DB time.
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    # Human-readable source identifier such as 'snmp_lldp' or 'cli_lldp'
    source = Column(String)  # e.g., 'snmp_lldp', 'cli_lldp'
    device_id = Column(Integer, ForeignKey('network_devices.id'))
    # relationship points to the NetworkDevice that was scanned
    device = relationship("backend.src.models.network_device.NetworkDevice")
    note = Column(String)


class NeighborRecord(Base):
    __tablename__ = "neighbor_records"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    collector_run_id = Column(Integer, ForeignKey('collector_runs.id'))
    collector_run = relationship("backend.src.models.lldp.CollectorRun")

    # local device + interface where this neighbor was observed
    local_device_id = Column(Integer, ForeignKey('network_devices.id'))
    local_device = relationship("backend.src.models.network_device.NetworkDevice")
    local_interface = Column(String)

    # remote/neighbor fields (normalized from raw TLVs)
    remote_chassis_id = Column(String)
    remote_port_id = Column(String)
    remote_sys_name = Column(String)
    remote_sys_descr = Column(String)
    remote_mgmt_ips = Column(JSON)
    capabilities = Column(String)

    # provenance: where the neighbor data came from and raw TLV dump
    source = Column(String)  # 'snmp_lldp', 'snmp_cdp', 'cli'
    raw_tlvs = Column(JSON)
    # confidence is a heuristic score (0.0 - 1.0) for automated matching
    confidence = Column(Float, default=0.0)
    # last_seen is useful for showing freshness in the UI
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
