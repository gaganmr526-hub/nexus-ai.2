import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import RecoveryPlan, RecoveryAction


def score_plan(plan: RecoveryPlan) -> float:
    """Score recovery plan 0-1 based on completeness and cost."""
    if not plan.total_estimated_cost or not plan.projected_recovery_days:
        return 0.5
    # Lower cost and faster recovery = higher score
    cost_factor = max(0, 1.0 - plan.total_estimated_cost / 10_000_000)
    time_factor = max(0, 1.0 - plan.projected_recovery_days / 365)
    return round((cost_factor + time_factor) / 2, 4)


def get_plans(db: Session, company_id: str) -> list[RecoveryPlan]:
    return (
        db.query(RecoveryPlan)
        .filter(RecoveryPlan.company_id == company_id)
        .order_by(RecoveryPlan.created_at.desc())
        .all()
    )


def create_plan(db: Session, company_id: str, scenario_id: str | None,
                name: str, description: str | None = None,
                total_estimated_cost: float | None = None,
                projected_recovery_days: int | None = None,
                created_by_id: str | None = None) -> RecoveryPlan:
    plan = RecoveryPlan(
        id=str(uuid.uuid4()),
        company_id=company_id,
        scenario_id=scenario_id,
        name=name,
        description=description,
        status="draft",
        total_estimated_cost=total_estimated_cost,
        projected_recovery_days=projected_recovery_days,
        created_by_id=created_by_id,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def approve_plan(db: Session, plan_id: str, approver_id: str) -> RecoveryPlan | None:
    plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == plan_id).first()
    if plan:
        plan.status = "approved"
        plan.approved_by_id = approver_id
        plan.updated_at = datetime.utcnow()
        db.commit()
    return plan
