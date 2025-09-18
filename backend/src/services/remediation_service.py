from typing import Dict, Any, List


"""
Create remediation patches from suggestion hints.

The service converts simple suggestion dictionaries (like add/remove rule)
into a normalized patch list which could be consumed by an automation
engine. This module is intentionally small and deterministic for testing.
"""


class RemediationService:

    def create_patches(self, suggestions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        patches: Dict[str, List[Dict[str, Any]]] = {}
        for device, hints in suggestions.items():
            device_patches: List[Dict[str, Any]] = []
            for h in hints:
                if h.get("action") == "add_rule":
                    device_patches.append({"action": "add", "rule": h.get("rule")})
                elif h.get("action") == "remove_rule":
                    device_patches.append({"action": "remove", "rule": h.get("rule")})
            patches[device] = device_patches
        return patches
