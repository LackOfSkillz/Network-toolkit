"""Credential groups API

Tiny REST endpoints to create, list, retrieve and delete credential
groups. This module is intentionally thin: it delegates validation and
storage to :class:`backend.src.services.credential_service.CredentialService`.

Goals of these doc edits:
- Make the module understandable to non-developers.
- Keep changes non-functional.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.services.credential_service import CredentialService
from backend.src.services.auth_dependency import get_current_user_dependency

router = APIRouter()


class CredentialGroupIn(BaseModel):
    """Input shape expected when creating a credential group."""
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


class CredentialGroupOut(BaseModel):
    """Output shape returned to clients for credential group objects."""
    id: int
    name: str
    username: str | None = None
    password: str | None = None
    private_key: str | None = None


@router.post("/credential-groups", response_model=CredentialGroupOut, status_code=201)
async def create_credential_group(payload: CredentialGroupIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    """Create a credential group and return the persisted row.

    Any validation or encryption is handled by the service layer. The
    endpoint returns 500 if creation fails for an unexpected reason.
    """
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
    """Fetch a single credential group by numeric id."""
    svc = CredentialService(db)
    res = svc.get_credential_group(cg_id)
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res


@router.get("/credential-groups", response_model=list[CredentialGroupOut])
async def list_credential_groups(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    """Return a list of credential groups.

    The endpoint intentionally omits returning secrets in the list
    response; clients must fetch individual groups to retrieve secret
    values (if permitted).
    """
    # Use the ORM model directly for the list operation.
    from backend.src.models import CredentialGroup
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
    """Delete a credential group by id.

    Returns 404 when the group does not exist. Deletion is permanent.
    """
    from backend.src.models import CredentialGroup
    cg = db.query(CredentialGroup).filter(CredentialGroup.id == cg_id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(cg)
    db.commit()
    return None
