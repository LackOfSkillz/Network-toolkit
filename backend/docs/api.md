# API documentation (Prototype)

This file summarizes the backend API endpoints available in the prototype.

Base URL: `/`

Health
- GET `/health`
  - Response: `{ "status": "ok" }`

Authentication
- POST `/auth/login`
  - Payload: `{ "username": "admin", "password": "admin" }`
  - Response: `{ "token": "<jwt>" }`
  - Notes: Prototype uses an in-memory demo user (admin/admin) and JWT.

Configurations
- GET `/configurations`
  - Response: list of configuration objects.
- POST `/configurations`
  - Auth: Requires `Authorization: Bearer <token>` header
  - Payload: `{ "name": "cfg1", "description": "..." }`
  - Response: created configuration object

Credentials (encrypted at rest)
- POST `/credentials`
  - Auth: Requires `Authorization: Bearer <token>` header
  - Payload: `{ "name": "cg1", "username": "u1", "password": "p1", "private_key": "..." }`
  - Response: created credential metadata (note: prototype returns plaintext in response)
- GET `/credentials/{id}`
  - Auth: Requires `Authorization: Bearer <token>` header
  - Response: credential object with decrypted `password` and `private_key` (prototype behavior)

Notes & Security
- In production:
  - Replace in-memory auth with persistent users and secure password storage.
  - Use KMS for key management; do not persist keys in repo or unencrypted files.
  - Limit endpoints that return decrypted secrets and audit access.

Scripts
- `backend/scripts/create_db.py` — create sqlite DB tables (prototype)
- `backend/scripts/rotate_credentials.py` — re-encrypt credential records with a new base64 key (prototype)

Testing
- Contract and integration tests live under `backend/tests/contract` and `backend/tests/integration`.
- Unit tests under `backend/tests/unit`.

