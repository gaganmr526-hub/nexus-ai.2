import { apiClient } from './client'
import type { User } from '@/types'

export const login = async (email: string, password: string) => {
  const res = await apiClient.post<{ access_token: string; token_type: string }>(
    '/auth/login',
    { email, password }
  )
  return res.data
}

export const getMe = async () => {
  const res = await apiClient.get<User>('/auth/me')
  return res.data
}

export const register = async (data: { email: string; password: string; full_name: string }) => {
  const res = await apiClient.post<User>('/auth/register', data)
  return res.data
}
