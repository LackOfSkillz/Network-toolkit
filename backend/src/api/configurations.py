from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List
from backend.src.services.configuration_service import ConfigurationService
from backend.src.services.auth_dependency import get_current_user, get_current_user_dependency
from backend.src.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()


class ConfigurationIn(BaseModel):
    name: str
    description: str | None = None


class ConfigurationOut(BaseModel):
    id: int
    name: str
    description: str | None = None


@router.get("/configurations", response_model=List[ConfigurationOut])
async def list_configurations(db: Session = Depends(get_db)):
    svc = ConfigurationService(db)
    return svc.list_configurations()


@router.post("/configurations", response_model=ConfigurationOut, status_code=201)
async def create_configuration(
    payload: ConfigurationIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_dependency),
):
    svc = ConfigurationService(db)

    cfg = svc.create_configuration(payload.name, payload.description)
    if not cfg:
        raise HTTPException(status_code=500, detail="Could not create configuration")
    return cfg
