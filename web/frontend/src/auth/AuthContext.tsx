import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'
import { api, setAccessToken } from '../api/client'

export interface AuthUser {
  id: number
  email: string
  nickname: string
  gender?: string
  ageRange?: string
  preferredGenres: string[]
  emailVerified: boolean
}

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)

  const refreshMe = useCallback(async () => {
    const me = await api.get<AuthUser>('/users/me')
    setUser(me)
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      const { accessToken } = await api.post<{ accessToken: string }>('/auth/login', {
        email,
        password,
      })
      setAccessToken(accessToken)
      await refreshMe()
    },
    [refreshMe],
  )

  const logout = useCallback(async () => {
    await api.post('/auth/logout').catch(() => undefined)
    setAccessToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth는 AuthProvider 하위에서만 사용할 수 있습니다.')
  return ctx
}
