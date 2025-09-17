import os
import sys

# Ensure the database file is created under backend directory
os.environ.setdefault("DATABASE_URL", "sqlite:///backend/dev.db")

# Add repo root to path so backend package imports resolve
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.src.db import engine, Base
# Ensure models are imported so mappers are registered
import backend.src.models  # noqa: F401

if __name__ == "__main__":
    print("Using DATABASE_URL=", os.environ.get("DATABASE_URL"))
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not present).\nDB path may be backend/dev.db relative to repo root.")
