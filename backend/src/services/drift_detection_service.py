"""
Detect configuration drift by comparing desired to observed rules per device.

The compare function returns a report listing rules that are missing (in
desired but not observed) and extra (in observed but not desired).
"""

from typing import Dict, Any, List


class DriftDetectionService:

    def compare(self, desired: Dict[str, Any], observed: Dict[str, Any]) -> Dict[str, Any]:
        report: Dict[str, Any] = {}

        for device, d_cfg in desired.items():
            desired_rules: List[Dict[str, Any]] = d_cfg.get("rules", [])
            obs_rules: List[Dict[str, Any]] = observed.get(device, {}).get("rules", [])

            # Identify missing: in desired but not in observed (by id if present, else by full rule)
            obs_by_id = {r.get("id"): r for r in obs_rules if r.get("id")}
            desired_missing: List[Dict[str, Any]] = []
            for dr in desired_rules:
                rid = dr.get("id")
                if rid:
                    if rid not in obs_by_id:
                        desired_missing.append(dr)
                else:
                    # fallback: full object comparison
                    if dr not in obs_rules:
                        desired_missing.append(dr)

            # Identify extra: in observed but not desired
            desired_by_id = {r.get("id"): r for r in desired_rules if r.get("id")}
            extras: List[Dict[str, Any]] = []
            for orr in obs_rules:
                oid = orr.get("id")
                if oid:
                    if oid not in desired_by_id:
                        extras.append(orr)
                else:
                    if orr not in desired_rules:
                        extras.append(orr)

            report[device] = {"missing": desired_missing, "extra": extras}

        return report
