"""test_import.py — CSV import validation and commit tests."""
import pytest
import io
from app.services.import_service import (
    validate_suppliers_csv,
    commit_suppliers_import,
    get_template_csv,
)
from app.models.models import ImportJob, Supplier
import uuid

VALID_CSV = """name,supplier_type,tier_level,geographic_region,risk_score,criticality,verification_status
Test Supplier Alpha,direct,1,North America,0.45,high,unverified
Test Supplier Beta,subtier,2,Europe,0.62,medium,supplier_declared
"""

INVALID_CSV = """name,supplier_type,tier_level,geographic_region,risk_score
,direct,1,North America,0.5
Good Supplier,direct,bad_tier,Europe,0.3
"""


def test_validate_valid_csv(demo_company):
    result = validate_suppliers_csv(VALID_CSV, demo_company.id)
    assert result["total_rows"] == 2
    assert result["valid_rows"] == 2
    assert result["invalid_rows"] == 0
    assert result["errors"] == []


def test_validate_invalid_csv(demo_company):
    result = validate_suppliers_csv(INVALID_CSV, demo_company.id)
    assert result["total_rows"] == 2
    assert result["invalid_rows"] > 0
    assert len(result["errors"]) > 0


def test_validate_empty_name_flagged(demo_company):
    result = validate_suppliers_csv(INVALID_CSV, demo_company.id)
    name_errors = [e for e in result["errors"] if e["field"] == "name"]
    assert len(name_errors) > 0


def test_validate_bad_tier_flagged(demo_company):
    result = validate_suppliers_csv(INVALID_CSV, demo_company.id)
    tier_errors = [e for e in result["errors"] if e["field"] == "tier_level"]
    assert len(tier_errors) > 0


def test_commit_imports_suppliers(db, demo_company):
    job = ImportJob(
        id=str(uuid.uuid4()),
        company_id=demo_company.id,
        import_type="suppliers",
        status="preview",
    )
    db.add(job)
    db.commit()

    count = commit_suppliers_import(db, job, VALID_CSV, demo_company.id)
    assert count == 2

    # Verify in DB
    sups = db.query(Supplier).filter(
        Supplier.company_id == demo_company.id,
        Supplier.name.in_(["Test Supplier Alpha", "Test Supplier Beta"]),
    ).all()
    assert len(sups) == 2


def test_commit_deduplication(db, demo_company):
    """Importing the same CSV twice should not create duplicates."""
    job1 = ImportJob(id=str(uuid.uuid4()), company_id=demo_company.id, import_type="suppliers", status="preview")
    db.add(job1)
    db.commit()
    count1 = commit_suppliers_import(db, job1, VALID_CSV, demo_company.id)

    job2 = ImportJob(id=str(uuid.uuid4()), company_id=demo_company.id, import_type="suppliers", status="preview")
    db.add(job2)
    db.commit()
    count2 = commit_suppliers_import(db, job2, VALID_CSV, demo_company.id)

    assert count2 == 0, f"Expected 0 new imports (deduplication), got {count2}"


def test_get_template_suppliers():
    template = get_template_csv("suppliers")
    assert "name" in template
    assert "supplier_type" in template


def test_get_template_relationships():
    template = get_template_csv("relationships")
    assert "from_supplier_name" in template


def test_import_upload_endpoint(client, db, demo_company, admin_headers, demo_membership):
    csv_bytes = VALID_CSV.encode("utf-8")
    resp = client.post(
        f"/api/v1/imports/upload?company_id={demo_company.id}&import_type=suppliers",
        files={"file": ("suppliers.csv", csv_bytes, "text/csv")},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["total_rows"] == 2


def test_import_confirm_endpoint(client, db, demo_company, admin_headers, demo_membership):
    # Upload first
    csv_bytes = VALID_CSV.encode("utf-8")
    upload_resp = client.post(
        f"/api/v1/imports/upload?company_id={demo_company.id}&import_type=suppliers",
        files={"file": ("suppliers.csv", csv_bytes, "text/csv")},
        headers=admin_headers,
    )
    job_id = upload_resp.json()["job_id"]

    # Confirm
    confirm_resp = client.post(
        f"/api/v1/imports/{job_id}/confirm",
        headers=admin_headers,
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "completed"
