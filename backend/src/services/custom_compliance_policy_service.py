from typing import Dict, Any, List


class CustomCompliancePolicyService:
    """Evaluate simple custom policies against a device configuration.

    Policy format (naive): {"required_rules": [{"protocol":"tcp","port":22}, ...]}
    """

    def evaluate(self, policy: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        required = policy.get("required_rules", [])
        rules = config.get("rules", [])

        missing = []
        for req in required:
            found = False
            for r in rules:
                if r.get("protocol") == req.get("protocol") and int(r.get("port")) == int(req.get("port")):
                    found = True
                    break
            if not found:
                missing.append(req)

        return {"compliant": len(missing) == 0, "missing": missing}
