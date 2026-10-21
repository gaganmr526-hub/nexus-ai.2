from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ScenarioResult, MitigationOption, User
from app.schemas.schemas import ScenarioResultRead, MitigationOptionRead
from app.deps import get_current_user, require_company_access
import json

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("/summary")
def impact_summary(
    scenario_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.query(ScenarioResult).filter(ScenarioResult.scenario_id == scenario_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="No result found. Run scenario first.")
    return {
        "scenario_id": scenario_id,
        "direct_affected_count": result.direct_affected_count,
        "indirect_affected_count": result.indirect_affected_count,
        "total_affected": result.direct_affected_count + result.indirect_affected_count,
        "affected_components_count": result.affected_components_count,
        "affected_products_count": result.affected_products_count,
        "estimated_revenue_exposure": result.estimated_revenue_exposure,
        "estimated_cost": result.estimated_cost,
        "estimated_shortfall_units": result.estimated_shortfall_units,
        "recovery_duration_days": result.recovery_duration_days,
        "residual_risk_score": result.residual_risk_score,
        "currency": result.currency,
        "calculated_at": result.calculated_at,
    }


@router.get("/financial")
def financial_impact(
    scenario_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.query(ScenarioResult).filter(ScenarioResult.scenario_id == scenario_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="No result found. Run scenario first.")
    assumptions = {}
    breakdown = {}
    if result.assumptions_json:
        try:
            assumptions = json.loads(result.assumptions_json)
        except Exception:
            pass
    if result.result_json:
        try:
            detail = json.loads(result.result_json)
            breakdown = detail.get("revenue_breakdown", {})
        except Exception:
            pass
    return {
        "scenario_id": scenario_id,
        "estimated_revenue_exposure": result.estimated_revenue_exposure,
        "estimated_cost": result.estimated_cost,
        "shortfall_units": result.estimated_shortfall_units,
        "currency": result.currency,
        "assumptions": assumptions,
        "revenue_breakdown": breakdown,
    }


@router.get("/mitigation-options", response_model=list[MitigationOptionRead])
def mitigation_options(
    scenario_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(MitigationOption)
        .filter(MitigationOption.scenario_id == scenario_id)
        .order_by(MitigationOption.ranking_score.desc())
        .all()
    )
