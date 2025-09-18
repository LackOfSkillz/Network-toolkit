import os
import sys
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path so 'backend' package can be imported
_here = os.path.abspath(os.path.dirname(__file__))
_project_root = os.path.abspath(os.path.join(_here, '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from backend.src import db as dbmod

# Prefer a temporary file-backed SQLite DB for tests unless DATABASE_URL is explicitly set.
# Using a file avoids distinct in-memory databases when multiple engine objects
# are created during test collection / app import. The temp file is removed
# when the test session completes.
_temp_db_file = None
if not os.getenv('DATABASE_URL'):
    tf = tempfile.NamedTemporaryFile(prefix="nt_test_db_", suffix=".db", delete=False)
    _temp_db_file = tf.name
    tf.close()
    os.environ['DATABASE_URL'] = f"sqlite:///{_temp_db_file}"

# Configure the backend DB module to use the test DATABASE_URL before any
# application modules import it. This prevents detached connection issues.
TEST_DB_URL = os.getenv('DATABASE_URL')
test_engine = dbmod.configure_database(TEST_DB_URL)
Base = dbmod.Base

# Import models and create tables immediately so tests that import the FastAPI
# app directly (and don't use the engine fixture) will see the schema.
try:
    import backend.src.models  # noqa: F401
except Exception:
    pass
Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope='session')
def sqlite_url():
    # Use an in-memory sqlite DB for speed unless DATABASE_URL overrides
    env = os.getenv('DATABASE_URL')
    if env:
        return env
    # fallback (should not happen) to in-memory
    return 'sqlite:///:memory:'


@pytest.fixture(scope='session')
def engine(sqlite_url):
    # reuse the engine created at module import so all code sees the same engine
    # Ensure model modules are imported so SQLAlchemy mappers/tables are registered
    try:
        import backend.src.models  # noqa: F401
    except Exception:
        pass
    # Ensure all tables are created in the test database before running tests
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    # remove temp DB file if we created one
    try:
        if _temp_db_file and os.path.exists(_temp_db_file):
            os.unlink(_temp_db_file)
    except Exception:
        pass


@pytest.fixture()
def db_session(engine, monkeypatch):
    """Provide a SQLAlchemy session bound to the test engine.

    Also monkeypatch the application's SessionLocal/engine so code under test
    uses the test database.
    """
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Monkeypatch backend.src.db.SessionLocal and engine so app uses test DB
    import backend.src.db as dbmod
    monkeypatch.setattr(dbmod, 'SessionLocal', TestSession)
    monkeypatch.setattr(dbmod, 'engine', engine)

    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(monkeypatch, db_session):
    """Provide an HTTPX AsyncClient that talks to the FastAPI app with the
    test DB session patched in. Use ASGITransport so no network is required.
    """
    from httpx import AsyncClient, ASGITransport
    from backend.src import main as mainmod

    # ensure app startup creates tables against the test engine (no-op since conftest did)
    transport = ASGITransport(app=mainmod.app)
    async_client = AsyncClient(transport=transport, base_url="http://test")
    yield async_client
    # cleanup
    try:
        import asyncio
        asyncio.get_event_loop().run_until_complete(async_client.aclose())
    except Exception:
        pass
import json
import os
import time
import sys
from pathlib import Path
from typing import Any

from backend.src.db import Base

DEBUG_DIR = Path(os.environ.get("DEBUG_DUMP_DIR", "/tmp/network-toolkit-debug"))
REPO_DUMP_DIR = Path(__file__).resolve().parent / "debug_dumps"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)
REPO_DUMP_DIR.mkdir(parents=True, exist_ok=True)


def _safe_id(obj: Any) -> int | None:
    try:
        return id(obj)
    except Exception:
        return None


def _serialize_mapper(mapper: Any) -> dict:
    cls = mapper.class_
    entry = {"name": cls.__name__, "module": cls.__module__, "id": _safe_id(cls)}
    try:
        rels = []
        for rel in mapper.relationships:
            try:
                rels.append({
                    "key": rel.key,
                    "back_populates": rel.back_populates,
                    "argument": str(getattr(rel, "argument", None)),
                    "target_mapper_class": getattr(rel.mapper, "class_", None).__name__ if getattr(rel, "mapper", None) else None,
                    "target_mapper_module": getattr(rel.mapper, "class_", None).__module__ if getattr(rel, "mapper", None) else None,
                })
            except Exception as e:
                rels.append({"key": getattr(rel, "key", None), "error": str(e)})
        entry["relationships"] = rels
    except Exception:
        entry["relationships_error"] = True
    return entry


