from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import RiskFinding, User
from app.schemas.schemas import RiskFindingRead, RiskFindingUpdate
from app.deps import get_current_user, require_company_access
from app.services.risk_service import build_risk_register, update_supplier_risk_scores
from datetime import datetime

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("/register", response_model=list[RiskFindingRead])
def risk_register(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return build_risk_register(db, company_id)


@router.post("/refresh-scores")
def refresh_scores(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    count = update_supplier_risk_scores(db, company_id)
    return {"updated_suppliers": count}


@router.get("/findings/{finding_id}", response_model=RiskFindingRead)
def get_finding(
    finding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    finding = db.query(RiskFinding).filter(RiskFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    require_company_access(finding.company_id, db, current_user)
    return finding


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
    finding.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(finding)
    return finding
