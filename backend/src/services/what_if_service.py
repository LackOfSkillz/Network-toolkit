from typing import List, Dict, Any
from backend.src.services.rule_engine import evaluate_rules


class WhatIfService:
    """What-if modeling service that uses a deterministic rule engine.

    network_state: device_name -> { 'ip': str, 'rules': [rule_dicts...] }
    """

    def __init__(self, network_state: Dict[str, Dict[str, Any]] | None = None):
        self.network_state = network_state or {}

    def simulate_add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate adding a firewall rule by inserting it into each device's rule set
        and evaluating a representative packet to see the decision change.

        rule should include fields compatible with rule_engine (action, protocol, port, priority, src_cidr, dst_cidr)
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
            # If the new rule is a deny, only apply it to devices that currently
            # have an allowed entry matching the same proto/port — otherwise a
            # deny for an unrelated port shouldn't be considered an "impact" on
            # that device in the what-if analysis.
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
