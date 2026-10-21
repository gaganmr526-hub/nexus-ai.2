import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import DataImportPage from '@/pages/DataImportPage'

vi.mock('@/hooks/useCompany', () => ({
  useCompany: () => ({
    selectedCompany: { id: 'co1', name: 'TestCorp', is_demo: false, industry: 'Tech', tenant_id: 't1' },
    companies: [],
    selectCompany: vi.fn(),
    isLoading: false,
  }),
}))

vi.mock('@/api/imports', () => ({
  getImportJobs: vi.fn().mockResolvedValue([]),
  uploadImportFile: vi.fn().mockResolvedValue({ id: 'j1', status: 'preview', total_rows: 10, valid_rows: 9, error_count: 1, filename: 'test.csv' }),
  confirmImport: vi.fn().mockResolvedValue({ id: 'j1', status: 'completed' }),
  downloadTemplate: vi.fn().mockRejectedValue(new Error('no template')),
}))

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DataImportPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DataImportPage', () => {
  it('renders drop zone', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText(/Drag & drop/i)).toBeInTheDocument()
    })
  })

  it('shows import type selector', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Suppliers')).toBeInTheDocument()
    })
  })

  it('renders sample template download button', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText(/Sample Template/i)).toBeInTheDocument()
    })
  })
})
