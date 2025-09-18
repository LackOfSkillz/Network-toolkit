from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.services.what_if_service import WhatIfService
from backend.src.services.auth_dependency import get_current_user_dependency
from backend.src.db import get_db
from backend.src.models import NetworkDevice, FirewallRule

"""
Lightweight what-if analysis endpoint.

This endpoint builds a small representation of the network (devices and
their allowed ports) from either a saved configuration or a simple default
set, then delegates to the `WhatIfService` which runs the deterministic
rule engine to see how adding a rule would affect packet decisions.
"""

router = APIRouter()


class WhatIfRule(BaseModel):
    """Input model describing a firewall rule to simulate."""

    action: str
    proto: str
    port: int
    target: str | None = "all"
    configuration_id: int | None = None


@router.post("/what-if")
async def simulate(rule: WhatIfRule, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    network_state = {}

    if rule.configuration_id:
        # load devices and firewall rules tied to the configuration
        devices = db.query(NetworkDevice).filter(NetworkDevice.configuration_id == rule.configuration_id).all()
        fw_rules = db.query(FirewallRule).filter(FirewallRule.configuration_id == rule.configuration_id).all()

        for d in devices:
            # devices may have a 'config' JSON with allowed ports; try to load it
            allowed = []
            cfg = d.config or {}
            # expected cfg format: {"allowed": [{"proto": "tcp", "port": 22}]}
            if isinstance(cfg, dict) and "allowed" in cfg:
                allowed = cfg.get("allowed")
            network_state[d.name or f"device-{d.id}"] = {"allowed": allowed}

        # incorporate existing firewall rules as "allowed" entries for modeling purposes
        for r in fw_rules:
            # if action is allow, add to allowed lists where appropriate
            if r.action and r.action.lower() == "allow":
                # naive: add allowing rule to all devices
                for s in network_state.values():
                    s.setdefault("allowed", []).append({"proto": r.protocol, "port": r.port})

    if not network_state:
        network_state = {
            "device1": {"allowed": [{"proto": "tcp", "port": 22}]},
            "device2": {"allowed": [{"proto": "tcp", "port": 80}]},
        }

    svc = WhatIfService(network_state)
    return svc.simulate_add_rule(rule.model_dump())
