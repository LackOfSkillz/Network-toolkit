from backend.src.services.configuration_service import ConfigurationService
from backend.src.db import SessionLocal


def test_create_and_list_configurations():
    db = SessionLocal()
    try:
        svc = ConfigurationService(db)
        cfg = svc.create_configuration("cfg-test", "desc")
        assert cfg.id is not None
        all_cfgs = svc.list_configurations()
        assert any(c.id == cfg.id for c in all_cfgs)
    finally:
        db.close()
