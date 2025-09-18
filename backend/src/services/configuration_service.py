"""
Simple service layer for creating and listing NetworkConfiguration records.

This file contains a tiny class that wraps direct database queries so the
API layer doesn't need to know SQLAlchemy details. It's intentionally small
and synchronous: each method expects to be called with a SQLAlchemy Session
that is already open and will be closed by the caller.
"""

from sqlalchemy.orm import Session
from backend.src.models import NetworkConfiguration


class ConfigurationService:
    """Service providing simple configuration CRUD operations.

    Constructor:
    - db: a SQLAlchemy Session instance (provided by the API dependency)
    """

    def __init__(self, db: Session):
        self.db = db

    def list_configurations(self):
        """Return a list of all NetworkConfiguration rows."""
        return self.db.query(NetworkConfiguration).all()

    def create_configuration(self, name: str, description: str | None = None):
        """Create a NetworkConfiguration row and return it.

        This method performs a commit and refresh so the returned object has an
        `id` assigned by the database.
        """
        cfg = NetworkConfiguration(name=name, description=description)
        self.db.add(cfg)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg
