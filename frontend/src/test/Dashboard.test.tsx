import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import DashboardPage from '@/pages/DashboardPage'

// Mock the hooks
vi.mock('@/hooks/useCompany', () => ({
  useCompany: () => ({
    selectedCompany: { id: 'company-1', name: 'Test Corp', industry: 'Tech', is_demo: true, tenant_id: 'tenant-1' },
    companies: [],
    selectCompany: vi.fn(),
    isLoading: false,
  }),
}))

vi.mock('@/api/companies', () => ({
  getDashboardStats: vi.fn().mockResolvedValue({
    total_suppliers: 45,
    total_upstream_entities: 120,
    total_relationships: 87,
    shared_upstream_sources: 3,
    critical_risk_sources: 2,
    active_scenario_affected_suppliers: 12,
    products_at_risk: 5,
    estimated_revenue_exposure: 2500000,
    estimated_recovery_cost: 800000,
    risk_reduction_potential: 35,
    currency: 'USD',
    last_updated: new Date().toISOString(),
  }),
}))

vi.mock('@/api/dependencies', () => ({
  getFindings: vi.fn().mockResolvedValue([
    {
      id: 'f1',
      company_id: 'company-1',
      finding_type: 'hidden_dependency',
      title: 'Helios Semiconductor Dependency',
      description: '3 suppliers depend on Helios',
      severity: 'critical',
      status: 'open',
      confidence_score: 0.92,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]),
}))

vi.mock('@/api/suppliers', () => ({
  getSuppliers: vi.fn().mockResolvedValue([
    { id: 's1', name: 'Supplier A', criticality: 'high', tier_level: 1 },
    { id: 's2', name: 'Supplier B', criticality: 'low', tier_level: 2 },
  ]),
}))

function renderDashboard() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DashboardPage', () => {
  it('renders KPI cards when data loads', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Total Suppliers')).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByText('45')).toBeInTheDocument()
    })
  })

  it('shows DemoBanner when company is demo', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText(/SYNTHETIC DEMO DATA/i)).toBeInTheDocument()
    })
  })

  it('shows company name as heading', async () => {
    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Test Corp')).toBeInTheDocument()
    })
  })
})
