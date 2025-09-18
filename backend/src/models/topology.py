from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.db import Base


"""
Represents topology links between devices.

Links are directional (source -> target) and have a `link_type` such as
`lldp` to indicate how the link was discovered.
"""


class TopologyLink(Base):
    __tablename__ = 'topology_links'
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    source_device_id = Column(Integer, ForeignKey('network_devices.id'))
    target_device_id = Column(Integer, ForeignKey('network_devices.id'))
    link_type = Column(String, default='lldp')

    source_device = relationship("backend.src.models.network_device.NetworkDevice", foreign_keys=[source_device_id])
    target_device = relationship("backend.src.models.network_device.NetworkDevice", foreign_keys=[target_device_id])
