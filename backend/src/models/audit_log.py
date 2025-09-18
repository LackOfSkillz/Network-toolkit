from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String)
    entity = Column(String)
    entity_id = Column(Integer)
    changes = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("backend.src.models.user.User")
