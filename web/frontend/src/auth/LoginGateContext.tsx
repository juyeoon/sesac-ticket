import { createContext, useContext, useState, type ReactNode } from 'react'
import { LoginRequiredModal } from './LoginRequiredModal'

interface LoginGateContextValue {
  promptLogin: () => void
}

const LoginGateContext = createContext<LoginGateContextValue | null>(null)

export function LoginGateProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)

  return (
    <LoginGateContext.Provider value={{ promptLogin: () => setOpen(true) }}>
      {children}
      <LoginRequiredModal open={open} onClose={() => setOpen(false)} />
    </LoginGateContext.Provider>
  )
}

export function useLoginGate() {
  const ctx = useContext(LoginGateContext)
  if (!ctx) throw new Error('useLoginGate는 LoginGateProvider 하위에서만 사용할 수 있습니다.')
  return ctx
}
