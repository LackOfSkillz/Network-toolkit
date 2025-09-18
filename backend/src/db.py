from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Generator


"""
Simple DB helper for the application.

What this module provides:
- a SQLAlchemy Declarative `Base` that model classes inherit from
- a `configure_database(database_url)` function to create a SQLAlchemy
	engine and session factory (`SessionLocal`)
- a `get_db()` generator dependency used by FastAPI endpoints to obtain
	a scoped SQLAlchemy session.

Design notes and testing guidance:
- We intentionally avoid creating an engine at module import time. Tests
	or higher-level application code should call `configure_database(...)`
	early (for example from `tests/conftest.py`) so the test harness controls
	which database URL and engine are used. This prevents import-time
	capture of engine/session objects which often causes flaky tests with
	SQLite in-memory databases when multiple engines are created.

This module is intentionally minimal and meant for development/test
environments. In production you would typically wire this to a migration
tool (Alembic) and stronger connection/engine configuration.
"""

# Declarative base is safe to create at import time and used by models.
Base = declarative_base()

# Engine and SessionLocal will be configured via configure_database().
# Leaving these as None means other modules don't create DB connections
# until configure_database() is called.
engine = None
SessionLocal = None


def configure_database(database_url: str | None = None):
		"""Create and bind the SQLAlchemy engine and Session factory.

		Provide a database URL (e.g. 'sqlite:///...') or it will be read from
		the DATABASE_URL environment variable. This function is idempotent and
		can be called multiple times (it will rebind engine/SessionLocal).

		Returns the created engine object.
		"""
		global engine, SessionLocal
		url = database_url or os.getenv("DATABASE_URL", "sqlite:///backend/dev.db")
		# SQLite requires a special connect arg when used with multiple threads
		connect_args = {"check_same_thread": False} if url.startswith('sqlite') else {}
		engine = create_engine(url, connect_args=connect_args)
		SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
		return engine


def get_db() -> Generator:
		"""Yield a SQLAlchemy session for use in a request or a test.

		This generator is designed to be used as a FastAPI dependency. It
		lazily configures the DB from environment if nothing has been set up
		(for backward compatibility), then yields a SessionLocal instance and
		closes it after use.
		"""
		if SessionLocal is None:
				# attempt to configure from env automatically for backward compatibility
				configure_database()
		db = SessionLocal()
		try:
				yield db
		finally:
				db.close()


# Note: do not configure the engine at import time. Callers should call
# configure_database(...) explicitly. This keeps import-time side-effects
# minimal and lets tests configure the DB before other modules are imported.
