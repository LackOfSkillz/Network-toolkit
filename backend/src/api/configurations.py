"""
API endpoints for managing network configurations.

This module exposes a small, self-documenting set of HTTP endpoints used by the
frontend to list and create `NetworkConfiguration` objects.

Notes for non-developers:
- Each endpoint receives a database session via dependency injection
  (`get_db`) so it does not need to open or close connections itself.
- The input/output schemas are Pydantic models which describe the shape of
  requests and responses (they are used to validate JSON sent by the client).
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List
from backend.src.services.configuration_service import ConfigurationService
from backend.src.services.auth_dependency import get_current_user, get_current_user_dependency
from backend.src.db import get_db
from sqlalchemy.orm import Session

router = APIRouter()


class ConfigurationIn(BaseModel):
    """Shape of data expected when creating a configuration.

    Fields:
    - name: user-visible name for the configuration
    - description: optional human readable note
    """

    name: str
    description: str | None = None


class ConfigurationOut(BaseModel):
    """Shape of data returned to clients for a configuration object."""

    id: int
    name: str
    description: str | None = None


@router.get("/configurations", response_model=List[ConfigurationOut])
async def list_configurations(db: Session = Depends(get_db)):
    """Return all saved configurations.

    The `db` parameter is provided automatically by FastAPI using the
    `get_db` generator; the function itself delegates to the service layer.
    """
    svc = ConfigurationService(db)
    return svc.list_configurations()


@router.post("/configurations", response_model=ConfigurationOut, status_code=201)
async def create_configuration(
    payload: ConfigurationIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_dependency),
):
    """Create a new configuration.

    The `user` dependency enforces authentication. The endpoint returns the
    created object or raises a 500 error if creation fails.
    """
    svc = ConfigurationService(db)

    cfg = svc.create_configuration(payload.name, payload.description)
    if not cfg:
        raise HTTPException(status_code=500, detail="Could not create configuration")
    return cfg
