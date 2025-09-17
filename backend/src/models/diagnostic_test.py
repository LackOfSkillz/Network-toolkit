from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from backend.src.db import Base

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String)
    destination_ip = Column(String)
    port = Column(Integer)
    results = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
