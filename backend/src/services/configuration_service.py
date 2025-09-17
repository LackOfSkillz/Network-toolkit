from sqlalchemy.orm import Session
from backend.src.models.network_configuration import NetworkConfiguration


class ConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def list_configurations(self):
        return self.db.query(NetworkConfiguration).all()

    def create_configuration(self, name: str, description: str | None = None):
        cfg = NetworkConfiguration(name=name, description=description)
        self.db.add(cfg)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg
