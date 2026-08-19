import { useCallback } from 'react'
import { useAuth } from './AuthContext'
import { useLoginGate } from './LoginGateContext'

/** 로그인 상태면 action을 바로 실행하고, 아니면 로그인 유도 모달을 띄운다. */
export function useRequireAuth() {
  const { isAuthenticated } = useAuth()
  const { promptLogin } = useLoginGate()

  return useCallback(
    (action: () => void) => {
      if (isAuthenticated) action()
      else promptLogin()
    },
    [isAuthenticated, promptLogin],
  )
}
