from backend.src.services.credential_service import CredentialService
from backend.src.db import SessionLocal


def test_create_and_get_credential_group():
    db = SessionLocal()
    try:
        svc = CredentialService(db)
        cg = svc.create_credential_group("cg-unit", "u", "p", "k")
        assert cg.id is not None
        res = svc.get_credential_group(cg.id)
        assert res["name"] == "cg-unit"
        assert res["username"] == "u"
        assert res["password"] == "p"
        assert res["private_key"] == "k"
    finally:
        db.close()
