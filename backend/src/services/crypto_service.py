"""
Lightweight crypto helpers for encrypting credential material.

This module manages a Fernet key and exposes convenience functions to
encrypt/decrypt bytes and text. Key selection order (highest to lowest):
1) environment variable `CRED_KEY` (base64 or raw),
2) key file at `CRED_KEY_PATH`,
3) generate a new key and try to persist it to disk.

Important notes for non-developers:
- This implementation is intended for development and tests only. In
  production you should use a secure key management system (KMS) and never
  store persistent keys in the repo or writable project directories.
"""

from cryptography.fernet import Fernet
import os
import base64


# For prototype only: prioritize explicit key via env, then file, then generate.
# In production use KMS and avoid persistent keys on disk.
KEY_ENV = os.getenv("CRED_KEY")
KEY_PATH = os.getenv("CRED_KEY_PATH", "backend/.cred_key")


def _load_key_from_file(path: str) -> bytes | None:
    try:
        if os.path.exists(path):
            return open(path, "rb").read()
    except Exception:
        return None
    return None


def _ensure_key() -> bytes:
    # Highest precedence: KEY_ENV (base64 or raw), then file, then generate new key and try to persist.
    if KEY_ENV:
        # Accept either a base64-encoded key or raw bytes string
        try:
            return base64.urlsafe_b64decode(KEY_ENV)
        except Exception:
            return KEY_ENV.encode()

    file_key = _load_key_from_file(KEY_PATH)
    if file_key:
        return file_key

    key = Fernet.generate_key()
    try:
        open(KEY_PATH, "wb").write(key)
    except Exception:
        # best-effort only — don't fail startup if we can't persist the key
        pass
    return key


# Module-level Fernet instance for the active key
_KEY = _ensure_key()
fernet = Fernet(_KEY)


def current_key() -> bytes:
    """Return the active key bytes used by the service."""
    return _KEY


def make_fernet_from_key(key_bytes: bytes) -> Fernet:
    return Fernet(key_bytes)


def encrypt_bytes_with_fernet(data: bytes, f: Fernet) -> bytes:
    return f.encrypt(data)


def decrypt_bytes_with_fernet(token: bytes, f: Fernet) -> bytes:
    return f.decrypt(token)


def encrypt_text_with_key(text: str, key_bytes: bytes) -> str:
    f = make_fernet_from_key(key_bytes)
    return encrypt_bytes_with_fernet(text.encode(), f).decode()


def decrypt_text_with_key(token_str: str, key_bytes: bytes) -> str:
    f = make_fernet_from_key(key_bytes)
    return decrypt_bytes_with_fernet(token_str.encode(), f).decode()


def encrypt_bytes(data: bytes) -> bytes:
    return fernet.encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    return fernet.decrypt(token)


def encrypt_text(text: str) -> str:
    return encrypt_bytes(text.encode()).decode()


def decrypt_text(token_str: str) -> str:
    return decrypt_bytes(token_str.encode()).decode()
