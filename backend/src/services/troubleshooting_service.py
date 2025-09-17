from typing import Dict, Any, List


class TroubleshootingService:
    """Provide simple remediation hints given a drift report."""

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
