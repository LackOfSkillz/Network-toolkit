"""
Credential management service.

This service provides simple helpers for storing and retrieving credential
groups. Sensitive fields (password, private key) are encrypted before being
stored in the database and are decrypted when read back via
`get_credential_group`.
"""

from sqlalchemy.orm import Session
from backend.src.models import CredentialGroup
from backend.src.services.crypto_service import encrypt_text, decrypt_text


class CredentialService:
    """Small service wrapper for credential group CRUD.

    - `create_credential_group` persists a group, encrypting sensitive fields.
    - `get_credential_group` returns a dictionary with decrypted values for
      use by the API layer; it intentionally returns a plain dict instead of
      the raw ORM object to avoid accidental leakage of encrypted fields.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_credential_group(self, name: str, username: str | None, password: str | None, private_key: str | None):
        cg = CredentialGroup(
            name=name,
            username=username,
            # encrypt_text returns None if input is None; we store encrypted blobs
            password_encrypted=encrypt_text(password) if password else None,
            private_key_encrypted=encrypt_text(private_key) if private_key else None,
        )
        self.db.add(cg)
        self.db.commit()
        self.db.refresh(cg)
        return cg

    def get_credential_group(self, cg_id: int):
        """Return a dict representing the credential group with decrypted secrets.

        Returns None if the group does not exist.
        """
        cg = self.db.query(CredentialGroup).filter(CredentialGroup.id == cg_id).first()
        if not cg:
            return None
        # decrypt on read; service returns a simple dict to the API layer
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
