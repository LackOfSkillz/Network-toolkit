"""
Service layer for dashboard widgets.

The service validates widget types and performs simple CRUD returning
plain dictionaries suitable for JSON responses. Keep logic here small so the
API layer's responsibilities are limited to request/response translation.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.src.models import DashboardWidget


class DashboardWidgetService:
    # only a small set of widget types are allowed today
    ALLOWED_TYPES = {"chart", "table"}

    def create(self, db: Session, name: str, wtype: str, config: Dict[str, Any]) -> Dict[str, Any]:
        if wtype not in self.ALLOWED_TYPES:
            raise ValueError("unsupported widget type")
        w = DashboardWidget(name=name, type=wtype, config=str(config))
        db.add(w)
        db.commit()
        db.refresh(w)
        return {"id": w.id, "name": w.name, "type": w.type, "config": w.config}

    def update(self, db: Session, wid: int, name: str | None = None, wtype: str | None = None, config: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
        w = db.query(DashboardWidget).filter(DashboardWidget.id == wid).first()
        if not w:
            return None
        if name is not None:
            w.name = name
        if wtype is not None:
            if wtype not in self.ALLOWED_TYPES:
                raise ValueError("unsupported widget type")
            w.type = wtype
        if config is not None:
            w.config = str(config)
        db.commit()
        db.refresh(w)
        return {"id": w.id, "name": w.name, "type": w.type, "config": w.config}

    def get(self, db: Session, wid: int) -> Dict[str, Any] | None:
        w = db.query(DashboardWidget).filter(DashboardWidget.id == wid).first()
        if not w:
            return None
        return {"id": w.id, "name": w.name, "type": w.type, "config": w.config}

    def delete(self, db: Session, wid: int) -> bool:
        w = db.query(DashboardWidget).filter(DashboardWidget.id == wid).first()
        if not w:
            return False
        db.delete(w)
        db.commit()
        return True

    def list(self, db: Session):
        rows = db.query(DashboardWidget).all()
        return [{"id": r.id, "name": r.name, "type": r.type} for r in rows]
