import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Float, Integer, Boolean, DateTime, ForeignKey,
    Enum as SAEnum, JSON, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SupplierTypeEnum(str, enum.Enum):
    buyer = "buyer"
    direct = "direct"
    subtier = "subtier"
    manufacturer = "manufacturer"
    material = "material"
    facility = "facility"
    logistics = "logistics"
    port = "port"
    region = "region"
    product = "product"
    production_facility = "production_facility"


class RelationshipTypeEnum(str, enum.Enum):
    supplies = "supplies"
    manufactures = "manufactures"
    depends_on = "depends_on"
    transports_through = "transports_through"
    produces_from = "produces_from"
    operates_in = "operates_in"
    shares_upstream = "shares_upstream"
    substitutes_for = "substitutes_for"


class VerificationStatusEnum(str, enum.Enum):
    verified = "verified"
    supplier_declared = "supplier_declared"
    evidence_inference = "evidence_inference"
    unverified = "unverified"
    unknown = "unknown"
    rejected = "rejected"


class POStatusEnum(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    issued = "issued"
    received = "received"
    cancelled = "cancelled"


class DisruptionStatusEnum(str, enum.Enum):
    active = "active"
    resolved = "resolved"
    simulated = "simulated"


class SeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ScenarioStatusEnum(str, enum.Enum):
    draft = "draft"
    running = "running"
    completed = "completed"
    failed = "failed"


class FindingTypeEnum(str, enum.Enum):
    hidden_dependency = "hidden_dependency"
    concentration = "concentration"
    single_point_of_failure = "single_point_of_failure"
    geographic_exposure = "geographic_exposure"


class FindingStatusEnum(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    verified = "verified"
    rejected = "rejected"
    resolved = "resolved"


class ImportStatusEnum(str, enum.Enum):
    pending = "pending"
    validating = "validating"
    preview = "preview"
    confirmed = "confirmed"
    importing = "importing"
    completed = "completed"
    failed = "failed"
    reversed = "reversed"


class RecoveryPlanStatusEnum(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    active = "active"
    completed = "completed"


class RecoveryActionStatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class IntegrationStatusEnum(str, enum.Enum):
    configured = "configured"
    not_configured = "not_configured"
    error = "error"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    memberships: Mapped[list["CompanyMembership"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    permissions: Mapped[list["Permission"]] = relationship(back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="permissions")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    memberships: Mapped[list["CompanyMembership"]] = relationship(back_populates="company")
    suppliers: Mapped[list["Supplier"]] = relationship(back_populates="company")
    products: Mapped[list["Product"]] = relationship(back_populates="company")
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="company")
    disruptions: Mapped[list["Disruption"]] = relationship(back_populates="company")
    scenarios: Mapped[list["Scenario"]] = relationship(back_populates="company")
    risk_findings: Mapped[list["RiskFinding"]] = relationship(back_populates="company")
    recovery_plans: Mapped[list["RecoveryPlan"]] = relationship(back_populates="company")
    import_jobs: Mapped[list["ImportJob"]] = relationship(back_populates="company")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="company")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="company")
    integration_connections: Mapped[list["IntegrationConnection"]] = relationship(back_populates="company")
    alternative_suppliers: Mapped[list["AlternativeSupplier"]] = relationship(back_populates="company")
    inventory_snapshots: Mapped[list["InventorySnapshot"]] = relationship(back_populates="company")


class CompanyMembership(Base):
    __tablename__ = "company_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    user: Mapped["User"] = relationship(back_populates="memberships")
    company: Mapped["Company"] = relationship(back_populates="memberships")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    supplier_type: Mapped[str] = mapped_column(
        SAEnum(SupplierTypeEnum, name="suppliertype"), default=SupplierTypeEnum.direct
    )
    tier_level: Mapped[int] = mapped_column(Integer, default=1)
    risk_score: Mapped[Optional[float]] = mapped_column(Float)
    criticality: Mapped[Optional[str]] = mapped_column(String(50))
    geographic_region: Mapped[Optional[str]] = mapped_column(String(100))
    verification_status: Mapped[Optional[str]] = mapped_column(String(50))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    source_name: Mapped[Optional[str]] = mapped_column(String(255))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="suppliers")
    aliases: Mapped[list["SupplierAlias"]] = relationship(back_populates="supplier")
    facilities: Mapped[list["Facility"]] = relationship(back_populates="supplier")
    components: Mapped[list["Component"]] = relationship(back_populates="supplier")
    outgoing_relationships: Mapped[list["SupplierRelationship"]] = relationship(
        back_populates="from_supplier", foreign_keys="SupplierRelationship.from_supplier_id"
    )
    incoming_relationships: Mapped[list["SupplierRelationship"]] = relationship(
        back_populates="to_supplier", foreign_keys="SupplierRelationship.to_supplier_id"
    )
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="supplier")
    quotes: Mapped[list["SupplierQuote"]] = relationship(back_populates="supplier")
    inventory_snapshots: Mapped[list["InventorySnapshot"]] = relationship(back_populates="supplier")
    disruptions: Mapped[list["Disruption"]] = relationship(back_populates="affected_supplier")
    alternative_records: Mapped[list["AlternativeSupplier"]] = relationship(back_populates="supplier")


