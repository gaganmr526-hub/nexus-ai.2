import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import HiddenDependencyPage from '@/pages/HiddenDependencyPage'

vi.mock('@/hooks/useCompany', () => ({
  useCompany: () => ({
    selectedCompany: { id: 'co1', name: 'TestCorp', is_demo: true, industry: 'Tech', tenant_id: 't1' },
    companies: [],
    selectCompany: vi.fn(),
    isLoading: false,
  }),
}))

vi.mock('@/api/dependencies', () => ({
  getFindings: vi.fn().mockResolvedValue([
    {
      id: 'f1',
      company_id: 'co1',
      finding_type: 'hidden_dependency',
      title: 'Helios Semiconductor Dependency',
      description: '3 direct suppliers all depend on Helios Semiconductor Works',
      severity: 'critical',
      status: 'open',
      confidence_score: 0.92,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'f2',
      company_id: 'co1',
      finding_type: 'concentration',
      title: 'Asia Pacific Concentration',
      description: 'High geographic concentration in APAC',
      severity: 'high',
      status: 'investigating',
      confidence_score: 0.75,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]),
  analyzeHiddenDependencies: vi.fn().mockResolvedValue([]),
  updateFindingStatus: vi.fn().mockResolvedValue({}),
}))

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <HiddenDependencyPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('HiddenDependencyPage', () => {
  it('renders findings list', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Helios Semiconductor Dependency')).toBeInTheDocument()
    })
  })

  it('severity badge renders correctly for critical finding', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Critical')).toBeInTheDocument()
    })
  })

  it('shows Helios demo callout for demo company', async () => {
    renderPage()
    await waitFor(() => {
      const elements = screen.getAllByText(/Helios Semiconductor Works/i)
      expect(elements.length).toBeGreaterThan(0)
    })
  })
})
