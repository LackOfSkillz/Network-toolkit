from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.services.drift_detection_service import DriftDetectionService
from backend.src.services.auth_dependency import get_current_user_dependency
from backend.src.db import get_db

router = APIRouter()


class DriftPayload(BaseModel):
    desired: dict
    observed: dict


@router.post("/drift-detection")
async def detect(payload: DriftPayload, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = DriftDetectionService()
    report = svc.compare(payload.desired, payload.observed)
    return {"report": report}
