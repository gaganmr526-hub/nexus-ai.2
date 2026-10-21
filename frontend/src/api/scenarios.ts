import { apiClient } from './client'
import type { Scenario, ScenarioResult } from '@/types'

export const getScenarios = async (companyId: string) => {
  const res = await apiClient.get<Scenario[]>('/scenarios', {
    params: { company_id: companyId },
  })
  return res.data
}

export const getScenario = async (id: string) => {
  const res = await apiClient.get<Scenario>(`/scenarios/${id}`)
  return res.data
}

export const createScenario = async (data: Partial<Scenario>) => {
  const res = await apiClient.post<Scenario>('/scenarios', data)
  return res.data
}

export const runScenario = async (id: string) => {
  const res = await apiClient.post<ScenarioResult>(`/scenarios/${id}/run`)
  return res.data
}

export const getScenarioResult = async (scenarioId: string) => {
  const res = await apiClient.get<ScenarioResult>(`/scenarios/${scenarioId}/result`)
  return res.data
}

export const updateScenario = async (id: string, data: Partial<Scenario>) => {
  const res = await apiClient.put<Scenario>(`/scenarios/${id}`, data)
  return res.data
}

export const deleteScenario = async (id: string) => {
  await apiClient.delete(`/scenarios/${id}`)
}
