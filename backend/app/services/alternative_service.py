from sqlalchemy.orm import Session
from app.models.models import AlternativeSupplier, Component, Supplier


def rank_alternatives(
    db: Session,
    company_id: str,
    component_id: str | None = None,
    weights: dict | None = None,
) -> list[AlternativeSupplier]:
    """Rank alternative suppliers using configurable weights."""
    if weights is None:
        weights = {
            "compatibility_score": 0.25,
            "capacity_score": 0.20,
            "reliability_score": 0.20,
            "geographic_exposure_score": 0.15,
            "concentration_score": 0.10,
            "lead_time_score": 0.10,
        }

    q = db.query(AlternativeSupplier).filter(AlternativeSupplier.company_id == company_id)
    if component_id:
        q = q.filter(AlternativeSupplier.component_id == component_id)
    alternatives = q.all()

    for alt in alternatives:
        score = 0.0
        score += (alt.compatibility_score or 0.5) * weights.get("compatibility_score", 0.25)
        score += (alt.capacity_score or 0.5) * weights.get("capacity_score", 0.20)
        score += (alt.reliability_score or 0.5) * weights.get("reliability_score", 0.20)
        # Invert geographic exposure (lower is better)
        geo_score = 1.0 - (alt.geographic_exposure_score or 0.5)
        score += geo_score * weights.get("geographic_exposure_score", 0.15)
        # Invert concentration (lower is better)
        conc_score = 1.0 - (alt.concentration_score or 0.5)
        score += conc_score * weights.get("concentration_score", 0.10)
        # Lead time score (shorter = better; normalise 0-120 days)
        lt = alt.lead_time_days or 60
        lt_score = max(0.0, 1.0 - lt / 120.0)
        score += lt_score * weights.get("lead_time_score", 0.10)

        alt.overall_score = round(score, 4)

    db.commit()
    alternatives.sort(key=lambda a: a.overall_score or 0, reverse=True)
    return alternatives


def compare_suppliers(
    db: Session,
    supplier_ids: list[str],
    company_id: str,
) -> list[dict]:
    results = []
    for sid in supplier_ids:
        supplier = db.query(Supplier).filter(Supplier.id == sid).first()
        alt = (
            db.query(AlternativeSupplier)
            .filter(
                AlternativeSupplier.supplier_id == sid,
                AlternativeSupplier.company_id == company_id,
            )
            .first()
        )
        if supplier:
            results.append({
                "supplier_id": sid,
                "name": supplier.name,
                "supplier_type": supplier.supplier_type,
                "geographic_region": supplier.geographic_region,
                "risk_score": supplier.risk_score,
                "compatibility_score": alt.compatibility_score if alt else None,
                "capacity_score": alt.capacity_score if alt else None,
                "overall_score": alt.overall_score if alt else None,
                "lead_time_days": alt.lead_time_days if alt else None,
                "quality_cert": alt.quality_cert if alt else None,
            })
    return results
