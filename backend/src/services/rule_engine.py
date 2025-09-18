"""
Simple deterministic rule engine utilities.

This module provides a compact `evaluate_rules` function used by the
what-if modeling and packet decision simulations. It's intentionally small
and pure so it is deterministic and easy to unit test.
"""

from typing import List, Dict, Any, Optional
import ipaddress


def cidr_match(cidr: str | None, ip: str) -> bool:
    if not cidr:
        return True
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        return ipaddress.ip_address(ip) in net
    except Exception:
        return False


def evaluate_rules(rules: List[Dict[str, Any]], packet: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically evaluate rules against a packet.

    Rules are expected to have: action (allow/deny), protocol, port, priority (lower first), enabled, src_cidr, dst_cidr
    packet: { src_ip, dst_ip, proto, port }
    Returns: { decision: 'allow'|'deny'|'no-match', rule: matched_rule or None }
    """
    def prefix_len(cidr: Optional[str]) -> int:
        if not cidr:
            return 0
        try:
            return ipaddress.ip_network(cidr, strict=False).prefixlen
        except Exception:
            return 0

    # sort by priority asc, then by destination CIDR specificity (more specific first),
    # then by source CIDR specificity, then by id asc
    sorted_rules = sorted(
        rules,
        key=lambda r: (
            r.get("priority", 100),
            -prefix_len(r.get("dst_cidr")),
            -prefix_len(r.get("src_cidr")),
            r.get("id", 0),
        ),
    )

    for r in sorted_rules:
        if not r.get("enabled", True):
            continue
        if r.get("protocol") and r.get("protocol").lower() != packet.get("proto").lower():
            continue
        if r.get("port") and int(r.get("port")) != int(packet.get("port")):
            continue
        # CIDR/source/dest matching
        if not cidr_match(r.get("src_cidr"), packet.get("src_ip")):
            continue
        if not cidr_match(r.get("dst_cidr"), packet.get("dst_ip")):
            continue

        # first matching rule decides
        return {"decision": r.get("action"), "rule": r}

    return {"decision": "no-match", "rule": None}
