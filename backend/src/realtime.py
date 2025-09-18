from typing import Dict, Any
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

# Try to import python-socketio; if unavailable, provide a fallback ASGI app so
# tests and environments without the optional dependency don't fail at import.
try:
    import socketio  # type: ignore

    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
    # ASGI app for mounting under FastAPI
    socket_app = socketio.ASGIApp(sio)

    # Simple in-memory room tracking (prototype only)
    connected_clients: Dict[str, Dict[str, Any]] = {}


    @sio.event
    async def connect(sid, environ, auth):
        logger.info(f"Socket connected: {sid}, auth={auth}")
        connected_clients[sid] = {"auth": auth}


    @sio.event
    async def disconnect(sid):
        logger.info(f"Socket disconnected: {sid}")
        connected_clients.pop(sid, None)


    @sio.on("join_room")
    async def handle_join(sid, data):
        room = data.get("room")
        if not room:
            return
        logger.info(f"{sid} joining room {room}")
        await sio.save_session(sid, {"room": room})
        await sio.enter_room(sid, room)
        await sio.emit("presence", {"sid": sid, "action": "joined"}, room=room)


    @sio.on("leave_room")
    async def handle_leave(sid, data):
        room = data.get("room")
        if not room:
            return
        logger.info(f"{sid} leaving room {room}")
        await sio.leave_room(sid, room)
        await sio.emit("presence", {"sid": sid, "action": "left"}, room=room)


    @sio.on("widget_update")
    async def handle_widget_update(sid, data):
        # Broadcast widget update to everyone in the room
        room = data.get("room")
        widget = data.get("widget")
        logger.info(f"widget_update from {sid} in {room}: {widget}")
        if room:
            await sio.emit("widget_updated", {"widget": widget, "from": sid}, room=room)


    # Optional helper to integrate with FastAPI request lifecycle
    async def attach_request_context(request: Request):
        # Inspect headers for auth token if needed
        token = request.headers.get("authorization")
        return {"auth_header": token}

except Exception:
    # socketio is optional at import-time for environments where deps are not installed.
    logger.warning("python-socketio not installed; realtime features disabled")

    async def socket_app(scope, receive, send):
        """A minimal ASGI app used when python-socketio is not available.

        Returns 501 JSON for HTTP requests and closes websocket connections.
        """
        if scope["type"] == "http":
            from starlette.responses import JSONResponse

            response = JSONResponse({"error": "realtime_not_enabled"}, status_code=501)
            await response(scope, receive, send)
            return

        if scope["type"] == "websocket":
            # Consume the connect and immediately close
            event = await receive()
            await send({"type": "websocket.close", "code": 1000})
            return

    # Provide no-op attachments for compat
    connected_clients: Dict[str, Dict[str, Any]] = {}

    async def attach_request_context(request: Request):
        return {"auth_header": request.headers.get("authorization")}
