from backend.src.services.credential_service import CredentialService


def test_create_and_get_credential_group(db_session):
    svc = CredentialService(db_session)
    cg = svc.create_credential_group("cg-unit", "u", "p", "k")
    assert cg.id is not None
    res = svc.get_credential_group(cg.id)
    assert res["name"] == "cg-unit"
    assert res["username"] == "u"
    assert res["password"] == "p"
    assert res["private_key"] == "k"
