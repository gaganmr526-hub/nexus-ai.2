import { apiClient } from './client'
import type { MitigationOption } from '@/types'

export const getMitigationOptions = async (scenarioId: string) => {
  const res = await apiClient.get<MitigationOption[]>('/impact/mitigation-options', {
    params: { scenario_id: scenarioId },
  })
  return res.data
}

export const getAlternativeSuppliers = async (companyId: string, componentId?: string) => {
  const res = await apiClient.get('/alternatives', {
    params: { company_id: companyId, component_id: componentId },
  })
  return res.data
}
