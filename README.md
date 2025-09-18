# Network-Toolkit

Network-Toolkit is a web-based toolkit for network mapping, troubleshooting, policy simulation and compliance checks. It provides a FastAPI backend with services for rule evaluation, drift detection, troubleshooting suggestions, and a Vite+React frontend with dashboard widgets (charts and tables).

## Features
- Network topology saved views and dashboard widgets (chart & table)
- Firewall rule simulation (what-if)
- Deterministic rule engine with priority & specificity resolution
- Drift detection between desired and observed configs
- Troubleshooting suggestions and remediation patches
- Custom compliance policy evaluation and remediation guidance
- Authentication (JWT), user management and RBAC (basic)

## How to run (development)

Backend

1. Create a Python virtual environment and activate it (example):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run tests (important: tests configure the DB early):

```bash
# Run from repository root so tests can import the package and configure the DB
PYTHONPATH=$(pwd) .venv/bin/python -m pytest -q
```

4. Run the backend (development):

```bash
cd backend
uvicorn backend.src.main:app --reload
```

Frontend

1. Install Node dependencies in the `frontend` folder:

```bash
cd frontend
npm install
```

2. Run the dev server:

```bash
npm run dev
```

3. Run frontend tests (Vitest):

```bash
cd frontend
npm test
```

4. Open the app in the browser (Vite will print the local URL).


## Database initialization and tests (important)

To make tests reliable and avoid SQLite in-memory pitfalls, the backend uses a programmatic database initialization pattern:

- `backend/src/db.py` exposes two helpers:
	- `configure_database(database_url: str | None = None)` — create the SQLAlchemy Engine and Session factory. Tests (or the main entry) should call this early to control which database is used.
	- `get_db()` — a FastAPI dependency generator that yields a SQLAlchemy session. It will lazily configure the DB if needed, but tests should configure the DB explicitly before importing modules that would otherwise create engines/sessions.

Why this matters for tests
- In-memory SQLite databases (sqlite:///:memory:) are connection-local and do not persist across multiple Engine instances. Test collection and fixtures often create multiple connections/engines which makes in-memory DBs fragile. The test harness therefore prefers a temporary file-backed SQLite database (stored in a temp file) when `DATABASE_URL` is not explicitly provided. This keeps test state persistent across engine instances while remaining isolated per test session.

Recommended test pattern (in `tests/conftest.py`)

- Create an engine early by calling `configure_database(temp_sqlite_url)` before other modules import `get_db`.
- Create the schema once with `Base.metadata.create_all(bind=engine)` and tear down the file after tests.


## Optional features and runtime notes

- Realtime (Socket.IO): The backend exposes an optional realtime ASGI app. The code attempts to import `python-socketio` and, if missing, provides a small fallback ASGI app that returns 501 for realtime endpoints. This allows tests and environments without the optional dependency to import the module safely.

- Crypto/Secrets: The prototype includes a small Fernet-based crypto helper to encrypt secrets at rest. It attempts to load a key from the environment or a file and will generate a new key if none is provided (development-only behavior). Treat this as a demo convenience rather than production-ready key management.

- Deprecation warnings: You may see warnings from SQLAlchemy (declarative_base migration) and FastAPI (`on_event` deprecation) during test runs — these are non-fatal but worth addressing in a future cleanup.


## Troubleshooting

- If you see SQLAlchemy table mapping errors during tests, ensure the test-runner configured the DB early (see the test pattern above). Running tests from repository root with `PYTHONPATH=$(pwd)` usually ensures modules import correctly.
- If frontend unit tests fail with network/XHR messages, the tests run in a jsdom environment and may expect mocked backend endpoints; run the full dev server for end-to-end testing.


## Contributing

Contributions welcome. Please open issues / PRs and follow the repository coding style.

If anything in this document is out-of-date, please open an issue with the corrections and a short patch suggestion.

## As-built Instruction Manual

This section documents the application as-built: its major UI screens, backend API surface, data model highlights, operational steps, environment variables, and common maintenance tasks. It's written for operators and new developers to get productive quickly.

Overview
- The app is a single-page React frontend (Vite) served separately in development. The backend is a FastAPI app exposing REST endpoints and optional realtime (Socket.IO) hooks.

UI / Pages (what users will see)
- Dashboard: configurable widgets showing charts and tables. Widgets display network metrics and saved views.
- Topology / Network Map: interactive map with device nodes, links, and context menus (right-click) for device actions and saved view management.
- What-If / Policy Simulation: form-based UI to craft firewall rules and run deterministic simulations showing allowed/denied traffic and affected rules.
- Drift Detection: page to compare desired configuration vs observed state and view detected drifts with suggested remediations.
- Compliance Policies: UI to create custom compliance policies, evaluate devices, and apply automated remediation suggestions.
- Settings: credential groups management, integrations, and user settings. Admins can manage users and RBAC roles.

Backend API (high-level)
- Auth: /api/auth/login (POST) — obtain JWT token; /api/auth/refresh (POST) — refresh tokens.
- Devices & Topology: /api/devices (GET/POST/PUT/DELETE), /api/topology/views (GET/POST) — saved views management.
- What-If Simulation: /api/whatif/run (POST) — run a simulation; returns decision trace and impacted rules.
- Drift & Troubleshooting: /api/drift/scan (POST) — start drift scan; /api/troubleshoot/suggest (POST) — get suggestions.
- Compliance Policies: /api/compliance/policies (GET/POST/PUT/DELETE), /api/compliance/evaluate (POST) — evaluate devices or configs.
- Dashboard Widgets: /api/widgets (GET/POST/PUT/DELETE) — save and load widget configurations.

Data Model Highlights
- The system persists canonical network device records, configurations, saved topology views, widget states, and user credentials (encrypted at rest using the optional Fernet helper). Key tables include:
  - devices
  - configurations
  - saved_views
  - widget_configs
  - users
  - credential_groups

Operational notes
- Database: use the programmatic init pattern. For production, set DATABASE_URL to a real RDS/Postgres/managed DB. For local development use the default SQLite file or a local Postgres. For tests, prefer a temporary file-backed SQLite DB to avoid in-memory sqlite issues.
- Realtime: socket.io is optional. If the dependency is absent the realtime module will expose a 501 fallback for realtime endpoints. Install python-socketio and configure the ASGI app if you need realtime in production.
- Secrets: The repo contains a demo Fernet wrapper used to encrypt secrets. Replace this with a proper KMS/HSM or cloud-secret manager in production.

Environment variables (common)
- DATABASE_URL — SQLAlchemy database URL. If unset, the app may default to sqlite:///./network_toolkit.db for development.
- SECRET_KEY — app secret used for JWT signing. Provide a strong value in production.
- FERNET_KEY — optional, base64 key for the Fernet helper to encrypt secrets.
- PORT — port for the backend server (if running via uvicorn directly).

Maintenance & Troubleshooting
- Running tests: run backend tests from repository root with PYTHONPATH=$(pwd) so tests can configure DB before imports. Example shown in the How to run section above.
- Migrations: the project currently uses SQLAlchemy metadata-based schema creation. If you add migrations, use Alembic and configure its env to read the same programmatic DB config.
- Linting and types: run the configured linters (ESLint for frontend, ruff/mypy or project's chosen tools for backend) regularly. See the pending todo in the project for running linters across the repo.

Where to look for more details
- backend/src — backend package (FastAPI app, services, models, API routers).
- frontend/src — React app sources (components, pages, utils).
- specs/001-1-web-based — project specs and API contracts (OpenAPI definition under contracts/openapi.yaml).

If anything in this document is out-of-date, please open an issue with the corrections and a short patch suggestion.
