"""Custom compliance policies API

This module provides simple endpoints to create and evaluate user-defined
compliance policies. Policies are stored as blobs and evaluated by the
service layer which understands the policy format.

These edits only add explanatory text for maintainers and consumers and
do not change behavior.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.models import CustomCompliancePolicy
from backend.src.services.custom_compliance_policy_service import CustomCompliancePolicyService
from backend.src.services.auth_dependency import get_current_user_dependency

router = APIRouter()


class PolicyIn(BaseModel):
    """Input payload used when creating a custom policy."""
    name: str
    description: str | None = None
    policy_blob: dict


@router.get("/custom-compliance-policies")
def list_policies(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    """Return a list of saved custom compliance policies (names only)."""
    policies = db.query(CustomCompliancePolicy).all()
    return ["name: %s" % p.name for p in policies]


@router.post("/custom-compliance-policies", status_code=201)
def create_policy(payload: PolicyIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    """Create and persist a custom compliance policy.

    The policy blob is stored as a string here in the prototype; in a
    real system you'd validate the policy schema before persisting.
    """
    p = CustomCompliancePolicy(name=payload.name, description=payload.description, policy_blob=str(payload.policy_blob))
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name}


class EvaluateIn(BaseModel):
    """Input payload for evaluating a policy against a configuration."""
    policy: dict
    config: dict


@router.post("/custom-compliance-policies/evaluate")
def evaluate_policy(payload: EvaluateIn, user=Depends(get_current_user_dependency)):
    """Evaluate an arbitrary policy against a provided device or network config."""
    svc = CustomCompliancePolicyService()
    res = svc.evaluate(payload.policy, payload.config)
    return res
