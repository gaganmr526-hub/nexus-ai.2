"""
seed_db.py
Load demo data from data/demo/ into the database via SQLAlchemy models.
"""
import sys
import os
import json
import csv
from datetime import datetime
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import event, text
from app.database import engine, SessionLocal, Base
import app.models.models as M  # noqa: F401 — registers all models

# SQLite needs FK constraints disabled during fixture seeding; PostgreSQL uses
# the insertion order below and does not support SQLite's PRAGMA statement.
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def _disable_fk(dbapi_conn, record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

DEMO_DIR = Path(__file__).parent.parent / "data" / "demo"


def load_json(filename):
    path = DEMO_DIR / filename
    if not path.exists():
        print(f"  ⚠ {filename} not found, skipping")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_csv(filename):
    path = DEMO_DIR / filename
    if not path.exists():
        print(f"  ⚠ {filename} not found, skipping")
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def coerce(row, fields_bool=None, fields_float=None, fields_int=None, fields_none=None):
    """Type-coerce a flat dict for SQLAlchemy insertion."""
    fields_bool = fields_bool or []
    fields_float = fields_float or []
    fields_int = fields_int or []
    fields_none = fields_none or []  # fields that should be None if empty string

    # Auto-parse ISO datetime strings for known timestamp fields
    DATETIME_FIELDS = {"created_at", "updated_at", "calculated_at", "start_date", "end_date",
                       "detected_at", "resolved_at", "order_date", "delivery_date", "effective_date",
                       "forecast_date", "snapshot_date"}
    for f in DATETIME_FIELDS:
        if f in row and isinstance(row[f], str) and row[f]:
            try:
                row[f] = datetime.fromisoformat(row[f])
            except ValueError:
                row[f] = None

    for f in fields_bool:
        if f in row:
            v = row[f]
            if isinstance(v, str):
                row[f] = v.lower() in ("true", "1", "yes")
    for f in fields_float:
        if f in row:
            v = row[f]
            if v == "" or v is None:
                row[f] = None
            else:
                try:
                    row[f] = float(v)
                except (ValueError, TypeError):
                    row[f] = None
    for f in fields_int:
        if f in row:
            v = row[f]
            if v == "" or v is None:
                row[f] = None
            else:
                try:
                    row[f] = int(float(v))
                except (ValueError, TypeError):
                    row[f] = None
    for f in fields_none:
        if f in row and row[f] == "":
            row[f] = None
    return row


def seed_table(db, Model, records, bool_fields=None, float_fields=None, int_fields=None, none_fields=None, label=""):
    inserted = 0
    skipped = 0
    for rec in records:
        rec = coerce(dict(rec), bool_fields, float_fields, int_fields, none_fields)
        existing = db.query(Model).filter(Model.id == rec["id"]).first()
        if existing:
            skipped += 1
            continue
        # Remove keys not in model
        valid_cols = {c.name for c in Model.__table__.columns}
        rec = {k: v for k, v in rec.items() if k in valid_cols}
        db.add(Model(**rec))
        inserted += 1
    db.commit()
    print(f"  {label or Model.__tablename__}: inserted={inserted}, skipped={skipped}")


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("\nSeeding database from demo data files...")

        # Companies
        seed_table(db, M.Company, load_json("companies.json"),
                   bool_fields=["is_demo"],
                   none_fields=["tenant_id", "description", "industry"],
                   label="Companies")

        # Users
        seed_table(db, M.User, load_json("users.json"),
                   bool_fields=["is_active", "is_platform_admin"],
                   label="Users")

        # Memberships
        seed_table(db, M.CompanyMembership, load_json("memberships.json"),
                   label="Memberships")

        # Suppliers (from CSV)
        seed_table(db, M.Supplier, load_csv("suppliers.csv"),
                   bool_fields=["is_demo"],
                   float_fields=["risk_score", "confidence_score"],
                   int_fields=["tier_level"],
                   none_fields=["tenant_id", "source_name", "geographic_region",
                                "verification_status", "criticality", "source_type"],
                   label="Suppliers")

        # Relationships (from CSV)
        seed_table(db, M.SupplierRelationship, load_csv("relationships.csv"),
                   float_fields=["confidence_score"],
                   none_fields=["notes", "tenant_id", "source_type", "evidence_source", "effective_date"],
                   label="SupplierRelationships")

        # Materials
        seed_table(db, M.Material, load_json("materials.json"),
                   none_fields=["description", "source_type"],
                   label="Materials")

        # Components
        seed_table(db, M.Component, load_json("components.json"),
                   float_fields=["unit_price"],
                   int_fields=["lead_time_days"],
                   none_fields=["description", "part_number", "supplier_id", "material_id"],
                   label="Components")

        # Products
        seed_table(db, M.Product, load_json("products.json"),
                   float_fields=["daily_demand", "revenue_per_unit"],
                   none_fields=["description", "product_code"],
                   label="Products")

        # BOM
        seed_table(db, M.BillOfMaterial, load_json("bom.json"),
                   float_fields=["quantity_required"],
                   none_fields=["unit"],
                   label="BillOfMaterials")

        # Inventory
        seed_table(db, M.InventorySnapshot, load_json("inventory.json"),
                   float_fields=["quantity_on_hand", "days_of_supply"],
                   none_fields=["supplier_id", "unit", "source_type"],
                   label="InventorySnapshots")

        # Demand Forecasts
        seed_table(db, M.DemandForecast, load_json("demand_forecasts.json"),
                   float_fields=["daily_demand", "confidence"],
                   int_fields=["forecast_period_days"],
                   label="DemandForecasts")

        # Purchase Orders
        seed_table(db, M.PurchaseOrder, load_json("purchase_orders.json"),
                   bool_fields=["is_demo"],
                   float_fields=["total_amount"],
                   none_fields=["shipping_terms", "payment_terms", "approval_status",
                                "approved_by_id", "source_type", "delivery_date"],
                   label="PurchaseOrders")

        # PO Items
        seed_table(db, M.PurchaseOrderItem, load_json("purchase_order_items.json"),
                   float_fields=["quantity", "unit_price"],
                   none_fields=["component_id", "description"],
                   label="PurchaseOrderItems")

        # Alternative Suppliers
        seed_table(db, M.AlternativeSupplier, load_json("alternative_suppliers.json"),
                   float_fields=["compatibility_score", "capacity_score", "geographic_exposure_score",
                                 "concentration_score", "reliability_score", "switching_cost_estimate",
                                 "overall_score"],
                   int_fields=["lead_time_days"],
                   none_fields=["component_id", "quality_cert", "notes"],
                   label="AlternativeSuppliers")

        # Disruptions
        seed_table(db, M.Disruption, load_json("disruptions.json"),
                   float_fields=["capacity_reduction_pct"],
                   none_fields=["affected_supplier_id", "end_date", "description", "source_type"],
                   label="Disruptions")

        # Scenarios
        seed_table(db, M.Scenario, load_json("scenarios.json"),
                   bool_fields=["is_predefined"],
                   float_fields=["capacity_reduction_pct"],
                   int_fields=["duration_days", "recovery_lead_time_days"],
                   none_fields=["target_supplier_id", "created_by_id", "start_date",
                                "inventory_assumption", "demand_level", "substitute_availability",
                                "description", "disruption_type"],
                   label="Scenarios")

        # Risk Findings
        seed_table(db, M.RiskFinding, load_json("risk_findings.json"),
                   float_fields=["confidence_score"],
                   none_fields=["shared_upstream_supplier_id", "analyst_id", "analyst_notes",
                                "dependency_paths_json", "evidence_json", "affected_products_json",
                                "affected_suppliers_json", "recommended_action", "source_type"],
                   label="RiskFindings")

        # Notifications
        seed_table(db, M.Notification, load_json("notifications.json"),
                   bool_fields=["is_read"],
                   none_fields=["company_id", "message", "notification_type",
                                "related_entity_type", "related_entity_id"],
                   label="Notifications")

        print("\n✅ Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
