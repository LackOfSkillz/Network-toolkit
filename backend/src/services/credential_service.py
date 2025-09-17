from sqlalchemy.orm import Session
from backend.src.models.credential_group import CredentialGroup
from backend.src.services.crypto_service import encrypt_text, decrypt_text


class CredentialService:
    def __init__(self, db: Session):
        self.db = db

    def create_credential_group(self, name: str, username: str | None, password: str | None, private_key: str | None):
        cg = CredentialGroup(
            name=name,
            username=username,
            password_encrypted=encrypt_text(password) if password else None,
            private_key_encrypted=encrypt_text(private_key) if private_key else None,
        )
        self.db.add(cg)
        self.db.commit()
        self.db.refresh(cg)
        return cg

    def get_credential_group(self, cg_id: int):
        cg = self.db.query(CredentialGroup).filter(CredentialGroup.id == cg_id).first()
        if not cg:
            return None
        # decrypt on read
        res = {
            "id": cg.id,
            "name": cg.name,
            "username": cg.username,
            "password": decrypt_text(cg.password_encrypted) if cg.password_encrypted else None,
            "private_key": decrypt_text(cg.private_key_encrypted) if cg.private_key_encrypted else None,
            "created_at": cg.created_at,
            "updated_at": cg.updated_at,
        }
        return res
