import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { Controller, useForm } from 'react-hook-form'
import { Alert, Button, MenuItem, Stack, TextField } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { SendCodeButton } from '../../components/auth/SendCodeButton'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { authApi } from '../auth/authApi'
import { userApi } from './userApi'
import { myInfoSchema, type MyInfoFormValues } from './myInfoSchemas'

const GENDER_OPTIONS = [
  { value: 'F', label: '여성' },
  { value: 'M', label: '남성' },
]
/** 백엔드가 나이대 값 목록을 확정해주지 않아, 흔히 쓰는 구간으로 임의 지정 — 실제 연동 시 확인 필요 */
const AGE_RANGE_OPTIONS = ['10대', '20대', '30대', '40대', '50대 이상']

export default function MyInfoEditPage() {
  const { user, refreshMe } = useAuth()
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)
  const [codeSent, setCodeSent] = useState(false)

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<MyInfoFormValues>({
    resolver: zodResolver(myInfoSchema),
    defaultValues: {
      nickname: user?.nickname ?? '',
      gender: user?.gender ?? '',
      ageRange: user?.ageRange ?? '',
      verificationCode: '',
    },
  })

  if (!user) return null

  const onSubmit = async (values: MyInfoFormValues) => {
    setFormError(null)
    try {
      await userApi.update(values)
      await refreshMe()
      navigate('/mypage', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '정보 수정에 실패했습니다.')
    }
  }

  return (
    <Stack
      component="form"
      spacing={2.5}
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ maxWidth: 480 }}
    >
      {formError && <Alert severity="error">{formError}</Alert>}

      <TextField
        label="닉네임"
        fullWidth
        {...register('nickname')}
        error={!!errors.nickname}
        helperText={errors.nickname?.message}
      />

      <Controller
        name="gender"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            select
            label="성별"
            fullWidth
            error={!!errors.gender}
            helperText={errors.gender?.message}
          >
            {GENDER_OPTIONS.map((o) => (
              <MenuItem key={o.value} value={o.value}>
                {o.label}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      <Controller
        name="ageRange"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            select
            label="나이대"
            fullWidth
            error={!!errors.ageRange}
            helperText={errors.ageRange?.message}
          >
            {AGE_RANGE_OPTIONS.map((a) => (
              <MenuItem key={a} value={a}>
                {a}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
        <TextField
          label="인증번호"
          placeholder="본인 확인을 위해 이메일로 전송된 인증번호를 입력해주세요"
          fullWidth
          {...register('verificationCode')}
          error={!!errors.verificationCode}
          helperText={errors.verificationCode?.message}
        />
        <SendCodeButton
          onSend={async () => {
            await authApi.requestEmailVerification(user.email)
            setCodeSent(true)
          }}
        />
      </Stack>
      {codeSent && (
        <Alert severity="success" variant="outlined">
          인증 코드를 전송했어요. (개발 중에는 브라우저 콘솔에서 코드를 확인할 수 있어요)
        </Alert>
      )}

      <Stack direction="row" spacing={1.5}>
        <Button variant="outlined" fullWidth onClick={() => navigate('/mypage')}>
          취소
        </Button>
        <Button type="submit" variant="contained" fullWidth disabled={isSubmitting}>
          저장
        </Button>
      </Stack>
    </Stack>
  )
}