class SupplierAlias(Base):
    __tablename__ = "supplier_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="aliases")


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    facility_type: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    supplier: Mapped["Supplier"] = relationship(back_populates="facilities")


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    material_type: Mapped[Optional[str]] = mapped_column(String(100))
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    components: Mapped[list["Component"]] = relationship(back_populates="material")


class Component(Base):
    __tablename__ = "components"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_type: Mapped[Optional[str]] = mapped_column(String(100))
    part_number: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    supplier_id: Mapped[Optional[str]] = mapped_column(ForeignKey("suppliers.id"))
    material_id: Mapped[Optional[str]] = mapped_column(ForeignKey("materials.id"))
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="components")
    material: Mapped[Optional["Material"]] = relationship(back_populates="components")
    bom_entries: Mapped[list["BillOfMaterial"]] = relationship(back_populates="component")
    order_items: Mapped[list["PurchaseOrderItem"]] = relationship(back_populates="component")
    quotes: Mapped[list["SupplierQuote"]] = relationship(back_populates="component")
    inventory_snapshots: Mapped[list["InventorySnapshot"]] = relationship(back_populates="component")
    alternative_suppliers: Mapped[list["AlternativeSupplier"]] = relationship(back_populates="component")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_code: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    daily_demand: Mapped[Optional[float]] = mapped_column(Float)
    revenue_per_unit: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    company: Mapped["Company"] = relationship(back_populates="products")
    bom_entries: Mapped[list["BillOfMaterial"]] = relationship(back_populates="product")
    demand_forecasts: Mapped[list["DemandForecast"]] = relationship(back_populates="product")


class BillOfMaterial(Base):
    __tablename__ = "bill_of_materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    component_id: Mapped[str] = mapped_column(ForeignKey("components.id"), nullable=False)
    quantity_required: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    product: Mapped["Product"] = relationship(back_populates="bom_entries")
    component: Mapped["Component"] = relationship(back_populates="bom_entries")


class SupplierRelationship(Base):
    __tablename__ = "supplier_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    from_supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    to_supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(
        SAEnum(RelationshipTypeEnum, name="relationshiptype"), nullable=False
    )
    evidence_source: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    verification_status: Mapped[str] = mapped_column(
        SAEnum(VerificationStatusEnum, name="verificationstatus"), default=VerificationStatusEnum.unverified
    )
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    from_supplier: Mapped["Supplier"] = relationship(
        back_populates="outgoing_relationships", foreign_keys=[from_supplier_id]
    )
    to_supplier: Mapped["Supplier"] = relationship(
        back_populates="incoming_relationships", foreign_keys=[to_supplier_id]
    )
    evidence: Mapped[list["RelationshipEvidence"]] = relationship(back_populates="relationship")

    __table_args__ = (
        Index("ix_rel_from_to", "from_supplier_id", "to_supplier_id"),
    )


class RelationshipEvidence(Base):
    __tablename__ = "relationship_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    relationship_id: Mapped[str] = mapped_column(ForeignKey("supplier_relationships.id"), nullable=False)
    evidence_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    relationship: Mapped["SupplierRelationship"] = relationship(back_populates="evidence")


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    component_id: Mapped[str] = mapped_column(ForeignKey("components.id"), nullable=False)
    supplier_id: Mapped[Optional[str]] = mapped_column(ForeignKey("suppliers.id"))
    quantity_on_hand: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    days_of_supply: Mapped[Optional[float]] = mapped_column(Float)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    company: Mapped["Company"] = relationship(back_populates="inventory_snapshots")
    component: Mapped["Component"] = relationship(back_populates="inventory_snapshots")
    supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="inventory_snapshots")


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    forecast_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    daily_demand: Mapped[float] = mapped_column(Float, nullable=False)
    forecast_period_days: Mapped[int] = mapped_column(Integer, default=30)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    product: Mapped["Product"] = relationship(back_populates="demand_forecasts")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    order_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(
        SAEnum(POStatusEnum, name="postatus"), default=POStatusEnum.draft
    )
    total_amount: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    shipping_terms: Mapped[Optional[str]] = mapped_column(String(100))
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100))
    approval_status: Mapped[Optional[str]] = mapped_column(String(50))
    approved_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="purchase_orders")
    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
    items: Mapped[list["PurchaseOrderItem"]] = relationship(back_populates="order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    component_id: Mapped[Optional[str]] = mapped_column(ForeignKey("components.id"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    order: Mapped["PurchaseOrder"] = relationship(back_populates="items")
    component: Mapped[Optional["Component"]] = relationship(back_populates="order_items")


class SupplierQuote(Base):
    __tablename__ = "supplier_quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    component_id: Mapped[Optional[str]] = mapped_column(ForeignKey("components.id"))
    unit_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50))
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    supplier: Mapped["Supplier"] = relationship(back_populates="quotes")
    component: Mapped[Optional["Component"]] = relationship(back_populates="quotes")


class Disruption(Base):
    __tablename__ = "disruptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    disruption_type: Mapped[Optional[str]] = mapped_column(String(100))
    affected_supplier_id: Mapped[Optional[str]] = mapped_column(ForeignKey("suppliers.id"))
    status: Mapped[str] = mapped_column(
        SAEnum(DisruptionStatusEnum, name="disruptionstatus"), default=DisruptionStatusEnum.active
    )
    severity: Mapped[str] = mapped_column(
        SAEnum(SeverityEnum, name="severityenum"), default=SeverityEnum.medium
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    capacity_reduction_pct: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    company: Mapped["Company"] = relationship(back_populates="disruptions")
    affected_supplier: Mapped[Optional["Supplier"]] = relationship(back_populates="disruptions")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    disruption_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_supplier_id: Mapped[Optional[str]] = mapped_column(ForeignKey("suppliers.id"))
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    capacity_reduction_pct: Mapped[float] = mapped_column(Float, default=100.0)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    inventory_assumption: Mapped[Optional[str]] = mapped_column(String(100))
    demand_level: Mapped[Optional[str]] = mapped_column(String(50))
    recovery_lead_time_days: Mapped[int] = mapped_column(Integer, default=60)
    substitute_availability: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        SAEnum(ScenarioStatusEnum, name="scenariostatus"), default=ScenarioStatusEnum.draft
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    is_predefined: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="scenarios")
    target_supplier: Mapped[Optional["Supplier"]] = relationship()
    results: Mapped[list["ScenarioResult"]] = relationship(back_populates="scenario")
    mitigation_options: Mapped[list["MitigationOption"]] = relationship(back_populates="scenario")
    recovery_plans: Mapped[list["RecoveryPlan"]] = relationship(back_populates="scenario")


class ScenarioResult(Base):
    __tablename__ = "scenario_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    direct_affected_count: Mapped[int] = mapped_column(Integer, default=0)
    indirect_affected_count: Mapped[int] = mapped_column(Integer, default=0)
    affected_components_count: Mapped[int] = mapped_column(Integer, default=0)
    affected_products_count: Mapped[int] = mapped_column(Integer, default=0)
    exposed_companies_count: Mapped[int] = mapped_column(Integer, default=0)
    estimated_revenue_exposure: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_shortfall_units: Mapped[float] = mapped_column(Float, default=0.0)
    recovery_duration_days: Mapped[int] = mapped_column(Integer, default=0)
    residual_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    assumptions_json: Mapped[Optional[str]] = mapped_column(Text)
    result_json: Mapped[Optional[str]] = mapped_column(Text)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    scenario: Mapped["Scenario"] = relationship(back_populates="results")


class RiskFinding(Base):
    __tablename__ = "risk_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    finding_type: Mapped[str] = mapped_column(
        SAEnum(FindingTypeEnum, name="findingtype"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    shared_upstream_supplier_id: Mapped[Optional[str]] = mapped_column(ForeignKey("suppliers.id"))
    severity: Mapped[str] = mapped_column(
        SAEnum(SeverityEnum, name="severityenum2"), default=SeverityEnum.medium
    )
    status: Mapped[str] = mapped_column(
        SAEnum(FindingStatusEnum, name="findingstatus"), default=FindingStatusEnum.open
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    affected_suppliers_json: Mapped[Optional[str]] = mapped_column(Text)
    affected_products_json: Mapped[Optional[str]] = mapped_column(Text)
    dependency_paths_json: Mapped[Optional[str]] = mapped_column(Text)
    evidence_json: Mapped[Optional[str]] = mapped_column(Text)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text)
    analyst_notes: Mapped[Optional[str]] = mapped_column(Text)
    analyst_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="risk_findings")
    shared_upstream_supplier: Mapped[Optional["Supplier"]] = relationship()


class MitigationOption(Base):
    __tablename__ = "mitigation_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    option_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    time_to_implement_days: Mapped[Optional[int]] = mapped_column(Integer)
    expected_shortage_reduction_pct: Mapped[Optional[float]] = mapped_column(Float)
    expected_revenue_protection: Mapped[Optional[float]] = mapped_column(Float)
    residual_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    operational_constraints: Mapped[Optional[str]] = mapped_column(Text)
    data_quality_notes: Mapped[Optional[str]] = mapped_column(Text)
    ranking_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    scenario: Mapped["Scenario"] = relationship(back_populates="mitigation_options")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    scenario_id: Mapped[Optional[str]] = mapped_column(ForeignKey("scenarios.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        SAEnum(RecoveryPlanStatusEnum, name="recoveryplanstatus"), default=RecoveryPlanStatusEnum.draft
    )
    total_estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    projected_recovery_days: Mapped[Optional[int]] = mapped_column(Integer)
    approved_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    created_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="recovery_plans")
    scenario: Mapped[Optional["Scenario"]] = relationship(back_populates="recovery_plans")
    actions: Mapped[list["RecoveryAction"]] = relationship(back_populates="plan")


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("recovery_plans.id"), nullable=False)
    action_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        SAEnum(RecoveryActionStatusEnum, name="recoveryactionstatus"), default=RecoveryActionStatusEnum.pending
    )
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    plan: Mapped["RecoveryPlan"] = relationship(back_populates="actions")


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    import_type: Mapped[str] = mapped_column(String(100), nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        SAEnum(ImportStatusEnum, name="importstatus"), default=ImportStatusEnum.pending
    )
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    result_json: Mapped[Optional[str]] = mapped_column(Text)
    imported_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)

    company: Mapped["Company"] = relationship(back_populates="import_jobs")
    errors: Mapped[list["ImportError"]] = relationship(back_populates="job")


class ImportError(Base):
    __tablename__ = "import_errors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    job_id: Mapped[str] = mapped_column(ForeignKey("import_jobs.id"), nullable=False)
    row_number: Mapped[Optional[int]] = mapped_column(Integer)
    field_name: Mapped[Optional[str]] = mapped_column(String(100))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    raw_data: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    job: Mapped["ImportJob"] = relationship(back_populates="errors")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[Optional[str]] = mapped_column(ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text)
    notification_type: Mapped[Optional[str]] = mapped_column(String(100))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    related_entity_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    user: Mapped["User"] = relationship(back_populates="notifications")
    company: Mapped[Optional["Company"]] = relationship(back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    company_id: Mapped[Optional[str]] = mapped_column(ForeignKey("companies.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    entity_id: Mapped[Optional[str]] = mapped_column(String(36))
    old_values_json: Mapped[Optional[str]] = mapped_column(Text)
    new_values_json: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")
    company: Mapped[Optional["Company"]] = relationship(back_populates="audit_logs")


class IntegrationConnection(Base):
    __tablename__ = "integration_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(IntegrationStatusEnum, name="integrationstatus"), default=IntegrationStatusEnum.not_configured
    )
    config_json: Mapped[Optional[str]] = mapped_column(Text)
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    company: Mapped["Company"] = relationship(back_populates="integration_connections")


class AlternativeSupplier(Base):
    __tablename__ = "alternative_suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    component_id: Mapped[Optional[str]] = mapped_column(ForeignKey("components.id"))
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    compatibility_score: Mapped[Optional[float]] = mapped_column(Float)
    capacity_score: Mapped[Optional[float]] = mapped_column(Float)
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    quality_cert: Mapped[Optional[str]] = mapped_column(String(255))
    geographic_exposure_score: Mapped[Optional[float]] = mapped_column(Float)
    concentration_score: Mapped[Optional[float]] = mapped_column(Float)
    reliability_score: Mapped[Optional[float]] = mapped_column(Float)
    switching_cost_estimate: Mapped[Optional[float]] = mapped_column(Float)
    overall_score: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    verification_status: Mapped[Optional[str]] = mapped_column(String(50))
    source_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    company: Mapped["Company"] = relationship(back_populates="alternative_suppliers")
    component: Mapped[Optional["Component"]] = relationship(back_populates="alternative_suppliers")
    supplier: Mapped["Supplier"] = relationship(back_populates="alternative_records")
