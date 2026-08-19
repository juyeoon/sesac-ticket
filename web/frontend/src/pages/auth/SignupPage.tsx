import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Alert, Button, Link as MuiLink, Stack, TextField, Typography } from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { AuthCard } from '../../components/auth/AuthCard'
import { SendCodeButton } from '../../components/auth/SendCodeButton'
import { PasswordField } from '../../components/common/PasswordField'
import { ApiError } from '../../api/client'
import { authApi } from './authApi'
import { signupSchema, type SignupFormValues } from './authSchemas'

export default function SignupPage() {
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)
  const [codeSent, setCodeSent] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({ resolver: zodResolver(signupSchema) })

  const email = watch('email')
  const emailLooksValid = !!email && !errors.email

  const onSubmit = async (values: SignupFormValues) => {
    setFormError(null)
    try {
      const { verified } = await authApi.verifyEmail(values.email, values.verificationCode)
      if (!verified) {
        setFormError('인증번호가 올바르지 않습니다.')
        return
      }
      await authApi.signup(values.email, values.password, values.nickname)
      navigate('/login', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '회원가입에 실패했습니다.')
    }
  }

  return (
    <AuthCard
      title="처음 오셨나요?"
      description="이메일로 가입하여 서비스를 이용하세요."
      footer={
        <Typography variant="body2">
          이미 계정이 있으신가요?{' '}
          <MuiLink component={RouterLink} to="/login" underline="always">
            로그인하기
          </MuiLink>
        </Typography>
      }
    >
      <Stack component="form" spacing={2.5} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert severity="error">{formError}</Alert>}

        <TextField
          label="이메일"
          placeholder="example@example.com"
          fullWidth
          {...register('email')}
          error={!!errors.email}
          helperText={errors.email?.message}
        />

        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
          <TextField
            label="인증번호"
            placeholder="이메일로 전송된 인증 코드를 입력해주세요"
            fullWidth
            {...register('verificationCode')}
            error={!!errors.verificationCode}
            helperText={errors.verificationCode?.message}
          />
          <SendCodeButton
            disabled={!emailLooksValid}
            onSend={async () => {
              await authApi.requestEmailVerification(email)
              setCodeSent(true)
            }}
          />
        </Stack>
        {codeSent && (
          <Alert severity="success" variant="outlined">
            인증 코드를 전송했어요. (개발 중에는 브라우저 콘솔에서 코드를 확인할 수 있어요)
          </Alert>
        )}

        <TextField
          label="닉네임"
          placeholder="2~20자로 입력해주세요"
          fullWidth
          {...register('nickname')}
          error={!!errors.nickname}
          helperText={errors.nickname?.message}
        />
        <PasswordField
          label="비밀번호"
          placeholder="8자리 이상의 영문, 숫자 조합"
          fullWidth
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password?.message}
        />
        <PasswordField
          label="비밀번호 확인"
          placeholder="8자리 이상의 영문, 숫자 조합"
          fullWidth
          {...register('passwordConfirm')}
          error={!!errors.passwordConfirm}
          helperText={errors.passwordConfirm?.message}
        />

        <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
          회원가입
        </Button>
      </Stack>
    </AuthCard>
  )
}
