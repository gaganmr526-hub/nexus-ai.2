import { apiClient } from './client'
import type { Supplier } from '@/types'

export const getSuppliers = async (companyId: string, params?: Record<string, string | number>) => {
  const res = await apiClient.get<Supplier[]>('/suppliers', {
    params: { company_id: companyId, ...params },
  })
  return res.data
}

export const getSupplier = async (id: string) => {
  const res = await apiClient.get<Supplier>(`/suppliers/${id}`)
  return res.data
}

export const createSupplier = async (data: Partial<Supplier>) => {
  const res = await apiClient.post<Supplier>('/suppliers', data)
  return res.data
}

export const updateSupplier = async (id: string, data: Partial<Supplier>) => {
  const res = await apiClient.put<Supplier>(`/suppliers/${id}`, data)
  return res.data
}

export const deleteSupplier = async (id: string) => {
  await apiClient.delete(`/suppliers/${id}`)
}
