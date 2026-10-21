from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Scenario, ScenarioResult, User
from app.schemas.schemas import ScenarioCreate, ScenarioUpdate, ScenarioRead, ScenarioResultRead
from app.deps import get_current_user, require_company_access
from app.services.simulation_service import run_scenario
from app.graph.builder import build_graph
import uuid
from datetime import datetime

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

PREDEFINED_TEMPLATES = [
    {"name": "Semiconductor Shortage", "disruption_type": "supply_shortage", "duration_days": 90, "capacity_reduction_pct": 100.0, "description": "Complete shutdown of semiconductor supply"},
    {"name": "Port Disruption", "disruption_type": "logistics", "duration_days": 30, "capacity_reduction_pct": 80.0, "description": "Major port closure affecting logistics"},
    {"name": "Factory Fire", "disruption_type": "facility_damage", "duration_days": 60, "capacity_reduction_pct": 100.0, "description": "Critical manufacturing facility fire"},
    {"name": "Geopolitical Trade Ban", "disruption_type": "geopolitical", "duration_days": 180, "capacity_reduction_pct": 100.0, "description": "Trade sanctions cutting off a key region"},
    {"name": "Pandemic Supply Shock", "disruption_type": "pandemic", "duration_days": 120, "capacity_reduction_pct": 70.0, "description": "Pandemic causing partial supply disruption"},
    {"name": "Raw Material Shortage", "disruption_type": "material_shortage", "duration_days": 60, "capacity_reduction_pct": 50.0, "description": "Critical raw material unavailability"},
    {"name": "Logistics Strike", "disruption_type": "labor", "duration_days": 21, "capacity_reduction_pct": 90.0, "description": "Trucking/logistics industry strike"},
    {"name": "Cyber Attack on Supplier", "disruption_type": "cyber", "duration_days": 14, "capacity_reduction_pct": 80.0, "description": "Ransomware attack on key supplier systems"},
    {"name": "Natural Disaster", "disruption_type": "natural_disaster", "duration_days": 45, "capacity_reduction_pct": 100.0, "description": "Earthquake/flood destroying production facility"},
    {"name": "Bankruptcy of Key Supplier", "disruption_type": "financial", "duration_days": 365, "capacity_reduction_pct": 100.0, "description": "Critical supplier goes bankrupt"},
]


@router.get("/predefined")
def list_predefined():
    return PREDEFINED_TEMPLATES


@router.get("", response_model=list[ScenarioRead])
def list_scenarios(
    company_id: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Scenario)
    if company_id:
        require_company_access(company_id, db, current_user)
        q = q.filter(Scenario.company_id == company_id)
    return q.order_by(Scenario.created_at.desc()).all()


@router.post("", response_model=ScenarioRead, status_code=201)
def create_scenario(data: ScenarioCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(data.company_id, db, current_user)
    scenario = Scenario(id=str(uuid.uuid4()), created_by_id=current_user.id, **data.model_dump())
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioRead)
def get_scenario(scenario_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    require_company_access(scenario.company_id, db, current_user)
    return scenario


@router.put("/{scenario_id}", response_model=ScenarioRead)
def update_scenario(scenario_id: str, data: ScenarioUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    require_company_access(scenario.company_id, db, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(scenario, k, v)
    scenario.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    require_company_access(scenario.company_id, db, current_user)
    db.delete(scenario)
    db.commit()


@router.post("/{scenario_id}/run")
def run_scenario_endpoint(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    require_company_access(scenario.company_id, db, current_user)
    scenario.status = "running"
    db.commit()
    try:
        G = build_graph(db)
        result = run_scenario(db, scenario, G)
        scenario.status = "completed"
        db.commit()
        return {
            "scenario_id": scenario_id,
            "status": "completed",
            "result_id": result.id,
            "estimated_revenue_exposure": result.estimated_revenue_exposure,
            "direct_affected_count": result.direct_affected_count,
            "indirect_affected_count": result.indirect_affected_count,
        }
    except Exception as e:
        scenario.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}/result", response_model=ScenarioResultRead)
def get_result(scenario_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    require_company_access(scenario.company_id, db, current_user)
    result = db.query(ScenarioResult).filter(ScenarioResult.scenario_id == scenario_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="No result yet. Run the scenario first.")
    return result