def _dump(label: str, nodeid: str | None = None) -> str:
    ts = int(time.time() * 1000)
    safe_label = label.replace("/", "_").replace(" ", "_")
    filename = f"{ts}-{safe_label}"
    if nodeid:
        filename += f"-{nodeid.replace('/', '_').replace(':', '_')}"
    filename += ".json"

    out = {
        "timestamp": ts,
        "label": label,
        "nodeid": nodeid,
        "sys_path": list(sys.path),
        "sys_modules": [k for k in sorted(sys.modules.keys()) if k.startswith("backend.src.models") or k.startswith("models")],
        "mappers": [],
    }
    try:
        for m in Base.registry.mappers:
            out["mappers"].append(_serialize_mapper(m))
    except Exception as e:
        out["mapper_dump_error"] = str(e)

    path_tmp = DEBUG_DIR / filename
    path_repo = REPO_DUMP_DIR / filename
    try:
        with open(path_tmp, "w") as f:
            json.dump(out, f, indent=2)
        with open(path_repo, "w") as f:
            json.dump(out, f, indent=2)
    except Exception as e:
        print("FAILED TO WRITE DEBUG DUMP", e)
        print(json.dumps(out, indent=2))
    else:
        print("WROTE DEBUG DUMP", path_tmp)
    return str(path_tmp)


def pytest_sessionstart(session):
    # Dump state at collection start for debugging import-time mapper registrations
    _dump("session_start")


def pytest_runtest_setup(item):
    # Dump state before each test setup
    _dump("before_test", nodeid=item.nodeid)
import os
import sys
import time
import json
from pathlib import Path

from backend.src.db import Base

# Early aliasing: try to import the canonical backend.src.models package
# at module import time and alias it to top-level 'models' so that any
# subsequent imports like 'import models.network_device' will return the
# same module objects. Doing this early (on import) avoids duplicate
# mappers created during pytest collection.
try:
    import importlib
    canonical = importlib.import_module("backend.src.models")
    sys.modules.setdefault("models", canonical)
    # alias submodules found in the package directory
    pkg_path = Path(canonical.__file__).parent
    for p in pkg_path.iterdir():
        if p.is_file() and p.suffix == ".py" and p.stem != "__init__":
            short = p.stem
            target = f"backend.src.models.{short}"
            try:
                mod = importlib.import_module(target)
                sys.modules.setdefault(f"models.{short}", mod)
            except Exception:
                # skip non-importable modules at this time
                pass
except Exception:
    # non-fatal; conftest will still try to dump state later
    pass


DEBUG_DIR = Path(os.environ.get("DEBUG_DUMP_DIR", "/tmp/network-toolkit-debug"))
REPO_DUMP_DIR = Path(__file__).resolve().parent / "debug_dumps"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)
REPO_DUMP_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:200]


def dump_state(label: str):
    ts = int(time.time() * 1000)
    fname = f"{ts}-{_safe_name(label)}.json"
    path_tmp = DEBUG_DIR / fname
    path_repo = REPO_DUMP_DIR / fname

    data = {
        "label": label,
        "time": ts,
        "sys_path": list(sys.path),
        "sys_modules": [k for k in sorted(sys.modules) if k.startswith("backend.src.models") or k.startswith("models")],
        "mappers": [],
        "classes": [],
    }

    try:
        for m in Base.registry.mappers:
            cls = m.class_
            data["mappers"].append({
                "name": cls.__name__,
                "module": cls.__module__,
                "id": id(cls),
            })
    except Exception as e:
        data["mappers_error"] = str(e)

    # try to include package-level exported classes if present
    try:
        import backend.src.models as pkg_models

        for attr in ("NetworkConfiguration", "NetworkDevice", "FirewallRule"):
            if hasattr(pkg_models, attr):
                c = getattr(pkg_models, attr)
                data["classes"].append({"name": attr, "module": c.__module__, "id": id(c)})
    except Exception:
        pass

    # write both to /tmp and into the repo for easy reading
    with open(path_tmp, "w") as f:
        json.dump(data, f, indent=2)
    with open(path_repo, "w") as f:
        json.dump(data, f, indent=2)
    print("WROTE DEBUG DUMP", path_tmp)


