from backend.src.services.remediation_service import RemediationService


def test_create_patches_from_suggestions():
    suggestions = {
        "d1": [{"action": "add_rule", "rule": {"id": "r2"}}, {"action": "remove_rule", "rule": {"id": "rX"}}]
    }
    svc = RemediationService()
    patches = svc.create_patches(suggestions)
    assert "d1" in patches
    acts = [p["action"] for p in patches["d1"]]
    assert "add" in acts
    assert "remove" in acts
