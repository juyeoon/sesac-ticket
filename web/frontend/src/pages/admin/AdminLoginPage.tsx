import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Alert, Button, Stack, TextField } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { AuthCard } from '../../components/auth/AuthCard'
import { PasswordField } from '../../components/common/PasswordField'
import { ApiError } from '../../api/client'
import { useAdminAuth } from '../../admin/AdminAuthContext'

const schema = z.object({
  adminId: z.string().min(1, '관리자 ID를 입력해주세요.'),
  password: z.string().min(1, '비밀번호를 입력해주세요.'),
})
type FormValues = z.infer<typeof schema>

export default function AdminLoginPage() {
  const { login } = useAdminAuth()
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      await login(values.adminId, values.password)
      navigate('/admin', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '로그인에 실패했습니다.')
    }
  }

  return (
    <AuthCard title="관리자 로그인" description="관리자 계정으로 로그인하세요.">
      <Stack component="form" spacing={2.5} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert severity="error">{formError}</Alert>}

        <TextField
          label="관리자 ID"
          fullWidth
          {...register('adminId')}
          error={!!errors.adminId}
          helperText={errors.adminId?.message}
        />
        <PasswordField
          label="비밀번호"
          fullWidth
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password?.message}
        />

        <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
          로그인
        </Button>
      </Stack>
    </AuthCard>
  )
}