def pytest_sessionstart(session):
    # dump at session start (collection time)
    # If pytest/import hooks caused modules to be importable as both
    # 'models.*' and 'backend.src.models.*', that creates duplicate
    # class objects and SQLAlchemy mappers which break relationship
    # back_populates. Normalize any 'models.' entries to point to the
    # canonical 'backend.src.models' modules before tests run.
    try:
        import importlib

        # perform remapping only if backend.src.models is loaded
        if "backend.src.models" in sys.modules:
            canonical_pkg = sys.modules["backend.src.models"]
            # ensure top-level 'models' points to the same module object
            sys.modules.setdefault("models", canonical_pkg)

            # remap any submodules
            to_remap = [k for k in list(sys.modules) if k.startswith("models.") and not k.startswith("backend.src.models")]
            for name in to_remap:
                short = name.split("models.", 1)[1]
                target = f"backend.src.models.{short}"
                if target in sys.modules:
                    sys.modules[name] = sys.modules[target]
                else:
                    # try importing the canonical module and then assign
                    try:
                        sys.modules[name] = importlib.import_module(target)
                    except Exception:
                        pass
    except Exception:
        pass

    dump_state("session_start")


def pytest_sessionfinish(session, exitstatus):
    # Drop test tables and remove temp DB file if present
    try:
        Base.metadata.drop_all(bind=test_engine)
    except Exception:
        pass
    try:
        if _temp_db_file and os.path.exists(_temp_db_file):
            os.unlink(_temp_db_file)
    except Exception:
        pass


def pytest_runtest_setup(item):
    # dump before each test setup to capture per-test import state
    dump_state(f"before_{_safe_name(item.nodeid)}")
import os
import sys
import time
import json
import pathlib
from typing import Any

from backend.src.db import Base


DEBUG_DIR = os.environ.get("DEBUG_DUMP_DIR", "/tmp/network-toolkit-debug")
pathlib.Path(DEBUG_DIR).mkdir(parents=True, exist_ok=True)


def _serialize_mapper(mapper: Any) -> dict:
    cls = mapper.class_
    entry = {"name": cls.__name__, "module": cls.__module__, "id": id(cls)}
    try:
        rels = []
        for rel in mapper.relationships:
            try:
                rels.append({
                    "key": rel.key,
                    "back_populates": rel.back_populates,
                    "target_arg": str(rel.argument),
                    "remote_side": [str(c) for c in getattr(rel, 'remote_side', [])],
                    "target_mapper_class": getattr(rel.mapper, 'class_', None).__name__ if getattr(rel, 'mapper', None) else None,
                    "target_mapper_module": getattr(rel.mapper, 'class_', None).__module__ if getattr(rel, 'mapper', None) else None,
                })
            except Exception as e:  # pragma: no cover - debug helper
                rels.append({"key": getattr(rel, 'key', None), "error": str(e)})
        entry["relationships"] = rels
    except Exception:
        entry["relationships_error"] = True
    return entry


def dump_state(label: str, nodeid: str | None = None) -> str:
    ts = int(time.time() * 1000)
    safe_label = label.replace("/", "_").replace(" ", "_")
    filename = f"{ts}-{safe_label}"
    if nodeid:
        filename += f"-{nodeid.replace('/', '_').replace(':', '_')}"
    filename += ".json"
    out = {
        "timestamp": ts,
        "label": label,
        "nodeid": nodeid,
        # record sys.path to see what import roots make 'models' resolvable
        "sys_path": list(sys.path),
        "sys_modules": [k for k in sorted(sys.modules.keys()) if k.startswith("backend") or k.startswith('models')],
        "mappers": [],
    }
    try:
        for m in Base.registry.mappers:
            out["mappers"].append(_serialize_mapper(m))
    except Exception as e:  # pragma: no cover - defensive
        out["mapper_dump_error"] = str(e)

    path = os.path.join(DEBUG_DIR, filename)
    try:
        with open(path, "w") as f:
            json.dump(out, f, indent=2)
    except Exception as e:  # pragma: no cover - defensive
        # If writing fails, at least print to stdout so it's visible in pytest logs
        print("FAILED TO WRITE DEBUG DUMP", path, e)
        print(json.dumps(out, indent=2))
    else:
        print("WROTE DEBUG DUMP", path)
    return path


