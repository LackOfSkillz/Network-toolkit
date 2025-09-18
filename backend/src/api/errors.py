from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def api_error_handler(request: Request, exc: APIError):
    logger.exception(f"APIError: {exc.message}")
    return JSONResponse(status_code=exc.status_code, content={
        "error": {
            "message": exc.message,
            "details": exc.details
        }
    })


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={
        "error": {
            "message": "Internal server error",
            "details": {"type": type(exc).__name__}
        }
    })
