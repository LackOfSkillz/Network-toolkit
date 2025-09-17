from typing import Dict, Any, List


class RemediationService:
    """Create simple remediation patches from suggestions.

    patches: { device: [ { action: 'add'|'remove', 'rule': {...} } ] }
    """

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
