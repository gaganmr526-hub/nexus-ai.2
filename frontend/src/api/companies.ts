import { apiClient } from './client'
import type { Company, DashboardStats } from '@/types'

export const getCompanies = async () => {
  const res = await apiClient.get<Company[]>('/companies')
  return res.data
}

export const getCompany = async (id: string) => {
  const res = await apiClient.get<Company>(`/companies/${id}`)
  return res.data
}

export const createCompany = async (data: Partial<Company>) => {
  const res = await apiClient.post<Company>('/companies', data)
  return res.data
}

export const getDashboardStats = async (companyId: string) => {
  const res = await apiClient.get<DashboardStats>(`/companies/${companyId}/stats`)
  return res.data
}

export const deleteCompany = async (id: string) => {
  await apiClient.delete(`/companies/${id}`)
}
