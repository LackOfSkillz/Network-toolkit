from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.src.db import Base


"""
Table storing user-saved UI views.

`view_blob` holds the UI state as a JSON-serializable string. The API and
service layers convert it to/from Python structures as needed.
"""


class SavedView(Base):
    __tablename__ = "saved_views"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    view_blob = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
