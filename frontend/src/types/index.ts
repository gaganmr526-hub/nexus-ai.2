export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_platform_admin: boolean
  created_at: string
}

export interface Company {
  id: string
  name: string
  industry: string
  description?: string
  is_demo: boolean
  tenant_id: string
}

export interface Supplier {
  id: string
  company_id: string
  name: string
  supplier_type: SupplierType
  tier_level: number
  risk_score: number
  criticality: 'low' | 'medium' | 'high' | 'critical'
  geographic_region?: string
  verification_status: VerificationStatus
  is_demo: boolean
  source_type: string
  confidence_score?: number
}

export type SupplierType =
  | 'buyer'
  | 'direct'
  | 'subtier'
  | 'manufacturer'
  | 'material'
  | 'facility'
  | 'logistics'
  | 'port'
  | 'region'
  | 'product'
  | 'production_facility'

export type VerificationStatus =
  | 'verified'
  | 'supplier_declared'
  | 'evidence_inference'
  | 'unverified'
  | 'unknown'
  | 'rejected'

export type RiskSeverity = 'low' | 'medium' | 'high' | 'critical'

export interface SupplierRelationship {
  id: string
  from_supplier_id: string
  to_supplier_id: string
  relationship_type: string
  evidence_source?: string
  confidence_score?: number
  verification_status: VerificationStatus
  source_type: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  metadata: {
    total_nodes: number
    total_edges: number
    company_id?: string
    generated_at: string
  }
}

export interface GraphNode {
  id: string
  data: {
    label: string
    supplier_type: SupplierType
    risk_score: number
    criticality: string
    geographic_region?: string
    verification_status: VerificationStatus
    downstream_count: number
    is_demo: boolean
  }
  position: { x: number; y: number }
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  data: {
    relationship_type: string
    confidence_score?: number
    verification_status: VerificationStatus
    evidence_source?: string
  }
  label?: string
}

export interface RiskFinding {
  id: string
  company_id: string
  finding_type: 'hidden_dependency' | 'concentration' | 'single_point_of_failure' | 'geographic_exposure'
  title: string
  description: string
  shared_upstream_supplier_id?: string
  severity: RiskSeverity
  status: 'open' | 'investigating' | 'verified' | 'rejected' | 'resolved'
  confidence_score?: number
  affected_suppliers_json?: AffectedSupplier[]
  affected_products_json?: AffectedProduct[]
  dependency_paths_json?: DependencyPath[]
  evidence_json?: Evidence[]
  recommended_action?: string
  analyst_notes?: string
  created_at: string
  updated_at: string
}

export interface AffectedSupplier {
  id: string
  name: string
  tier_level?: number
}

export interface AffectedProduct {
  id: string
  name: string
}

export interface DependencyPath {
  path: string[]
  confidence?: number
}

export interface Evidence {
  type: string
  description: string
  source?: string
}

export interface Scenario {
  id: string
  company_id: string
  name: string
  description?: string
  disruption_type: string
  target_supplier_id?: string
  duration_days: number
  capacity_reduction_pct: number
  start_date?: string
  status: 'draft' | 'running' | 'completed' | 'failed'
  is_predefined: boolean
  created_at: string
}

export interface ScenarioResult {
  id: string
  scenario_id: string
  direct_affected_count: number
  indirect_affected_count: number
  affected_components_count: number
  affected_products_count: number
  exposed_companies_count: number
  estimated_revenue_exposure: number
  estimated_cost: number
  estimated_shortfall_units: number
  recovery_duration_days: number
  residual_risk_score: number
  currency: string
  assumptions_json?: Record<string, unknown>
  result_json?: Record<string, unknown>
  calculated_at: string
}

export interface MitigationOption {
  id: string
  scenario_id: string
  option_type: string
  description: string
  estimated_cost: number
  currency: string
  time_to_implement_days: number
  expected_shortage_reduction_pct: number
  expected_revenue_protection: number
  residual_risk_score: number
  operational_constraints?: string
  data_quality_notes?: string
  ranking_score: number
}

export interface PurchaseOrder {
  id: string
  company_id: string
  supplier_id: string
  order_number: string
  status: 'draft' | 'pending_approval' | 'approved' | 'issued' | 'received' | 'cancelled'
  total_amount: number
  currency: string
  delivery_date?: string
  approval_status: string
  is_demo: boolean
  created_at: string
}

export interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  is_read: boolean
  related_entity_type?: string
  related_entity_id?: string
  created_at: string
}

export interface ImportJob {
  id: string
  company_id: string
  import_type: string
  filename: string
  status: 'pending' | 'validating' | 'preview' | 'confirmed' | 'importing' | 'completed' | 'failed'
  total_rows?: number
  valid_rows?: number
  invalid_rows?: number
  error_count?: number
  result_json?: Record<string, unknown>
  created_at: string
}

export interface AlternativeSupplier {
  id: string
  company_id: string
  component_id?: string
  supplier_id: string
  supplier_name?: string
  compatibility_score: number
  capacity_score: number
  lead_time_days: number
  quality_cert?: string
  geographic_exposure_score: number
  concentration_score: number
  reliability_score: number
  switching_cost_estimate?: number
  overall_score: number
  notes?: string
  verification_status: VerificationStatus
  source_type: string
}

export interface RecoveryPlan {
  id: string
  company_id: string
  scenario_id?: string
  name: string
  description?: string
  status: 'draft' | 'pending_approval' | 'approved' | 'active' | 'completed'
  total_estimated_cost?: number
  currency?: string
  projected_recovery_days?: number
  created_at: string
}

export interface RecoveryAction {
  id: string
  plan_id: string
  action_type: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  due_date?: string
  assignee?: string
  estimated_cost?: number
}

export interface DashboardStats {
  total_suppliers: number
  total_upstream_entities: number
  total_relationships: number
  shared_upstream_sources: number
  critical_risk_sources: number
  active_scenario_affected_suppliers: number
  products_at_risk: number
  estimated_revenue_exposure: number
  estimated_recovery_cost: number
  risk_reduction_potential: number
  currency: string
  last_updated: string
}

export interface Report {
  id: string
  company_id: string
  report_type: string
  title: string
  generated_at: string
  data: Record<string, unknown>
}

export interface ProcurementRequisition {
  id: string
  company_id: string
  supplier_id: string
  component_name: string
  quantity: number
  unit: string
  status: 'draft' | 'pending' | 'approved' | 'rejected'
  estimated_cost?: number
  currency: string
  created_at: string
}

export interface ColumnDef<T> {
  key: keyof T | string
  header: string
  render?: (value: unknown, row: T) => React.ReactNode
  sortable?: boolean
  className?: string
}
