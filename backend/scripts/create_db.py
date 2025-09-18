import os
import sys

# Ensure the database file is created under backend directory
os.environ.setdefault("DATABASE_URL", "sqlite:///backend/dev.db")

# Add repo root to path so backend package imports resolve
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def main() -> None:
    """Create the database tables.

    This function only mutates sys.path and imports the package when the
    script is executed directly. Importing this module elsewhere will not
    change sys.path or eagerly import the application package.
    """
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from backend.src.db import engine, Base
    # Ensure models are imported so mappers are registered
    import backend.src.models  # noqa: F401

    print("Using DATABASE_URL=", os.environ.get("DATABASE_URL"))
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not present).\nDB path may be backend/dev.db relative to repo root.")


if __name__ == "__main__":
    main()
