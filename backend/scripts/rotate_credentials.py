"""Rotation script to re-encrypt credential_groups with a new Fernet key.

Usage (prototype):
  python backend/scripts/rotate_credentials.py <base64-key>

Note: In production, use KMS and rotate keys there; this script is for local dev/migration.
"""
import sys
import base64
from backend.src.db import SessionLocal
from backend.src.models.credential_group import CredentialGroup
from backend.src.services.crypto_service import (
    decrypt_text_with_key,
    encrypt_text_with_key,
    current_key,
)


def rotate(new_key_b64: str):
    new_key = base64.urlsafe_b64decode(new_key_b64)
    old_key = current_key()

    db = SessionLocal()
    try:
        groups = db.query(CredentialGroup).all()
        for g in groups:
            if g.password_encrypted:
                plain = decrypt_text_with_key(g.password_encrypted, old_key)
                g.password_encrypted = encrypt_text_with_key(plain, new_key)
            if g.private_key_encrypted:
                plain = decrypt_text_with_key(g.private_key_encrypted, old_key)
                g.private_key_encrypted = encrypt_text_with_key(plain, new_key)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: rotate_credentials.py <base64-new-key>")
        sys.exit(2)
    rotate(sys.argv[1])
    print("Rotation finished (prototype).")
