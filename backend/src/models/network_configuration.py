from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base

class NetworkConfiguration(Base):
    __tablename__ = "network_configurations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    devices = relationship("NetworkDevice", back_populates="configuration", cascade="all, delete-orphan")
    firewall_rules = relationship("FirewallRule", back_populates="configuration", cascade="all, delete-orphan")
