from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# NOTE: For prototype only. Replace secret management with env/KMS in production.
SECRET_KEY = "dev-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserObj:
    def __init__(self, username: str, password_hash: str, role: str = "user"):
        self.username = username
        self.password_hash = password_hash
        self.role = role


class AuthService:
    def __init__(self):
        # In-memory demo user store for prototype
        self._users = {
            "admin": UserObj("admin", pwd_context.hash("admin"), role="admin")
        }

    def authenticate_user(self, username: str, password: str) -> Optional[UserObj]:
        user = self._users.get(username)
        if not user:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user

    def get_user(self, username: str) -> Optional[UserObj]:
        """Return the user object for a username or None."""
        return self._users.get(username)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
