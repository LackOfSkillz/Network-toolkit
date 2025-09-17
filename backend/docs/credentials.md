# Credential storage and encryption strategy

This document describes the prototype credential storage strategy used in this repository and guidance for production.

Design goals
- Ensure sensitive fields (passwords, private keys) are encrypted at rest.
- Allow key rotation and operational simplicity for the prototype.
- Be explicit about production recommendations (KMS, access controls).

Prototype implementation
- A Fernet symmetric key is used for encrypting credential fields.
- The key is loaded in the following precedence:
  1. `CRED_KEY` environment variable (base64); highest precedence.
  2. `backend/.cred_key` file on disk.
  3. If neither exists, a new key will be generated and written to `backend/.cred_key` (best-effort).
- The service provides `encrypt_text` and `decrypt_text` helpers and more explicit helpers that accept a specific key for rotation.
- A rotation script is provided at `backend/scripts/rotate_credentials.py` (prototype). It accepts a base64-encoded new key and re-encrypts existing credential groups using the new key.

Production recommendations
- Use a key management system (KMS) such as AWS KMS, Google Cloud KMS, Azure Key Vault, or HashiCorp Vault.
  - Store only minimal metadata in your DB (e.g., a key identifier) and perform encryption/decryption via a KMS-managed key when possible.
  - If using envelope encryption, KMS manages the data-encryption-keys (DEKs) while you store encrypted data locally.
- Restrict access to keys to a small set of services/principals using IAM.
- Implement key rotation using KMS features or a well-tested migration process.
- Audit all accesses and use role-based access control for UI/actions that can reveal secrets.

Migration and rotation notes (prototype)
1. Generate a new Fernet key and convert to base64:
   - Python example: `import base64, cryptography.fernet; print(base64.urlsafe_b64encode(cryptography.fernet.Fernet.generate_key()).decode())`
2. Run the provided rotation script with the new key:
   - `python backend/scripts/rotate_credentials.py <base64-new-key>`
   - This script reads the current key from the environment/file and re-encrypts all credential groups with the new key.
3. Replace the active key in production (set `CRED_KEY` or place new key file) and restart services.

Security caveats
- The rotation script reads plaintext in memory during re-encryption. Run this under strict control and ideally in a maintenance window.
- Do not commit keys to source control. Use secrets management in CI/CD.
- Consider limiting API responses so they don't return decrypted secrets by default.

Contact
- For questions about implementation details or production hardening, consult the security team or the repository maintainers.
