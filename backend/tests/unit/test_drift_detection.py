from backend.src.services.drift_detection_service import DriftDetectionService


def test_detect_missing_and_extra_rules():
    # desired config: d1 should allow tcp/22 and tcp/80
    desired = {
        "d1": {"rules": [{"id": "r1", "action": "allow", "protocol": "tcp", "port": 22},
                          {"id": "r2", "action": "allow", "protocol": "tcp", "port": 80}]}
    }

    # observed config: d1 only has tcp/22 and an extra deny tcp/23
    observed = {
        "d1": {"rules": [{"id": "r1", "action": "allow", "protocol": "tcp", "port": 22},
                          {"id": "rX", "action": "deny", "protocol": "tcp", "port": 23}]}
    }

    svc = DriftDetectionService()
    report = svc.compare(desired, observed)

    # expect report to indicate one missing rule (r2) and one extra rule (rX)
    assert "d1" in report
    assert report["d1"]["missing"] == [{"id": "r2", "action": "allow", "protocol": "tcp", "port": 80}]
    assert report["d1"]["extra"] == [{"id": "rX", "action": "deny", "protocol": "tcp", "port": 23}]
