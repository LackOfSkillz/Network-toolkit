from backend.src.services.saved_view_service import SavedViewService
from backend.src.services.dashboard_widget_service import DashboardWidgetService
from backend.src.db import SessionLocal


def test_saved_view_create():
    db = SessionLocal()
    try:
        svc = SavedViewService()
        res = svc.create(db, "view1", "alice", {"nodes": []})
        assert res["name"] == "view1"
    finally:
        db.close()


def test_widget_create():
    db = SessionLocal()
    try:
        svc = DashboardWidgetService()
        res = svc.create(db, "w1", "chart", {"type": "pie"})
        assert res["type"] == "chart"
    finally:
        db.close()
