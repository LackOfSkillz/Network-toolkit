# Network Toolkit Constitution

## Core Principles

### I. Defined Tech Stack
All code must use the approved technologies: Python 3.11+ (FastAPI, SQLAlchemy) for the backend, and React.js for the frontend. This ensures consistency and simplifies maintenance.

### II. Test-Driven Development (TDD)
All new functionality must be accompanied by tests *before* implementation. This includes contract tests for APIs and unit/integration tests for business logic. This is non-negotiable for ensuring quality.

### III. Modular Architecture
The backend and frontend must remain clearly separated. Backend services should be modular and single-purpose (e.g., an `AuthService`, a `ConfigService`). This makes the system easier to understand, test, and scale.

### IV. API-First Design
The backend API (defined in `contracts/`) is the source of truth. The frontend should only interact with the backend through this defined contract. No direct database access from the frontend is permitted.

### V. Consistent Styling
All Python code must follow PEP 8. All frontend code should be formatted with Prettier. This ensures readability and reduces cognitive overhead.

## Security Requirements

- All endpoints must be authenticated by default, unless explicitly marked as public.
- All sensitive data must be encrypted in transit (TLS) and at rest.

## Development Workflow

- We will adopt a GitFlow-like branching model (`feature/`, `develop`, `main`).
- All new work must be done in a feature branch and submitted as a pull request to `develop`.
- Every pull request must be reviewed and approved by at least one other developer before being merged.

## Governance

- This constitution is the source of truth for all development practices.
- Amendments to the constitution require a pull request and approval from the project lead.

**Version**: 1.0.0 | **Ratified**: 2025-09-17 | **Last Amended**: 2025-09-17
