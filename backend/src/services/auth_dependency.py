from fastapi import HTTPException, status, Depends, Header
from jose import jwt, JWTError
from backend.src.services.auth_service import AuthService, SECRET_KEY, ALGORITHM


def get_current_user(token: str | None):
    """Validate a JWT token string and return the corresponding user object.

    This helper is intentionally self-contained so callers (including tests) can
    call it directly after extracting the Authorization header.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    auth = AuthService()
    user = auth.get_user(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_user_dependency(authorization: str | None = Header(None)):
    """FastAPI-ready dependency that extracts Bearer token from Authorization header and returns user.

    Example Authorization header: "Bearer <token>". Tests commonly call
    `get_current_user` directly with a token string to avoid HTTP plumbing.
    """
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    return get_current_user(token)
