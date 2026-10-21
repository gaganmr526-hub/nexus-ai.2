import { createContext, createElement, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getCompanies } from '@/api/companies'
import type { Company } from '@/types'

interface CompanyContextValue {
  companies: Company[]
  selectedCompany: Company | null
  selectCompany: (id: string) => void
  isLoading: boolean
}

const CompanyContext = createContext<CompanyContextValue | null>(null)

export function CompanyProvider({ children }: { children: ReactNode }) {
  const [selectedCompanyId, setSelectedCompanyId] = useState<string | null>(
    () => localStorage.getItem('nexustrace_company_id')
  )

  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: getCompanies,
  })

  const selectedCompany =
    companies.find((company) => company.id === selectedCompanyId) ?? companies[0] ?? null

  const selectCompany = useCallback((id: string) => {
    localStorage.setItem('nexustrace_company_id', id)
    setSelectedCompanyId(id)
  }, [])

  const value = useMemo(
    () => ({ companies, selectedCompany, selectCompany, isLoading }),
    [companies, selectedCompany, selectCompany, isLoading]
  )

  return createElement(CompanyContext.Provider, { value }, children)
}

export function useCompany() {
  const context = useContext(CompanyContext)
  if (!context) throw new Error('useCompany must be used within CompanyProvider')
  return context
}
