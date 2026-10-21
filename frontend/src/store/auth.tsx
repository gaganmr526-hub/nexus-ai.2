import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { getMe } from '@/api/auth'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('nexustrace_token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => {
          setToken(null)
          localStorage.removeItem('nexustrace_token')
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [token])

  const login = async (newToken: string) => {
    localStorage.setItem('nexustrace_token', newToken)
    setToken(newToken)
    const me = await getMe()
    setUser(me)
  }

  const logout = () => {
    localStorage.removeItem('nexustrace_token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
