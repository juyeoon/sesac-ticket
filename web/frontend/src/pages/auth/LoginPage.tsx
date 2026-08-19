import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Alert, Button, Link as MuiLink, Stack, TextField, Typography } from '@mui/material'
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import { AuthCard } from '../../components/auth/AuthCard'
import { PasswordField } from '../../components/common/PasswordField'
import { useAuth } from '../../auth/AuthContext'
import { ApiError } from '../../api/client'
import { loginSchema, type LoginFormValues } from './authSchemas'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) })

  const onSubmit = async (values: LoginFormValues) => {
    setFormError(null)
    try {
      await login(values.email, values.password)
      const from = (location.state as { from?: { pathname: string; search?: string } })?.from
      navigate(from ? `${from.pathname}${from.search ?? ''}` : '/', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '로그인에 실패했습니다.')
    }
  }

  return (
    <AuthCard
      title="처음 오셨나요?"
      description="이메일로 로그인하여 서비스를 이용하세요."
      footer={
        <Typography variant="body2">
          계정이 없으신가요?{' '}
          <MuiLink component={RouterLink} to="/signup" underline="always">
            계정 만들기
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
        <PasswordField
          label="비밀번호"
          placeholder="비밀번호를 입력해주세요"
          fullWidth
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password?.message}
        />

        <MuiLink component={RouterLink} to="/password/reset" variant="body2" sx={{ alignSelf: 'flex-end' }}>
          비밀번호를 잊으셨나요?
        </MuiLink>

        <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
          로그인
        </Button>
      </Stack>
    </AuthCard>
  )
}
