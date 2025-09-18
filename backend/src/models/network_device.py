from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base


class NetworkDevice(Base):
    """Represents a single network device in the system.

    Each device has identifying fields (name, management IP, MAC) and
    optional configuration information. This model is used by discovery
    flows (LLDP/SNMP) and by admin CRUD endpoints.
    """

    # Name of the table used in the database
    __tablename__ = "network_devices"
    __table_args__ = {"extend_existing": True}

    # Primary key id (unique integer identifier)
    id = Column(Integer, primary_key=True, index=True)

    # Human-friendly name for display
    name = Column(String, nullable=False)

    # Optional type (switch, router, server, etc.)
    type = Column(String)

    # Management address used to reach the device
    ip_address = Column(String)

    # Hardware MAC address (used for LLDP chassis matching)
    mac_address = Column(String)

    # Arbitrary JSON blob that may store device-specific configuration
    config = Column(JSON)

    # Boolean-ish integer: 0 = LLDP disabled, 1 = LLDP enabled
    enable_lldp = Column(Integer, default=0)

    # Timestamps (created_at set by DB default, updated_at set on modification)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Optional foreign-key linking to a saved NetworkConfiguration record
    configuration_id = Column(Integer, ForeignKey('network_configurations.id'))

    # Relationship object to the configuration model. We use the fully
    # qualified module path for robustness in test environments where
    # modules may be imported from different paths.
    configuration = relationship("backend.src.models.network_configuration.NetworkConfiguration", back_populates="devices")
