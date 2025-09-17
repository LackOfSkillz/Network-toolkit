from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.src.db import Base


class CustomCompliancePolicy(Base):
    __tablename__ = "custom_compliance_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    # naive: store policy expression as JSON/text (e.g., required rules)
    policy_blob = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
