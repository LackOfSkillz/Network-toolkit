"""
Tiny collaboration helper used by the frontend to start collaborative sessions.

This is a placeholder that should be replaced by a real collaboration
backend (WebSockets/OT/CRDT) in a production system.
"""


class CollaborationService:
    def start_session(self, user):
        return {"session": "dummy", "user": getattr(user, "username", "anonymous")}
