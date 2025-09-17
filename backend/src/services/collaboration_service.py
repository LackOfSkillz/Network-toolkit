class CollaborationService:
    def start_session(self, user):
        return {"session": "dummy", "user": getattr(user, "username", "anonymous")}
