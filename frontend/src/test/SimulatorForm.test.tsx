import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import DisruptionSimulatorPage from '@/pages/DisruptionSimulatorPage'

vi.mock('@/hooks/useCompany', () => ({
  useCompany: () => ({
    selectedCompany: { id: 'co1', name: 'TestCorp', is_demo: false, industry: 'Tech', tenant_id: 't1' },
    companies: [],
    selectCompany: vi.fn(),
    isLoading: false,
  }),
}))

vi.mock('@/api/scenarios', () => ({
  getScenarios: vi.fn().mockResolvedValue([]),
  createScenario: vi.fn().mockResolvedValue({ id: 'sc1', name: 'Test Scenario', status: 'draft', is_predefined: false }),
  runScenario: vi.fn().mockResolvedValue({}),
  getScenarioResult: vi.fn().mockResolvedValue(null),
}))

vi.mock('@/api/suppliers', () => ({
  getSuppliers: vi.fn().mockResolvedValue([]),
}))

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DisruptionSimulatorPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DisruptionSimulatorPage', () => {
  it('renders scenario name input', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Taiwan Earthquake/i)).toBeInTheDocument()
    })
  })

  it('shows validation error when name is empty and form submitted', async () => {
    renderPage()
    const submitBtn = await screen.findByText('Create Scenario')
    await userEvent.click(submitBtn)
    await waitFor(() => {
      expect(screen.getByText('Name required')).toBeInTheDocument()
    })
  })

  it('shows duration and capacity sliders', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText(/Duration:/)).toBeInTheDocument()
      expect(screen.getByText(/Capacity Reduction:/)).toBeInTheDocument()
    })
  })
})
