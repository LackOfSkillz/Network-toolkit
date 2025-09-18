from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.src.db import Base


"""
Defines a dashboard widget record. Widgets store a `config` blob (string)
that the UI understands to render charts/tables.
"""


class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    config = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
