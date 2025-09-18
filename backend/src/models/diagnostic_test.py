from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from backend.src.db import Base


"""
Stores diagnostic test requests and their JSON results (e.g., ping/traceroute).

Used by UI-driven tests and integration flows to persist diagnostic outputs.
"""


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String)
    destination_ip = Column(String)
    port = Column(Integer)
    results = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
