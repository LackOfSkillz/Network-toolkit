from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.src.db import get_db
from backend.src.models.custom_compliance_policy import CustomCompliancePolicy
from backend.src.services.custom_compliance_policy_service import CustomCompliancePolicyService
from backend.src.services.auth_dependency import get_current_user_dependency

router = APIRouter()


class PolicyIn(BaseModel):
    name: str
    description: str | None = None
    policy_blob: dict


@router.get("/custom-compliance-policies")
def list_policies(db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    policies = db.query(CustomCompliancePolicy).all()
    return ["name: %s" % p.name for p in policies]


@router.post("/custom-compliance-policies", status_code=201)
def create_policy(payload: PolicyIn, db: Session = Depends(get_db), user=Depends(get_current_user_dependency)):
    p = CustomCompliancePolicy(name=payload.name, description=payload.description, policy_blob=str(payload.policy_blob))
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name}


class EvaluateIn(BaseModel):
    policy: dict
    config: dict


@router.post("/custom-compliance-policies/evaluate")
def evaluate_policy(payload: EvaluateIn, user=Depends(get_current_user_dependency)):
    svc = CustomCompliancePolicyService()
    res = svc.evaluate(payload.policy, payload.config)
    return res
