from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.services.credential_service import CredentialService
from backend.src.services.auth_dependency import get_current_user_dependency

router = APIRouter()


class CredentialIn(BaseModel):
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


class CredentialOut(BaseModel):
    id: int
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


@router.post("/credentials", response_model=CredentialOut, status_code=201)
async def create_credential(payload: CredentialIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = CredentialService(db)
    cg = svc.create_credential_group(payload.name, payload.username, payload.password, payload.private_key)
    if not cg:
        raise HTTPException(status_code=500, detail="Could not create credential group")
    return {
        "id": cg.id,
        "name": cg.name,
        "username": cg.username,
        "password": payload.password,
        "private_key": payload.private_key,
    }


@router.get("/credentials/{cg_id}", response_model=CredentialOut)
async def get_credential(cg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = CredentialService(db)
    res = svc.get_credential_group(cg_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res
