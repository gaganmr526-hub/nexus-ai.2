from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import RiskFinding, User
from app.schemas.schemas import RiskFindingRead, RiskFindingUpdate
from app.deps import get_current_user, require_company_access
from app.services.dependency_service import discover_hidden_dependencies
from app.graph.builder import build_graph
import json
from datetime import datetime

router = APIRouter(prefix="/dependencies", tags=["dependencies"])


@router.post("/analyze", response_model=list[RiskFindingRead])
def analyze(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    G = build_graph(db)
    findings = discover_hidden_dependencies(db, company_id, G)
    return findings


@router.get("/findings", response_model=list[RiskFindingRead])
def list_findings(
    company_id: str = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    query = db.query(RiskFinding).filter(RiskFinding.company_id == company_id)
    if status_filter:
        query = query.filter(RiskFinding.status == status_filter)
    if severity:
        query = query.filter(RiskFinding.severity == severity)
    return query.order_by(RiskFinding.created_at.desc()).all()


@router.put("/findings/{finding_id}", response_model=RiskFindingRead)
def update_finding(
    finding_id: str,
    data: RiskFindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    finding = db.query(RiskFinding).filter(RiskFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    require_company_access(finding.company_id, db, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(finding, k, v)
    finding.analyst_id = current_user.id
    finding.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(finding)
    return finding


@router.get("/findings/{finding_id}/paths")
def finding_paths(
    finding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    finding = db.query(RiskFinding).filter(RiskFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    require_company_access(finding.company_id, db, current_user)
    paths = {}
    if finding.dependency_paths_json:
        try:
            paths = json.loads(finding.dependency_paths_json)
        except Exception:
            pass
    return {"finding_id": finding_id, "paths": paths}
