from backend.src.services.auth_service import AuthService


def test_authenticate_user_success():
    svc = AuthService()
    user = svc.authenticate_user("admin", "admin")
    assert user is not None
    assert user.username == "admin"


def test_authenticate_user_fail():
    svc = AuthService()
    user = svc.authenticate_user("admin", "wrong")
    assert user is None
