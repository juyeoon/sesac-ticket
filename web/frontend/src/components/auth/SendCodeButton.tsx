import { useState } from 'react'
import { Button } from '@mui/material'

interface SendCodeButtonProps {
  disabled?: boolean
  onSend: () => Promise<unknown>
}

/** 회원가입 / 비밀번호 재설정에서 공통으로 쓰는 "인증번호 발송" 버튼. */
export function SendCodeButton({ disabled, onSend }: SendCodeButtonProps) {
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent'>('idle')

  const handleClick = async () => {
    setStatus('sending')
    try {
      await onSend()
      setStatus('sent')
    } catch {
      setStatus('idle')
    }
  }

  return (
    <Button
      variant="outlined"
      onClick={handleClick}
      disabled={disabled || status === 'sending'}
      sx={{ whiteSpace: 'nowrap', flexShrink: 0 }}
    >
      {status === 'sent' ? '재발송' : status === 'sending' ? '전송 중…' : '인증번호 발송'}
    </Button>
  )
}
