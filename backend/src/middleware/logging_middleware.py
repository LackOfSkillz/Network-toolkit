
"""
Request logging middleware for HTTP requests.

This ASGI middleware emits a single-line log for each HTTP request when the
response starts. It records the HTTP method, path, status code and elapsed
time in milliseconds. The middleware purposefully inspects only the
`http.response.start` event so it doesn't buffer response bodies or interfere
with streaming responses.

Why this is useful for new contributors
- Small, self-contained, and easy to reason about.
- Uses standard ASGI primitives so it works with any ASGI app (FastAPI,
    Starlette, etc.).
- Provides a simple hook for tests or hosting environments to capture request
    timings by configuring the `logging` module used here.
"""

import time
import logging
from starlette.types import ASGIApp, Receive, Scope, Send


logger = logging.getLogger("network-toolkit.middleware")


class RequestLoggingMiddleware:
    """ASGI middleware that logs a concise request line when the response starts.

    It intentionally does not alter the request/response flow and forwards all
    events unchanged. Use this in front of your app to get simple timing
    metrics for incoming requests.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Only log normal HTTP requests; leave websockets and background
        # scopes untouched so other components can handle them.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        method = scope.get("method")
        path = scope.get("path")

        async def send_wrapper(message):
            # The http.response.start event contains the status code. When we
            # see it, compute elapsed time and emit a single log entry. Other
            # events (body chunks, etc.) are forwarded unchanged.
            if message["type"] == "http.response.start":
                status = message["status"]
                elapsed = (time.time() - start) * 1000
                logger.info("%s %s -> %s (%.2fms)", method, path, status, elapsed)
            await send(message)

        await self.app(scope, receive, send_wrapper)
