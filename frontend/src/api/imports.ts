import { apiClient } from './client'
import type { ImportJob } from '@/types'

export const uploadImportFile = async (
  companyId: string,
  importType: string,
  file: File
) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('company_id', companyId)
  formData.append('import_type', importType)
  const res = await apiClient.post<ImportJob>('/imports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export const getImportJobs = async (companyId: string) => {
  const res = await apiClient.get<ImportJob[]>('/imports', {
    params: { company_id: companyId },
  })
  return res.data
}

export const getImportJob = async (id: string) => {
  const res = await apiClient.get<ImportJob>(`/imports/${id}`)
  return res.data
}

export const confirmImport = async (id: string) => {
  const res = await apiClient.post<ImportJob>(`/imports/${id}/confirm`)
  return res.data
}

export const downloadTemplate = async (importType: string) => {
  const res = await apiClient.get(`/imports/template/${importType}`, {
    responseType: 'blob',
  })
  return res.data
}
