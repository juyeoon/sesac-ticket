import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, refreshAccessToken, setAccessToken } from '../api/client'

export interface AuthUser {
  id: number
  email: string
  nickname: string
  gender?: string
  ageRange?: string
  status: string
  emailVerified: boolean
}

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  /** 앱 시작 시 refreshToken 쿠키로 로그인 상태 복원을 시도하는 동안 true */
  isInitializing: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isInitializing, setIsInitializing] = useState(true)

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

  // 새로고침 시 accessToken은 메모리에서 사라지지만, refreshToken은 HttpOnly 쿠키로 남아있으므로
  // 앱 시작 시 한 번 재발급을 시도해 로그인 상태를 복원한다.
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      const restored = await refreshAccessToken()
      if (restored && !cancelled) {
        await refreshMe().catch(() => setAccessToken(null))
      }
      if (!cancelled) setIsInitializing(false)
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isInitializing, login, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth는 AuthProvider 하위에서만 사용할 수 있습니다.')
  return ctx
}