def pytest_sessionstart(session):
    # Called after the Session object has been created and before performing collection.
    # First dump
    dump_state("session_start")

    # Normalize module identity: alias backend.src.models.* -> models.* in sys.modules
    try:
        mapping = {}
        for name, mod in list(sys.modules.items()):
            if name.startswith("backend.src.models."):
                short = name.replace("backend.src.", "")
                mapping[short] = mod
        # Also include package root
        if "backend.src.models" in sys.modules and "models" not in sys.modules:
            mapping["models"] = sys.modules["backend.src.models"]
        for short, mod in mapping.items():
            if short not in sys.modules:
                sys.modules[short] = mod
                print(f"ALIASED MODULE {short} -> {mod.__name__}")
    except Exception as e:  # pragma: no cover - defensive
        print("Error normalizing module aliases:", e)


def pytest_runtest_setup(item):
    # Called before running each test item
    dump_state("before_test", nodeid=item.nodeid)
import json
import os
import time
import sys
from pathlib import Path

from _pytest.config import Config

DEBUG_DIR = os.environ.get("DEBUG_DUMP_DIR", "/tmp/network-toolkit-debug")
Path(DEBUG_DIR).mkdir(parents=True, exist_ok=True)


def _safe_id(obj):
    try:
        return id(obj)
    except Exception:
        return None


def _collect_state(label, nodeid=None):
    ts = int(time.time() * 1000)
    # sanitize nodeid to a safe filename fragment
    safe_node = (nodeid or "session").replace("/", "_").replace(":", "_")
    # replace any characters that are undesirable
    safe_node = "".join([c if c.isalnum() or c in ('_', '-') else '_' for c in safe_node])
    fname = f"{ts}-{label.replace('/', '_')}-{safe_node}.json"
    path = Path(DEBUG_DIR) / fname
    data = {
        "label": label,
        "nodeid": nodeid,
        "timestamp": ts,
        "sys_modules": [],
        "mappers": [],
        "classes": [],
        "relationships": [],
    }

    # capture relevant sys.modules keys
    try:
        data["sys_modules"] = sorted([k for k in sys.modules.keys() if k.startswith("backend.src.models")])
    except Exception as e:
        data["sys_modules_error"] = str(e)

    # Try to inspect SQLAlchemy Base registry if available
    try:
        from backend.src.db import Base

        for mapper in getattr(Base, "registry").mappers:
            cls = mapper.class_
            m = {"name": cls.__name__, "module": cls.__module__, "id": _safe_id(cls)}
            data["mappers"].append(m)
            # relationships
            try:
                for rel in mapper.relationships:
                    try:
                        arg = rel.argument
                    except Exception:
                        arg = None
                    relinfo = {
                        "owner": cls.__name__,
                        "owner_module": cls.__module__,
                        "key": rel.key,
                        "argument": str(arg),
                        "back_populates": getattr(rel, "back_populates", None),
                    }
                    # attempt to get the other side's mapper info
                    try:
                        if rel.back_populates:
                            other = rel.mapper.get_property(rel.back_populates, _configure_mappers=False)
                            other_cls = getattr(other.mapper, "class_", None)
                            relinfo["other_cls_name"] = other_cls.__name__ if other_cls else None
                            relinfo["other_cls_module"] = other_cls.__module__ if other_cls else None
                            relinfo["other_cls_id"] = _safe_id(other_cls)
                    except Exception as e:
                        relinfo["other_error"] = str(e)
                    data["relationships"].append(relinfo)
            except Exception as e:
                data.setdefault("relationship_errors", []).append(str(e))
    except Exception as e:
        data["base_error"] = str(e)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
    except Exception as e:
        # print error so pytest capture will show it
        print('ERROR writing debug dump:', e)

    # also print a short line to stdout so pytest capture shows path
    print("WROTE DEBUG DUMP:", str(path))
    return str(path)


def pytest_sessionstart(session):
    """Called after the `Session` object has been created and before performing collection and entering the run test loop."""
    _collect_state("collection_start")


def pytest_runtest_setup(item):
    """Called before running each test item."""
    # limit frequency: only dump for contract/integration tests and a few unit tests to reduce noise
    node = item.nodeid
    # Dump for all tests to be aggressive; can be filtered if too noisy
    _collect_state("test_setup", nodeid=node)
