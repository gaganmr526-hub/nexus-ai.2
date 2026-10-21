import { apiClient } from './client'
import type { PurchaseOrder } from '@/types'

export const getPurchaseOrders = async (companyId: string) => {
  const res = await apiClient.get<PurchaseOrder[]>('/procurement/purchase-orders', {
    params: { company_id: companyId },
  })
  return res.data
}

export const getPurchaseOrder = async (id: string) => {
  const res = await apiClient.get<PurchaseOrder>(`/procurement/purchase-orders/${id}`)
  return res.data
}

export const createPurchaseOrder = async (data: Partial<PurchaseOrder>) => {
  const res = await apiClient.post<PurchaseOrder>('/procurement/purchase-orders', data)
  return res.data
}

export const updatePurchaseOrder = async (id: string, data: Partial<PurchaseOrder>) => {
  const res = await apiClient.put<PurchaseOrder>(`/procurement/purchase-orders/${id}`, data)
  return res.data
}

export const getRequisitions = async (companyId: string) => {
  const res = await apiClient.get<PurchaseOrder[]>('/procurement/requisitions', {
    params: { company_id: companyId },
  })
  return res.data
}

export const createRequisition = async (data: Partial<PurchaseOrder>) => {
  const res = await apiClient.post<PurchaseOrder>('/procurement/requisitions', data)
  return res.data
}
