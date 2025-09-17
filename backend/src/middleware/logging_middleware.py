import time
import logging
from starlette.types import ASGIApp, Receive, Scope, Send


logger = logging.getLogger("network-toolkit.middleware")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        method = scope.get("method")
        path = scope.get("path")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                elapsed = (time.time() - start) * 1000
                logger.info("%s %s -> %s (%.2fms)", method, path, status, elapsed)
            await send(message)

        await self.app(scope, receive, send_wrapper)
