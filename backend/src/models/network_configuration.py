from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base

"""
Network configuration record which groups devices and firewall rules.

Used to model a saved configuration snapshot. Relationships point to devices
and firewall rules associated with this configuration.
"""


class NetworkConfiguration(Base):
    __tablename__ = "network_configurations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Use fully-qualified module paths to be explicit about targets which
    # avoids ambiguity when SQLAlchemy resolves class names in the mapper
    # registry across test imports.
    devices = relationship("backend.src.models.network_device.NetworkDevice", back_populates="configuration", cascade="all, delete-orphan")
    firewall_rules = relationship("backend.src.models.firewall_rule.FirewallRule", back_populates="configuration", cascade="all, delete-orphan")
