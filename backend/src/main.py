from fastapi import FastAPI
from backend.src.api import auth as auth_api
from backend.src.api import configurations as cfg_api
from backend.src.api import credentials as cred_api
from backend.src.db import Base, engine
from backend.src.logging_config import configure_logging
from backend.src.middleware.logging_middleware import RequestLoggingMiddleware
# Ensure all models are imported so mappers are registered
import backend.src.models  # noqa: F401

app = FastAPI(title="Network Toolkit API - Prototype")

# Configure logging
configure_logging()


@app.on_event("startup")
def on_startup():
    # Create DB tables for prototype (use migrations in production)
    # Ensure all models are imported so mappers are registered, then create tables.
    import backend.src.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Also create tables at import time to support test runners that don't
# reliably trigger the startup event for every execution path.
import backend.src.models  # noqa: F401
Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(auth_api.router)
app.include_router(cfg_api.router)
app.include_router(cred_api.router)
# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)
from backend.src.api import what_if as what_if_api
from backend.src.api import drift_detection as drift_detection_api
from backend.src.api import custom_compliance_policies as custom_compliance_api
from backend.src.api import saved_views as saved_views_api
from backend.src.api import dashboard_widgets as dashboard_widgets_api

app.include_router(what_if_api.router)
app.include_router(drift_detection_api.router)
app.include_router(custom_compliance_api.router)
app.include_router(saved_views_api.router)
app.include_router(dashboard_widgets_api.router)
