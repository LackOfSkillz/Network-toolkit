from typing import Dict, Any, List


"""
Suggest remediation hints based on a drift detection report.

The output is a mapping device -> list of hints; each hint is a simple dict
with an action and rule payload that can be fed into the remediation flow.
This module is intentionally minimal so test authors can assert on hint
structures without heavy dependencies.
"""


class TroubleshootingService:

    def suggest(self, drift_report: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        suggestions: Dict[str, List[Dict[str, Any]]] = {}
        for device, d in drift_report.items():
            missing = d.get("missing", [])
            extra = d.get("extra", [])
            hints: List[Dict[str, Any]] = []
            for m in missing:
                hints.append({"action": "add_rule", "rule": m, "message": f"Add rule {m.get('id') or m}"})
            for e in extra:
                hints.append({"action": "remove_rule", "rule": e, "message": f"Remove rule {e.get('id') or e}"})
            suggestions[device] = hints
        return suggestions
