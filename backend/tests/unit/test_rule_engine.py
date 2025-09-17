from backend.src.services.rule_engine import evaluate_rules


def test_rule_engine_allow_first():
    rules = [
        {"id": 1, "priority": 10, "protocol": "tcp", "port": 22, "action": "allow", "enabled": True},
        {"id": 2, "priority": 20, "protocol": "tcp", "port": 22, "action": "deny", "enabled": True},
    ]
    pkt = {"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "proto": "tcp", "port": 22}
    res = evaluate_rules(rules, pkt)
    assert res["decision"] == "allow"


def test_rule_engine_deny_higher_priority():
    rules = [
        {"id": 1, "priority": 5, "protocol": "tcp", "port": 443, "action": "deny", "enabled": True},
        {"id": 2, "priority": 10, "protocol": "tcp", "port": 443, "action": "allow", "enabled": True},
    ]
    pkt = {"src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "proto": "tcp", "port": 443}
    res = evaluate_rules(rules, pkt)
    assert res["decision"] == "deny"
