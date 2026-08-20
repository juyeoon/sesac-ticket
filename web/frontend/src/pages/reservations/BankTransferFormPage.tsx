import { useEffect, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'
import { reservationApi } from './reservationApi'
import { useHoldCountdown, formatCountdown } from './useHoldCountdown'
import { ApiError } from '../../api/client'

const schema = z.object({
  depositorName: z.string().min(2, '2자 이상 입력해주세요.'),
})
type FormValues = z.infer<typeof schema>

interface LocationState {
  holdId: string
  performanceId: number
  performanceTitle: string
  scheduleId: number
  seats: { seatId: number; grade: string; row: string; number: number }[]
  totalPrice: number
}

export default function BankTransferFormPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null
  const [formError, setFormError] = useState<string | null>(null)

  const { remainingSeconds, expired } = useHoldCountdown(state?.holdId ?? null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const createMutation = useMutation({
    mutationFn: (depositorName: string) => reservationApi.createBankTransfer(state!.holdId, depositorName),
    onSuccess: (res) => navigate(`/reservations/bank-transfer/${res.reservationId}`, { replace: true }),
  })

  useEffect(() => {
    if (expired && state) {
      navigate(`/schedules/${state.scheduleId}/seats`, { replace: true });
    }
  }, [expired, state, navigate])

  if (!state) {
    return (
      <CenteredMessagePage
        eyebrow="예매"
        title="선택된 좌석 정보가 없어요"
        description="공연 상세 페이지에서 좌석 선택부터 다시 진행해주세요."
      />
    )
  }

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      await createMutation.mutateAsync(values.depositorName)
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : '예매 생성에 실패했습니다.')
    }
  }

  return (
    <Container maxWidth="sm" sx={{ py: 5 }}>
      <Typography variant="overline" color="text.secondary">
        무통장입금 예매
      </Typography>
      <Typography variant="h3" sx={{ mb: 3 }}>
        {state.performanceTitle}
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', rowGap: 1 }}>
            {state.seats.map((s) => (
              <Chip key={s.seatId} label={`${s.grade} ${s.row}열 ${s.number}번`} />
            ))}
          </Stack>
          <Divider sx={{ mb: 2 }} />
          <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
              결제 금액
            </Typography>
            <Typography variant="h6">{state.totalPrice.toLocaleString()}원</Typography>
          </Stack>
        </CardContent>
      </Card>

      <Alert severity="warning" sx={{ mb: 3 }}>
        선점 남은 시간{' '}
        <Box component="span" sx={{ fontWeight: 700 }}>
          {remainingSeconds !== null ? formatCountdown(remainingSeconds) : '--:--'}
        </Box>{' '}
        — 시간 내에 입금자명을 입력하고 예매를 완료해주세요.
      </Alert>

      <Stack component="form" spacing={2.5} onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert severity="error">{formError}</Alert>}
        <TextField
          label="입금자명"
          placeholder="실제 입금하실 분의 성함을 입력해주세요"
          fullWidth
          {...register('depositorName')}
          error={!!errors.depositorName}
          helperText={errors.depositorName?.message}
        />
        <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
          예매하기
        </Button>
      </Stack>
    </Container>
  )
}
