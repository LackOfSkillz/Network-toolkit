"""
Authentication endpoints.

This module implements a tiny login endpoint used by the UI to exchange
username/password for a signed JWT access token. The implementation is
intentionally minimal for a prototype and delegates to `AuthService` for the
real work.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.src.services.auth_service import AuthService

router = APIRouter()


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(payload: LoginPayload, auth: AuthService = Depends(AuthService)):
    """Authenticate the provided credentials and return a JWT token on success."""
    user = auth.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({"sub": user.username})
    return {"token": token}
