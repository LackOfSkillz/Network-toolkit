from fastapi import FastAPI

# main.py wires together the FastAPI application for the project. It:
# - imports model modules so SQLAlchemy mappers are registered
# - configures logging
# - ensures the database is configured on startup (tests may configure it earlier)
# - mounts routers and optional realtime endpoints

import backend.src.models  # noqa: F401  (ensure models are imported)
from backend.src.api import auth as auth_api
from backend.src.api import configurations as cfg_api
from backend.src.api import credentials as cred_api
from backend.src.db import Base, engine, configure_database
from backend.src.logging_config import configure_logging
from backend.src.middleware.logging_middleware import RequestLoggingMiddleware
from backend.src.realtime import socket_app
from backend.src.api.errors import api_error_handler, generic_exception_handler, APIError
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status


app = FastAPI(title="Network Toolkit API - Prototype")


# Configure logging early so middleware and handlers use the same format.
configure_logging()


@app.on_event("startup")
def on_startup():
    """Startup event handler.

    Behavior:
    - Ensure the DB engine is configured (tests often configure the DB in
      `conftest.py` so this is a no-op there).
    - Create tables using `Base.metadata.create_all` for development/test
      convenience. In production you should run migrations (Alembic) instead.
    """
    # Ensure models are imported (no-op if already imported)
    import backend.src.models  # noqa: F401

    # Ensure engine is configured (tests may have already configured it).
    if engine is None:
        configure_database()
    # Create tables for runtime (in tests the conftest may already have
    # created the schema, so this is safe/no-op in that case).
    Base.metadata.create_all(bind=engine)



@app.get("/health")
async def health():
    """Health endpoint used by CI or humans to check the service status."""
    return {"status": "ok"}


# Include routers for the various API components. Each router defines
# endpoints grouped by functionality (auth, configurations, credentials, etc.).
app.include_router(auth_api.router)
app.include_router(cfg_api.router)
app.include_router(cred_api.router)

# Add request-logging middleware so every incoming request is logged.
app.add_middleware(RequestLoggingMiddleware)
from backend.src.api import what_if as what_if_api
from backend.src.api import drift_detection as drift_detection_api
from backend.src.api import custom_compliance_policies as custom_compliance_api
from backend.src.api import saved_views as saved_views_api
from backend.src.api import dashboard_widgets as dashboard_widgets_api
from backend.src.api import credential_groups as credential_groups_api
from backend.src.api import lldp as lldp_api

app.include_router(what_if_api.router)
app.include_router(drift_detection_api.router)
app.include_router(custom_compliance_api.router)
app.include_router(saved_views_api.router)
app.include_router(dashboard_widgets_api.router)
app.include_router(credential_groups_api.router)
app.include_router(lldp_api.router)


# Mount the realtime Socket.IO application at /socket.io so the frontend
# can connect for updates. The socket_app is a small ASGI app created in
# backend.src.realtime.
app.mount("/socket.io", socket_app)


# Add API exception handlers so domain-specific exceptions are serialized
# to friendly JSON responses.
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)
