"""
What-if modeling service.

This small service wraps the internal rule engine to provide a deterministic
analysis of how adding a firewall rule would change packet decisions across a
set of devices. The input `network_state` is a mapping of device names to a
simple state dict (allowed ports, existing rules). The service returns a
report per-device showing the decision before and after the new rule.

Design notes:
- Uses the pure `evaluate_rules` function for deterministic behavior.
- Uses a simple heuristic to decide whether a deny rule applies to devices
  based on their `allowed` entries — this keeps reports focused and
  predictable for demo purposes.
"""

from typing import List, Dict, Any
from backend.src.services.rule_engine import evaluate_rules


class WhatIfService:
    """What-if modeling service that uses a deterministic rule engine.

    network_state: device_name -> { 'ip': str, 'rules': [rule_dicts...], 'allowed': [...] }
    """

    def __init__(self, network_state: Dict[str, Dict[str, Any]] | None = None):
        self.network_state = network_state or {}

    def simulate_add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate adding a firewall rule and return per-device impact report.

        The `rule` dict should be compatible with the project's rule engine
        (fields like action/protocol/port). The function returns a dict with
        the original rule and a `device_reports` mapping containing the
        decision before and after applying the rule for each device.
        """
        report = {"rule": rule, "device_reports": {}}

        for device_name, state in self.network_state.items():
            ip = state.get("ip") or "0.0.0.0"
            # build rules: existing + new rule
            existing_rules = state.get("rules", [])
            allowed_entries = state.get("allowed", [])
            # representative packet for evaluation: src=test, dst=device_ip
            packet = {"src_ip": "0.0.0.0", "dst_ip": ip, "proto": rule.get("protocol") or rule.get("proto"), "port": rule.get("port")}

            # evaluate without the new rule
            base_decision = evaluate_rules(existing_rules, packet)

            # determine whether to apply the new rule to this device
            apply_rule = True
            # Heuristic: a deny rule only affects devices that currently have
            # an allowed entry matching the same proto/port. This keeps the
            # what-if report focused on likely impacts.
            if (rule.get("action") or rule.get("act")) == "deny":
                match_found = False
                for ent in allowed_entries:
                    if (ent.get("proto") == (rule.get("protocol") or rule.get("proto"))
                            and ent.get("port") == rule.get("port")):
                        match_found = True
                        break
                apply_rule = match_found

            merged = existing_rules + ([rule] if apply_rule else [])
            new_decision = evaluate_rules(merged, packet)

            report["device_reports"][device_name] = {"before": base_decision, "after": new_decision}

        return report
