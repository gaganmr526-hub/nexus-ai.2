import csv
import io
import json
from sqlalchemy.orm import Session
from app.models.models import (
    Supplier, RiskFinding, Disruption, Scenario, ScenarioResult,
    AuditLog, PurchaseOrder, Company
)
from datetime import datetime


def export_suppliers_csv(db: Session, company_id: str) -> str:
    suppliers = db.query(Supplier).filter(Supplier.company_id == company_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "supplier_type", "tier_level", "risk_score",
                     "criticality", "geographic_region", "verification_status", "created_at"])
    for s in suppliers:
        writer.writerow([s.id, s.name, s.supplier_type, s.tier_level, s.risk_score,
                         s.criticality, s.geographic_region, s.verification_status, s.created_at])
    return output.getvalue()


def export_risk_findings_csv(db: Session, company_id: str) -> str:
    findings = db.query(RiskFinding).filter(RiskFinding.company_id == company_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "finding_type", "title", "severity", "status",
                     "confidence_score", "recommended_action", "created_at"])
    for f in findings:
        writer.writerow([f.id, f.finding_type, f.title, f.severity, f.status,
                         f.confidence_score, f.recommended_action, f.created_at])
    return output.getvalue()


def export_disruption_impact_csv(db: Session, scenario_id: str) -> str:
    result = db.query(ScenarioResult).filter(ScenarioResult.scenario_id == scenario_id).first()
    if not result:
        return "No result found for scenario."
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["scenario_id", "direct_affected", "indirect_affected",
                     "affected_components", "affected_products", "revenue_exposure",
                     "estimated_cost", "shortfall_units", "recovery_days", "residual_risk"])
    writer.writerow([
        result.scenario_id, result.direct_affected_count, result.indirect_affected_count,
        result.affected_components_count, result.affected_products_count,
        result.estimated_revenue_exposure, result.estimated_cost,
        result.estimated_shortfall_units, result.recovery_duration_days,
        result.residual_risk_score
    ])
    return output.getvalue()


def export_audit_csv(db: Session, company_id: str) -> str:
    logs = db.query(AuditLog).filter(AuditLog.company_id == company_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "action", "entity_type", "entity_id",
                     "ip_address", "created_at"])
    for log in logs:
        writer.writerow([log.id, log.user_id, log.action, log.entity_type,
                         log.entity_id, log.ip_address, log.created_at])
    return output.getvalue()


def generate_executive_summary(db: Session, company_id: str) -> dict:
    company = db.query(Company).filter(Company.id == company_id).first()
    suppliers = db.query(Supplier).filter(Supplier.company_id == company_id).all()
    findings = db.query(RiskFinding).filter(RiskFinding.company_id == company_id).all()
    disruptions = db.query(Disruption).filter(Disruption.company_id == company_id).all()

    critical_findings = [f for f in findings if f.severity in ("critical", "high")]
    active_disruptions = [d for d in disruptions if d.status == "active"]

    return {
        "company": {"id": company_id, "name": company.name if company else "Unknown"},
        "summary": {
            "total_suppliers": len(suppliers),
            "direct_suppliers": len([s for s in suppliers if s.tier_level == 1]),
            "total_findings": len(findings),
            "critical_high_findings": len(critical_findings),
            "open_findings": len([f for f in findings if f.status == "open"]),
            "active_disruptions": len(active_disruptions),
            "avg_risk_score": round(
                sum(s.risk_score or 0 for s in suppliers) / max(len(suppliers), 1), 3
            ),
        },
        "top_findings": [
            {
                "id": f.id,
                "title": f.title,
                "severity": f.severity,
                "status": f.status,
                "finding_type": f.finding_type,
            }
            for f in critical_findings[:5]
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }
