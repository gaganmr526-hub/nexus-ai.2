from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------------------------------------------------------------------
# Base helpers
# ---------------------------------------------------------------------------

class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserRead(OrmBase):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_platform_admin: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    is_demo: bool = False


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None


class CompanyRead(OrmBase):
    id: str
    name: str
    industry: Optional[str]
    description: Optional[str]
    is_demo: bool
    tenant_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class MembershipCreate(BaseModel):
    user_id: str
    role: str = "member"


class MembershipRead(OrmBase):
    id: str
    user_id: str
    company_id: str
    role: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------

class SupplierCreate(BaseModel):
    company_id: str
    name: str
    supplier_type: str = "direct"
    tier_level: int = 1
    risk_score: Optional[float] = None
    criticality: Optional[str] = None
    geographic_region: Optional[str] = None
    verification_status: Optional[str] = None
    is_demo: bool = False
    source_type: Optional[str] = None
    source_name: Optional[str] = None
    confidence_score: Optional[float] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    supplier_type: Optional[str] = None
    tier_level: Optional[int] = None
    risk_score: Optional[float] = None
    criticality: Optional[str] = None
    geographic_region: Optional[str] = None
    verification_status: Optional[str] = None
    confidence_score: Optional[float] = None


class SupplierRead(OrmBase):
    id: str
    company_id: str
    name: str
    supplier_type: str
    tier_level: int
    risk_score: Optional[float]
    criticality: Optional[str]
    geographic_region: Optional[str]
    verification_status: Optional[str]
    is_demo: bool
    source_type: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Relationship
# ---------------------------------------------------------------------------

class RelationshipCreate(BaseModel):
    from_supplier_id: str
    to_supplier_id: str
    relationship_type: str
    confidence_score: Optional[float] = None
    verification_status: str = "unverified"
    notes: Optional[str] = None
    source_type: Optional[str] = None
    evidence_source: Optional[str] = None


class RelationshipUpdate(BaseModel):
    verification_status: Optional[str] = None
    confidence_score: Optional[float] = None
    notes: Optional[str] = None


class RelationshipRead(OrmBase):
    id: str
    from_supplier_id: str
    to_supplier_id: str
    relationship_type: str
    confidence_score: Optional[float]
    verification_status: str
    notes: Optional[str]
    source_type: Optional[str]
    evidence_source: Optional[str]
    created_at: datetime
    updated_at: datetime


class EvidenceCreate(BaseModel):
    evidence_type: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    observed_at: Optional[datetime] = None


class EvidenceRead(OrmBase):
    id: str
    relationship_id: str
    evidence_type: Optional[str]
    description: Optional[str]
    source_url: Optional[str]
    observed_at: Optional[datetime]
    created_at: datetime


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    id: str
    label: str
    supplier_type: str
    tier_level: int
    risk_score: Optional[float]
    criticality: Optional[str]
    geographic_region: Optional[str]
    company_id: str


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    confidence_score: Optional[float]
    verification_status: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class PathResult(BaseModel):
    paths: list[list[str]]
    path_count: int


class CentralityResult(BaseModel):
    betweenness: dict[str, float]
    in_degree: dict[str, float]
    out_degree: dict[str, float]
    pagerank: dict[str, float]


# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------

class ScenarioCreate(BaseModel):
    company_id: str
    name: str
    description: Optional[str] = None
    disruption_type: Optional[str] = None
    target_supplier_id: Optional[str] = None
    duration_days: int = 30
    capacity_reduction_pct: float = 100.0
    start_date: Optional[datetime] = None
    inventory_assumption: Optional[str] = None
    demand_level: Optional[str] = None
    recovery_lead_time_days: int = 60
    substitute_availability: Optional[str] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_supplier_id: Optional[str] = None
    duration_days: Optional[int] = None
    capacity_reduction_pct: Optional[float] = None
    recovery_lead_time_days: Optional[int] = None
    substitute_availability: Optional[str] = None


class ScenarioRead(OrmBase):
    id: str
    company_id: str
    name: str
    description: Optional[str]
    disruption_type: Optional[str]
    target_supplier_id: Optional[str]
    duration_days: int
    capacity_reduction_pct: float
    status: str
    is_predefined: bool
    created_at: datetime
    updated_at: datetime


class ScenarioResultRead(OrmBase):
    id: str
    scenario_id: str
    direct_affected_count: int
    indirect_affected_count: int
    affected_components_count: int
    affected_products_count: int
    exposed_companies_count: int
    estimated_revenue_exposure: float
    estimated_cost: float
    estimated_shortfall_units: float
    recovery_duration_days: int
    residual_risk_score: float
    currency: str
    assumptions_json: Optional[str]
    result_json: Optional[str]
    calculated_at: datetime


