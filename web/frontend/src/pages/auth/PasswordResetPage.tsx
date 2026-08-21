import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Alert, Button, Stack, TextField } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { AuthCard } from '../../components/auth/AuthCard'
import { SendCodeButton } from '../../components/auth/SendCodeButton'
import { PasswordField } from '../../components/common/PasswordField'
import { ApiError } from '../../api/client'
import { authApi } from './authApi'
import { passwordResetSchema, type PasswordResetFormValues } from './authSchemas'

export default function PasswordResetPage() {
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)
  const [codeSent, setCodeSent] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<PasswordResetFormValues>({ resolver: zodResolver(passwordResetSchema) })

  const email = watch('email')
  const emailLooksValid = !!email && !errors.email

  const onSubmit = async (values: PasswordResetFormValues) => {
    setFormError(null)
    try {
      // 실제로는 6자리 코드가 아니라 이메일로 발송되는 긴 재설정 토큰(resetToken)을 그대로 붙여넣는 필드
      await authApi.resetPassword(values.verificationCode, values.newPassword)
      navigate('/login', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '비밀번호 재설정에 실패했습니다.')
    }
  }

  return (
    <AuthCard title="비밀번호를 잊으셨나요?" description="가입하신 이메일로 인증번호를 받아 비밀번호를 재설정해주세요.">
      <Stack component="form" spacing={2.5} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert severity="error">{formError}</Alert>}

        <TextField
          label="이메일 주소"
          placeholder="example@example.com"
          fullWidth
          {...register('email')}
          error={!!errors.email}
          helperText={errors.email?.message}
        />

        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
          <TextField
            label="재설정 토큰"
            placeholder="이메일로 전송된 재설정 토큰을 붙여넣어주세요"
            fullWidth
            {...register('verificationCode')}
            error={!!errors.verificationCode}
            helperText={errors.verificationCode?.message}
          />
          <SendCodeButton
            disabled={!emailLooksValid}
            onSend={async () => {
              await authApi.requestPasswordReset(email)
              setCodeSent(true)
            }}
          />
        </Stack>
        {codeSent && (
          <Alert severity="success" variant="outlined">
            재설정 토큰을 이메일로 전송했어요.
          </Alert>
        )}

        <PasswordField
          label="새 비밀번호"
          placeholder="8자리 이상의 영문, 숫자 조합"
          fullWidth
          {...register('newPassword')}
          error={!!errors.newPassword}
          helperText={errors.newPassword?.message}
        />
        <PasswordField
          label="새 비밀번호 확인"
          placeholder="8자리 이상의 영문, 숫자 조합"
          fullWidth
          {...register('newPasswordConfirm')}
          error={!!errors.newPasswordConfirm}
          helperText={errors.newPasswordConfirm?.message}
        />

        <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
          비밀번호 재설정
        </Button>
      </Stack>
    </AuthCard>
  )
}
