from backend.src.services.rule_engine import evaluate_rules


def test_overlapping_cidr_specificity():
    # Two rules: one broad CIDR, one more specific. The more specific should match.
    rules = [
        {"id": 1, "priority": 100, "enabled": True, "src_cidr": "0.0.0.0/0", "dst_cidr": "10.0.0.0/8", "protocol": "tcp", "port": 80, "action": "deny"},
        {"id": 2, "priority": 100, "enabled": True, "src_cidr": "0.0.0.0/0", "dst_cidr": "10.1.1.0/24", "protocol": "tcp", "port": 80, "action": "allow"},
    ]

    packet = {"src_ip": "1.2.3.4", "dst_ip": "10.1.1.5", "proto": "tcp", "port": 80}

    res = evaluate_rules(rules, packet)
    # Expect the more specific CIDR (id=2) to allow
    assert res["decision"] == "allow"
    assert res["rule"]["id"] == 2


def test_priority_and_id_tiebreaker():
    # Two rules matching the same packet. Lower priority value should win; if same priority, lower id should win.
    rules = [
        {"id": 10, "priority": 200, "enabled": True, "src_cidr": None, "dst_cidr": None, "protocol": "tcp", "port": 22, "action": "deny"},
        {"id": 2, "priority": 100, "enabled": True, "src_cidr": None, "dst_cidr": None, "protocol": "tcp", "port": 22, "action": "allow"},
        {"id": 1, "priority": 100, "enabled": True, "src_cidr": None, "dst_cidr": None, "protocol": "tcp", "port": 22, "action": "deny"},
    ]

    packet = {"src_ip": "8.8.8.8", "dst_ip": "10.0.0.5", "proto": "tcp", "port": 22}

    res = evaluate_rules(rules, packet)
    # priority=100 rules should be evaluated before priority=200
    # between id=1 and id=2 (same priority), id=1 is lower so it should win
    assert res["decision"] == "deny"
    assert res["rule"]["id"] == 1
