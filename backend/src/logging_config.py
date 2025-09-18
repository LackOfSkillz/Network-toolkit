"""
Simple logging configuration for the application.

This module provides a tiny `configure_logging()` helper used by `main.py`
to ensure a consistent stdout logging format during development and tests.
Keeping logging configuration small and explicit helps tests capture log
output deterministically.
"""

import logging
import sys


def configure_logging():
    """Configure a simple stdout logger for development and tests.

    This function is idempotent: if handlers are already configured it will
    return immediately which makes it safe to call from tests or multiple
    import paths.
    """
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(logging.INFO)
