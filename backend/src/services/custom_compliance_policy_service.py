"""
Evaluate simple custom compliance policies against device configurations.

This module provides a tiny evaluator intended for demos and tests. A
policy is expected to include a `required_rules` list and the evaluator
checks whether those rule signatures appear in the device's observed
configuration. The returned dict contains a `compliant` boolean and a list
of `missing` rules for quick human consumption.

Design notes:
- Purposefully simple: exact-match checks on protocol+port. Production
  systems should use a richer rule expression language and canonicalization.
"""

from typing import Dict, Any, List


class CustomCompliancePolicyService:

    def evaluate(self, policy: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        required = policy.get("required_rules", [])
        rules = config.get("rules", [])

        missing = []
        for req in required:
            found = False
            for r in rules:
                # compare protocol and port as a naive equality check
                if r.get("protocol") == req.get("protocol") and int(r.get("port")) == int(req.get("port")):
                    found = True
                    break
            if not found:
                missing.append(req)

        return {"compliant": len(missing) == 0, "missing": missing}
