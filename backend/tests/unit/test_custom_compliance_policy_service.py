from backend.src.services.custom_compliance_policy_service import CustomCompliancePolicyService


def test_evaluate_policy_missing_rule():
    svc = CustomCompliancePolicyService()
    policy = {"required_rules": [{"protocol": "tcp", "port": 22}]}
    config = {"rules": [{"id": "r1", "protocol": "tcp", "port": 80}]}
    res = svc.evaluate(policy, config)
    assert res["compliant"] is False
    assert res["missing"] == [{"protocol": "tcp", "port": 22}]
