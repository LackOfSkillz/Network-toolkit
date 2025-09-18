"""
Compatibility shim for tests: ensure imports like `import models.network_device`
resolve to the canonical `backend.src.models.network_device` modules so SQLAlchemy
doesn't see duplicate class objects under different module names.

This is a small, safe test-time helper that aliases sys.modules entries.
"""
import importlib
import sys
from pathlib import Path

CANONICAL_PREFIX = "backend.src.models"

# Attempt to import canonical package
try:
    canonical = importlib.import_module(CANONICAL_PREFIX)
except Exception:
    # If canonical package isn't importable at shim import time, defer.
    canonical = None


def _alias_submodules():
    if canonical is None:
        return
    # ensure the top-level 'models' points at the canonical package object
    sys.modules.setdefault("models", canonical)

    # Inspect the canonical package dir to find submodules
    pkg_path = Path(canonical.__file__).parent
    for p in pkg_path.iterdir():
        if p.is_file() and p.suffix == ".py" and p.stem != "__init__":
            sub = p.stem
            target = f"{CANONICAL_PREFIX}.{sub}"
            try:
                mod = importlib.import_module(target)
                sys.modules.setdefault(f"models.{sub}", mod)
            except Exception:
                # skip modules that aren't importable yet
                continue


# run aliasing eagerly when this shim is imported
_alias_submodules()
