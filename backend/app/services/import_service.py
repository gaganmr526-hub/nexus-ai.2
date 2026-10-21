import json
import csv
import io
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import (
    ImportJob, ImportError as ImportErrorModel, Supplier, SupplierRelationship, Company
)


SUPPLIER_COLUMNS = ["name", "supplier_type", "tier_level", "geographic_region",
                    "risk_score", "criticality", "verification_status"]

RELATIONSHIP_COLUMNS = ["from_supplier_name", "to_supplier_name", "relationship_type",
                        "confidence_score", "verification_status"]


def validate_suppliers_csv(content: str, company_id: str) -> dict:
    """Validate CSV content for supplier import. Returns preview dict."""
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    errors = []
    valid = []

    for i, row in enumerate(rows, start=2):
        row_errors = []
        if not row.get("name", "").strip():
            row_errors.append({"row": i, "field": "name", "message": "Name is required"})
        if row.get("tier_level"):
            try:
                int(row["tier_level"])
            except ValueError:
                row_errors.append({"row": i, "field": "tier_level", "message": "Must be an integer"})
        if row_errors:
            errors.extend(row_errors)
        else:
            valid.append(row)

    return {
        "total_rows": len(rows),
        "valid_rows": len(valid),
        "invalid_rows": len(rows) - len(valid),
        "errors": errors,
        "preview": valid[:5],
    }


def commit_suppliers_import(
    db: Session,
    job: ImportJob,
    content: str,
    company_id: str,
) -> int:
    """Commit supplier CSV into DB. Returns number imported."""
    reader = csv.DictReader(io.StringIO(content))
    imported = 0
    for row in reader:
        name = row.get("name", "").strip()
        if not name:
            continue
        # Duplicate detection by name
        existing = (
            db.query(Supplier)
            .filter(Supplier.company_id == company_id, Supplier.name == name)
            .first()
        )
        if existing:
            continue
        supplier = Supplier(
            id=str(uuid.uuid4()),
            company_id=company_id,
            name=name,
            supplier_type=row.get("supplier_type", "direct"),
            tier_level=int(row.get("tier_level", 1) or 1),
            geographic_region=row.get("geographic_region"),
            risk_score=float(row["risk_score"]) if row.get("risk_score") else None,
            criticality=row.get("criticality"),
            verification_status=row.get("verification_status", "unverified"),
            source_type="import",
        )
        db.add(supplier)
        imported += 1
    db.commit()
    return imported


def get_template_csv(import_type: str) -> str:
    """Return a sample CSV template."""
    templates = {
        "suppliers": "name,supplier_type,tier_level,geographic_region,risk_score,criticality,verification_status\nExample Supplier,direct,1,North America,0.5,medium,unverified",
        "relationships": "from_supplier_name,to_supplier_name,relationship_type,confidence_score,verification_status\nSupplier A,Supplier B,depends_on,0.8,unverified",
        "inventory": "component_name,quantity_on_hand,unit,days_of_supply,snapshot_date\nWidget A,1000,units,30,2024-01-01",
    }
    return templates.get(import_type, "# Template not available for this type")
