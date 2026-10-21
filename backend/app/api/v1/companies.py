from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import (
    Company,
    CompanyMembership,
    MitigationOption,
    RiskFinding,
    Scenario,
    ScenarioResult,
    Supplier,
    SupplierRelationship,
    User,
)
from app.schemas.schemas import CompanyCreate, CompanyUpdate, CompanyRead, MembershipCreate, MembershipRead
from app.deps import get_current_user, require_company_access
import uuid
from datetime import datetime
import json

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_platform_admin:
        return db.query(Company).all()
    memberships = db.query(CompanyMembership).filter(CompanyMembership.user_id == current_user.id).all()
    ids = [m.company_id for m in memberships]
    return db.query(Company).filter(Company.id.in_(ids)).all()


@router.post("", response_model=CompanyRead, status_code=201)
def create_company(data: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = Company(id=str(uuid.uuid4()), tenant_id=str(uuid.uuid4()), **data.model_dump())
    db.add(company)
    # Auto-add creator as admin
    membership = CompanyMembership(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        company_id=company.id,
        role="admin",
    )
    db.add(membership)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(company_id, db, current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/stats")
def get_company_stats(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    suppliers = db.query(Supplier).filter(Supplier.company_id == company_id).all()
    supplier_ids = {supplier.id for supplier in suppliers}
    relationships = db.query(SupplierRelationship).filter(
        SupplierRelationship.from_supplier_id.in_(supplier_ids)
    ).all() if supplier_ids else []
    findings = db.query(RiskFinding).filter(RiskFinding.company_id == company_id).all()
    scenarios = db.query(Scenario).filter(Scenario.company_id == company_id).all()
    scenario_ids = [scenario.id for scenario in scenarios]
    latest_result = (
        db.query(ScenarioResult)
        .filter(ScenarioResult.scenario_id.in_(scenario_ids))
        .order_by(ScenarioResult.calculated_at.desc())
        .first()
    ) if scenario_ids else None
    mitigation_options = (
        db.query(MitigationOption)
        .filter(MitigationOption.scenario_id.in_(scenario_ids))
        .all()
    ) if scenario_ids else []

    affected_product_ids = set()
    for finding in findings:
        if finding.severity not in {"critical", "high"} or not finding.affected_products_json:
            continue
        try:
            product_ids = json.loads(finding.affected_products_json)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(product_ids, list):
            affected_product_ids.update(
                item if isinstance(item, str) else item.get("id")
                for item in product_ids
                if isinstance(item, str) or isinstance(item, dict)
            )

    shared_sources = {
        finding.shared_upstream_supplier_id
        for finding in findings
        if finding.finding_type == "hidden_dependency" and finding.shared_upstream_supplier_id
    }
    upstream_ids = {
        relationship.to_supplier_id
        for relationship in relationships
        if relationship.to_supplier_id not in supplier_ids
    }

    return {
        "total_suppliers": len(suppliers),
        "total_upstream_entities": len(upstream_ids),
        "total_relationships": len(relationships),
        "shared_upstream_sources": len(shared_sources),
        "critical_risk_sources": sum(
            1 for supplier in suppliers if supplier.criticality == "critical"
        ),
        "active_scenario_affected_suppliers": (
            latest_result.direct_affected_count + latest_result.indirect_affected_count
            if latest_result else 0
        ),
        "products_at_risk": max(
            len(affected_product_ids),
            latest_result.affected_products_count if latest_result else 0,
        ),
        "estimated_revenue_exposure": latest_result.estimated_revenue_exposure if latest_result else 0,
        "estimated_recovery_cost": latest_result.estimated_cost if latest_result else 0,
        "risk_reduction_potential": max(
            (option.expected_shortage_reduction_pct or 0 for option in mitigation_options),
            default=0,
        ),
        "currency": latest_result.currency if latest_result else "USD",
        "last_updated": datetime.utcnow().isoformat(),
    }


@router.put("/{company_id}", response_model=CompanyRead)
def update_company(company_id: str, data: CompanyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(company_id, db, current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(company, k, v)
    company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(company_id, db, current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()


@router.get("/{company_id}/members", response_model=list[MembershipRead])
def list_members(company_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(company_id, db, current_user)
    return db.query(CompanyMembership).filter(CompanyMembership.company_id == company_id).all()


@router.post("/{company_id}/members", response_model=MembershipRead, status_code=201)
def add_member(company_id: str, data: MembershipCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_company_access(company_id, db, current_user)
    existing = db.query(CompanyMembership).filter(
        CompanyMembership.company_id == company_id,
        CompanyMembership.user_id == data.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")
    membership = CompanyMembership(
        id=str(uuid.uuid4()),
        company_id=company_id,
        user_id=data.user_id,
        role=data.role,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
