import { apiClient } from './client'
import type { Notification } from '@/types'

export const getNotifications = async () => {
  const res = await apiClient.get<Notification[]>('/notifications')
  return res.data
}

export const markNotificationRead = async (id: string) => {
  const res = await apiClient.put<{ id: string; is_read: boolean }>(`/notifications/${id}/read`)
  return res.data
}

export const markAllRead = async () => {
  const res = await apiClient.put<{ marked_read: number }>('/notifications/read-all/batch')
  return res.data
}
