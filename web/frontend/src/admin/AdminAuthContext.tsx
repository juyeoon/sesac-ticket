import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { refreshAdminAccessToken, setAdminAccessToken } from '../api/adminClient'
import { adminApi } from '../pages/admin/adminApi'

interface AdminAuthContextValue {
  /** 새로고침 후 refreshToken으로 복원된 세션은 실제 백엔드에 admin "whoami" API가 없어 null로 남는다 */
  adminId: string | null
  isAdminAuthenticated: boolean
  isInitializing: boolean
  login: (adminId: string, password: string) => Promise<void>
  logout: () => void
}

const AdminAuthContext = createContext<AdminAuthContextValue | null>(null)

/**
 * 일반 회원 인증(`AuthContext`)과 완전히 분리된 관리자 전용 인증 상태.
 * 실 백엔드도 관리자 refresh 쿠키(`adminRefreshToken`)를 회원용(`refreshToken`)과 별도 경로로 분리해서 관리한다.
 */
export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [adminId, setAdminId] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)

  const login = useCallback(async (id: string, password: string) => {
    const { accessToken } = await adminApi.login(id, password)
    setAdminAccessToken(accessToken)
    setAdminId(id)
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(() => {
    setAdminAccessToken(null)
    setAdminId(null)
    setIsAuthenticated(false)
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      const restored = await refreshAdminAccessToken()
      if (!cancelled) {
        setIsAuthenticated(restored)
        setIsInitializing(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <AdminAuthContext.Provider
      value={{ adminId, isAdminAuthenticated: isAuthenticated, isInitializing, login, logout }}
    >
      {children}
    </AdminAuthContext.Provider>
  )
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext)
  if (!ctx) throw new Error('useAdminAuth는 AdminAuthProvider 하위에서만 사용할 수 있습니다.')
  return ctx
}
