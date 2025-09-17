from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.services.dashboard_widget_service import DashboardWidgetService
from backend.src.services.auth_dependency import get_current_user_dependency
from backend.src.db import get_db

router = APIRouter()


class WidgetIn(BaseModel):
    name: str
    type: str
    config: dict


@router.post("/dashboard/widgets", status_code=201)
def create_widget(payload: WidgetIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DashboardWidgetService()
    try:
        return svc.create(db, payload.name, payload.type, payload.config)
    except ValueError:
        raise HTTPException(status_code=400, detail="unsupported widget type")


@router.get("/dashboard/widgets")
def list_widgets(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DashboardWidgetService()
    return svc.list(db)


@router.get("/dashboard/widgets/{wid}")
def get_widget(wid: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DashboardWidgetService()
    res = svc.get(db, wid)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res


@router.delete("/dashboard/widgets/{wid}")
def delete_widget(wid: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DashboardWidgetService()
    ok = svc.delete(db, wid)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}


@router.put("/dashboard/widgets/{wid}")
def update_widget(wid: int, payload: WidgetIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DashboardWidgetService()
    try:
        res = svc.update(db, wid, name=payload.name, wtype=payload.type, config=payload.config)
    except ValueError:
        raise HTTPException(status_code=400, detail="unsupported widget type")
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res
