import { apiClient } from './client'
import type { Report } from '@/types'

export const getReports = async (companyId: string) => {
  const res = await apiClient.get<Report[]>('/reports', {
    params: { company_id: companyId },
  })
  return res.data
}

export const generateReport = async (companyId: string, reportType: string) => {
  const res = await apiClient.post<Report>('/reports/generate', {
    company_id: companyId,
    report_type: reportType,
  })
  return res.data
}

export const exportReportCsv = async (reportId: string) => {
  const res = await apiClient.get(`/reports/${reportId}/export/csv`, {
    responseType: 'blob',
  })
  return res.data
}

export const exportReportJson = async (reportId: string) => {
  const res = await apiClient.get(`/reports/${reportId}/export/json`, {
    responseType: 'blob',
  })
  return res.data
}
