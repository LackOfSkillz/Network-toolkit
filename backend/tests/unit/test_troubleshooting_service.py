from backend.src.services.troubleshooting_service import TroubleshootingService


def test_suggest_from_drift_report():
    drift = {
        "d1": {
            "missing": [{"id": "r2", "action": "allow", "protocol": "tcp", "port": 80}],
            "extra": [{"id": "rX", "action": "deny", "protocol": "tcp", "port": 23}],
        }
    }

    svc = TroubleshootingService()
    suggestions = svc.suggest(drift)
    assert "d1" in suggestions
    msgs = [s["action"] for s in suggestions["d1"]]
    assert "add_rule" in msgs
    assert "remove_rule" in msgs
