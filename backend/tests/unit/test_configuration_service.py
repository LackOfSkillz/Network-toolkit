from backend.src.services.configuration_service import ConfigurationService


def test_create_and_list_configurations(db_session):
    svc = ConfigurationService(db_session)
    cfg = svc.create_configuration("cfg-test", "desc")
    assert cfg.id is not None
    all_cfgs = svc.list_configurations()
    assert any(c.id == cfg.id for c in all_cfgs)
