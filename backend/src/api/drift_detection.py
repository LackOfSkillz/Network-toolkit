"""
Simple drift detection endpoint.

This route accepts a pair of dictionaries: the `desired` configuration and the
`observed` (actual) configuration. It delegates to the `DriftDetectionService`
which returns a human-readable report describing differences and potential
fixes.

Inputs (JSON):
- desired: dict — the intended configuration state
- observed: dict — the current observed state

Output (JSON):
- report: dict — a structured drift report produced by the service

Authentication: the endpoint uses the standard `get_current_user_dependency`
so callers must be authenticated if the app enforces auth.
"""

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
    """Accepts a payload and returns a drift report.

    Note: The endpoint currently runs synchronously in-process. For very
    large configurations consider offloading to a background worker.
    """
    svc = DriftDetectionService()
    report = svc.compare(payload.desired, payload.observed)
    return {"report": report}
