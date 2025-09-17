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

3. Run tests:

```bash
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

3. Open the app in the browser (Vite will print the local URL).


## Notes & Troubleshooting
- The project uses SQLite for local development; `backend/dev.db` is ignored by .gitignore.
- If you encounter SQLAlchemy table mapping errors during tests, make sure tests are run from the repository root with `PYTHONPATH=$(pwd)` so package imports resolve.

## Contributing
Contributions welcome. Please open issues / PRs and follow the repository coding style.
