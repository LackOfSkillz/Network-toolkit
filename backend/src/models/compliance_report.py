from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base


"""
Stores the result of a compliance evaluation run for a configuration.

`details` contains a JSON-serializable payload with the findings.
"""


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('network_configurations.id'))
    status = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    configuration = relationship("backend.src.models.network_configuration.NetworkConfiguration")
