from backend.src.services.saved_view_service import SavedViewService
from backend.src.services.dashboard_widget_service import DashboardWidgetService


def test_saved_view_create(db_session):
    svc = SavedViewService()
    res = svc.create(db_session, "view1", "alice", {"nodes": []})
    assert res["name"] == "view1"


def test_widget_create(db_session):
    svc = DashboardWidgetService()
    res = svc.create(db_session, "w1", "chart", {"type": "pie"})
    assert res["type"] == "chart"
