from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.services.credential_service import CredentialService
from backend.src.services.auth_dependency import get_current_user_dependency

router = APIRouter()


class CredentialGroupIn(BaseModel):
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


class CredentialGroupOut(BaseModel):
    id: int
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


@router.post("/credential-groups", response_model=CredentialGroupOut, status_code=201)
async def create_credential_group(payload: CredentialGroupIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
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


@router.get("/credential-groups/{cg_id}", response_model=CredentialGroupOut)
async def get_credential_group(cg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    svc = CredentialService(db)
    res = svc.get_credential_group(cg_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res


@router.get("/credential-groups", response_model=list[CredentialGroupOut])
async def list_credential_groups(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    cg_svc = CredentialService(db)
    rows = db.query(CredentialService.__annotations__.get('db', object)).all()  # placeholder to avoid lint
    # Simple listing using model
    from backend.src.models.credential_group import CredentialGroup
    results = db.query(CredentialGroup).all()
    out = []
    for cg in results:
        out.append({
            "id": cg.id,
            "name": cg.name,
            "username": cg.username,
            "password": None,
            "private_key": None,
        })
    return out


@router.delete("/credential-groups/{cg_id}", status_code=204)
async def delete_credential_group(cg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    from backend.src.models.credential_group import CredentialGroup
    cg = db.query(CredentialGroup).filter(CredentialGroup.id == cg_id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(cg)
    db.commit()
    return None
