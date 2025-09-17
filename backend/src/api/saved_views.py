from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.services.saved_view_service import SavedViewService
from backend.src.services.auth_dependency import get_current_user_dependency
from backend.src.db import get_db

router = APIRouter()


class SavedViewIn(BaseModel):
    name: str
    view_blob: dict


@router.post("/saved-views", status_code=201)
def create_saved_view(payload: SavedViewIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = SavedViewService()
    res = svc.create(db, payload.name, getattr(user, "username", "anonymous"), payload.view_blob)
    return res


@router.get("/saved-views")
def list_saved_views(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = SavedViewService()
    return svc.list(db)


@router.get("/saved-views/{sv_id}")
def get_saved_view(sv_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = SavedViewService()
    res = svc.get(db, sv_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res


@router.delete("/saved-views/{sv_id}")
def delete_saved_view(sv_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = SavedViewService()
    ok = svc.delete(db, sv_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}


@router.put("/saved-views/{sv_id}")
def update_saved_view(sv_id: int, payload: SavedViewIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = SavedViewService()
    res = svc.update(db, sv_id, name=payload.name, view_blob=payload.view_blob)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res
