from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.deps import get_current_user, require_company_access
from app.services.export_service import (
    export_suppliers_csv, export_risk_findings_csv,
    export_disruption_impact_csv, export_audit_csv,
    generate_executive_summary
)
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["reports"])


class ExportRequest(BaseModel):
    company_id: str
    report_type: str
    scenario_id: str | None = None
    format: str = "json"


@router.get("/executive-summary")
def executive_summary(
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    return generate_executive_summary(db, company_id)


@router.get("/dependency-findings")
def dependency_findings(
    company_id: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    if format == "csv":
        csv_data = export_risk_findings_csv(db, company_id)
        return PlainTextResponse(csv_data, media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=findings.csv"})
    from app.models.models import RiskFinding
    findings = db.query(RiskFinding).filter(RiskFinding.company_id == company_id).all()
    return [{"id": f.id, "title": f.title, "severity": f.severity, "status": f.status,
              "finding_type": f.finding_type, "confidence_score": f.confidence_score} for f in findings]


@router.get("/disruption-impact")
def disruption_impact(
    scenario_id: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if format == "csv":
        csv_data = export_disruption_impact_csv(db, scenario_id)
        return PlainTextResponse(csv_data, media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=impact.csv"})
    from app.models.models import ScenarioResult
    result = db.query(ScenarioResult).filter(ScenarioResult.scenario_id == scenario_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="No result found")
    return {
        "scenario_id": scenario_id,
        "estimated_revenue_exposure": result.estimated_revenue_exposure,
        "direct_affected_count": result.direct_affected_count,
        "indirect_affected_count": result.indirect_affected_count,
        "affected_products_count": result.affected_products_count,
        "recovery_duration_days": result.recovery_duration_days,
    }


@router.get("/audit")
def audit_report(
    company_id: str = Query(...),
    format: str = Query("json"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(company_id, db, current_user)
    if format == "csv":
        csv_data = export_audit_csv(db, company_id)
        return PlainTextResponse(csv_data, media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=audit.csv"})
    from app.models.models import AuditLog
    logs = db.query(AuditLog).filter(AuditLog.company_id == company_id).all()
    return [{"id": l.id, "action": l.action, "entity_type": l.entity_type,
              "entity_id": l.entity_id, "created_at": l.created_at} for l in logs]


@router.post("/export")
def trigger_export(
    data: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_company_access(data.company_id, db, current_user)
    return {
        "status": "queued",
        "report_type": data.report_type,
        "company_id": data.company_id,
        "message": "Report generation queued. In production, this would trigger an async task.",
    }