# ---------------------------------------------------------------------------
# Risk Findings
# ---------------------------------------------------------------------------

class RiskFindingUpdate(BaseModel):
    status: Optional[str] = None
    analyst_notes: Optional[str] = None
    severity: Optional[str] = None


class RiskFindingRead(OrmBase):
    id: str
    company_id: str
    finding_type: str
    title: str
    description: Optional[str]
    shared_upstream_supplier_id: Optional[str]
    severity: str
    status: str
    confidence_score: Optional[float]
    affected_suppliers_json: Optional[str]
    affected_products_json: Optional[str]
    dependency_paths_json: Optional[str]
    evidence_json: Optional[str] = None
    recommended_action: Optional[str]
    analyst_notes: Optional[str]
    source_type: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Recovery
# ---------------------------------------------------------------------------

class RecoveryPlanCreate(BaseModel):
    company_id: str
    scenario_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    total_estimated_cost: Optional[float] = None
    projected_recovery_days: Optional[int] = None


class RecoveryPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    total_estimated_cost: Optional[float] = None
    projected_recovery_days: Optional[int] = None


class RecoveryPlanRead(OrmBase):
    id: str
    company_id: str
    scenario_id: Optional[str]
    name: str
    description: Optional[str]
    status: str
    total_estimated_cost: Optional[float]
    projected_recovery_days: Optional[int]
    created_at: datetime
    updated_at: datetime


class RecoveryActionCreate(BaseModel):
    action_type: Optional[str] = None
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    estimated_cost: Optional[float] = None
    due_date: Optional[datetime] = None


class RecoveryActionRead(OrmBase):
    id: str
    plan_id: str
    action_type: Optional[str]
    description: Optional[str]
    assigned_to_id: Optional[str]
    status: str
    estimated_cost: Optional[float]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


# ---------------------------------------------------------------------------
# Procurement
# ---------------------------------------------------------------------------

class PurchaseOrderCreate(BaseModel):
    company_id: str
    supplier_id: str
    order_number: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    delivery_date: Optional[datetime] = None
    shipping_terms: Optional[str] = None
    payment_terms: Optional[str] = None


class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = None
    total_amount: Optional[float] = None
    delivery_date: Optional[datetime] = None
    shipping_terms: Optional[str] = None
    payment_terms: Optional[str] = None


class PurchaseOrderRead(OrmBase):
    id: str
    company_id: str
    supplier_id: str
    order_number: Optional[str]
    status: str
    total_amount: Optional[float]
    currency: str
    delivery_date: Optional[datetime]
    approval_status: Optional[str]
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class PurchaseOrderItemCreate(BaseModel):
    component_id: Optional[str] = None
    quantity: float
    unit_price: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None


class PurchaseOrderItemRead(OrmBase):
    id: str
    order_id: str
    component_id: Optional[str]
    quantity: float
    unit_price: Optional[float]
    currency: str
    description: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

class ImportJobRead(OrmBase):
    id: str
    company_id: str
    import_type: str
    filename: Optional[str]
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    error_count: int
    result_json: Optional[str]
    created_at: datetime
    updated_at: datetime


class ImportErrorRead(OrmBase):
    id: str
    job_id: str
    row_number: Optional[int]
    field_name: Optional[str]
    error_message: Optional[str]
    raw_data: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class NotificationRead(OrmBase):
    id: str
    user_id: str
    company_id: Optional[str]
    title: str
    message: Optional[str]
    notification_type: Optional[str]
    is_read: bool
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

class AuditLogRead(OrmBase):
    id: str
    user_id: Optional[str]
    company_id: Optional[str]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    old_values_json: Optional[str]
    new_values_json: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

class AlternativeSupplierRead(OrmBase):
    id: str
    company_id: str
    component_id: Optional[str]
    supplier_id: str
    compatibility_score: Optional[float]
    capacity_score: Optional[float]
    lead_time_days: Optional[int]
    quality_cert: Optional[str]
    overall_score: Optional[float]
    notes: Optional[str]
    source_type: Optional[str]
    created_at: datetime


class MitigationOptionRead(OrmBase):
    id: str
    scenario_id: str
    option_type: Optional[str]
    description: Optional[str]
    estimated_cost: Optional[float]
    currency: str
    time_to_implement_days: Optional[int]
    expected_shortage_reduction_pct: Optional[float]
    expected_revenue_protection: Optional[float]
    residual_risk_score: Optional[float]
    ranking_score: Optional[float]
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    app_name: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
    checks: dict[str, Any]


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    pages: int
