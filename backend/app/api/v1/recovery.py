from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import RecoveryPlan, RecoveryAction, User
from app.schemas.schemas import RecoveryPlanCreate, RecoveryPlanUpdate, RecoveryPlanRead, RecoveryActionCreate, RecoveryActionRead
from app.deps import get_current_user, require_company_access
from app.services.recovery_service import create_plan, get_plans, approve_plan
import uuid
from datetime import datetime

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.get("/plans", response_model=list[RecoveryPlanRead])
def list_plans(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return get_plans(db, company_id)


@router.post("/plans", response_model=RecoveryPlanRead, status_code=201)
def create_recovery_plan(
    data: RecoveryPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(data.company_id, db, current_user)
    return create_plan(
        db, data.company_id, data.scenario_id, data.name, data.description,
        data.total_estimated_cost, data.projected_recovery_days, current_user.id
    )


@router.get("/plans/{plan_id}", response_model=RecoveryPlanRead)
def get_plan(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    require_company_access(plan.company_id, db, current_user)
    return plan


@router.put("/plans/{plan_id}", response_model=RecoveryPlanRead)
def update_plan(
    plan_id: str,
    data: RecoveryPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    require_company_access(plan.company_id, db, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(plan, k, v)
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/plans/{plan_id}/approve")
def approve(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    require_company_access(plan.company_id, db, current_user)
    plan = approve_plan(db, plan_id, current_user.id)
    return {"id": plan_id, "status": plan.status}


@router.get("/plans/{plan_id}/actions", response_model=list[RecoveryActionRead])
def list_actions(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    require_company_access(plan.company_id, db, current_user)
    return db.query(RecoveryAction).filter(RecoveryAction.plan_id == plan_id).all()


@router.post("/plans/{plan_id}/actions", response_model=RecoveryActionRead, status_code=201)
def create_action(
    plan_id: str,
    data: RecoveryActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    require_company_access(plan.company_id, db, current_user)
    action = RecoveryAction(id=str(uuid.uuid4()), plan_id=plan_id, **data.model_dump())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action
