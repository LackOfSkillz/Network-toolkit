from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base

class FirewallRule(Base):
    __tablename__ = "firewall_rules"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String)
    destination_ip = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    action = Column(String)
    priority = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)
    src_cidr = Column(String, nullable=True)
    dst_cidr = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    configuration_id = Column(Integer, ForeignKey('network_configurations.id'))
    configuration = relationship("backend.src.models.network_configuration.NetworkConfiguration", back_populates="firewall_rules")
