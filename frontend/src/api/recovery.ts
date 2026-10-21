import { apiClient } from './client'
import type { RecoveryPlan, RecoveryAction } from '@/types'

export const getRecoveryPlans = async (companyId: string) => {
  const res = await apiClient.get<RecoveryPlan[]>('/recovery/plans', {
    params: { company_id: companyId },
  })
  return res.data
}

export const getRecoveryPlan = async (id: string) => {
  const res = await apiClient.get<RecoveryPlan>(`/recovery/plans/${id}`)
  return res.data
}

export const createRecoveryPlan = async (data: Partial<RecoveryPlan>) => {
  const res = await apiClient.post<RecoveryPlan>('/recovery/plans', data)
  return res.data
}

export const updateRecoveryPlan = async (id: string, data: Partial<RecoveryPlan>) => {
  const res = await apiClient.put<RecoveryPlan>(`/recovery/plans/${id}`, data)
  return res.data
}

export const getRecoveryActions = async (planId: string) => {
  const res = await apiClient.get<RecoveryAction[]>(`/recovery/plans/${planId}/actions`)
  return res.data
}

export const createRecoveryAction = async (planId: string, data: Partial<RecoveryAction>) => {
  const res = await apiClient.post<RecoveryAction>(`/recovery/plans/${planId}/actions`, data)
  return res.data
}

export const updateRecoveryAction = async (
  planId: string,
  actionId: string,
  data: Partial<RecoveryAction>
) => {
  const res = await apiClient.put<RecoveryAction>(
    `/recovery/plans/${planId}/actions/${actionId}`,
    data
  )
  return res.data
}
