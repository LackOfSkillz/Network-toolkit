from backend.src.services.what_if_service import WhatIfService


def test_simulate_add_rule_allow():
    network_state = {"d1": {"allowed": [{"proto": "tcp", "port": 22}]}}
    svc = WhatIfService(network_state)
    rule = {"action": "allow", "proto": "tcp", "port": 80}
    res = svc.simulate_add_rule(rule)
    assert "device_reports" in res
    assert "d1" in res["device_reports"]
    assert res["device_reports"]["d1"]["after"]["decision"] == "allow"


def test_simulate_add_rule_deny():
    network_state = {"d1": {"allowed": [{"proto": "tcp", "port": 22}]}, "d2": {"allowed": [{"proto": "tcp", "port": 80}]}}
    svc = WhatIfService(network_state)
    rule = {"action": "deny", "proto": "tcp", "port": 22}
    res = svc.simulate_add_rule(rule)
    assert "device_reports" in res
    assert res["device_reports"]["d1"]["after"]["decision"] == "deny"
    assert res["device_reports"]["d2"]["after"]["decision"] == "no-match"
