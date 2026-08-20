import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'
import { adminApi } from '../pages/admin/adminApi'

interface AdminAuthContextValue {
  adminId: string | null
  isAdminAuthenticated: boolean
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

  const login = useCallback(async (id: string, password: string) => {
    await adminApi.login(id, password)
    setAdminId(id)
  }, [])

  const logout = useCallback(() => setAdminId(null), [])

  return (
    <AdminAuthContext.Provider value={{ adminId, isAdminAuthenticated: !!adminId, login, logout }}>
      {children}
    </AdminAuthContext.Provider>
  )
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext)
  if (!ctx) throw new Error('useAdminAuth는 AdminAuthProvider 하위에서만 사용할 수 있습니다.')
  return ctx
}
