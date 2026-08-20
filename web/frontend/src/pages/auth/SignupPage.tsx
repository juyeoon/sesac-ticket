import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Alert, Button, Link as MuiLink, Stack, TextField, Typography } from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { AuthCard } from '../../components/auth/AuthCard'
import { PasswordField } from '../../components/common/PasswordField'
import { ApiError } from '../../api/client'
import { authApi } from './authApi'
import { signupSchema, type SignupFormValues } from './authSchemas'

export default function SignupPage() {
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({ resolver: zodResolver(signupSchema) })

  const onSubmit = async (values: SignupFormValues) => {
    setFormError(null)
    try {
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
