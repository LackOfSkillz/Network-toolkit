"""
Service layer for SavedView CRUD operations.

This small helper converts ORM objects to plain python dictionaries that are
returned by the API layer. The service intentionally stores the `view_blob`
as a string to keep the DB simple — the UI should treat it as JSON.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.src.models import SavedView


class SavedViewService:
    def create(self, db: Session, name: str, owner: str, view_blob: Dict[str, Any]) -> Dict[str, Any]:
        sv = SavedView(name=name, owner=owner, view_blob=str(view_blob))
        db.add(sv)
        db.commit()
        db.refresh(sv)
        return {"id": sv.id, "name": sv.name, "owner": sv.owner, "view_blob": sv.view_blob}

    def update(self, db: Session, sv_id: int, name: str | None = None, view_blob: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
        sv = db.query(SavedView).filter(SavedView.id == sv_id).first()
        if not sv:
            return None
        if name is not None:
            sv.name = name
        if view_blob is not None:
            sv.view_blob = str(view_blob)
        db.commit()
        db.refresh(sv)
        return {"id": sv.id, "name": sv.name, "owner": sv.owner, "view_blob": sv.view_blob}

    def get(self, db: Session, sv_id: int) -> Dict[str, Any] | None:
        sv = db.query(SavedView).filter(SavedView.id == sv_id).first()
        if not sv:
            return None
        return {"id": sv.id, "name": sv.name, "owner": sv.owner, "view_blob": sv.view_blob}

    def delete(self, db: Session, sv_id: int) -> bool:
        sv = db.query(SavedView).filter(SavedView.id == sv_id).first()
        if not sv:
            return False
        db.delete(sv)
        db.commit()
        return True

    def list(self, db: Session):
        rows = db.query(SavedView).all()
        return [{"id": r.id, "name": r.name, "owner": r.owner} for r in rows]
