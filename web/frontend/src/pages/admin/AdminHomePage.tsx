import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Stack,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'
import { useAdminAuth } from '../../admin/AdminAuthContext'
import { ApiError } from '../../api/client'
import { adminApi, type AdminReservationListItem } from './adminApi'

const STATUS_LABEL: Record<string, string> = {
  PENDING_PAYMENT: '입금 대기중',
  CONFIRMED: '예매 확정',
  CANCELLED: '예매 취소',
  EXPIRED: '기한 만료',
}

const RESERVATIONS_QUERY_KEY = ['admin-reservations']

export default function AdminHomePage() {
  const { adminId, isAdminAuthenticated, isInitializing, logout } = useAdminAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    data: reservations,
    isLoading,
    isError,
  } = useQuery({
    queryKey: RESERVATIONS_QUERY_KEY,
    queryFn: adminApi.listReservations,
    enabled: isAdminAuthenticated,
  })

  const confirmMutation = useMutation({
    mutationFn: (reservationId: number) => adminApi.confirmBankTransfer(reservationId),
    onSuccess: (result) => {
      queryClient.setQueryData<AdminReservationListItem[]>(RESERVATIONS_QUERY_KEY, (prev) =>
        prev?.map((r) =>
          r.reservationId === result.reservationId
            ? { ...r, status: 'CONFIRMED', confirmedAt: result.confirmedAt }
            : r,
        ),
      )
    },
  })

  if (isInitializing) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (!isAdminAuthenticated) {
    return (
      <CenteredMessagePage
        eyebrow="관리자"
        title="로그인이 필요해요"
        description="관리자 계정으로 로그인 후 이용할 수 있어요."
        ctaHref="/admin/login"
        ctaLabel="관리자 로그인으로 이동"
      />
    )
  }

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Stack
        direction="row"
        sx={{ justifyContent: 'space-between', alignItems: 'baseline', mb: 4 }}
      >
        <Box>
          <Typography variant="overline" color="text.secondary">
            관리자
          </Typography>
          <Typography variant="h4">
            {adminId ? `${adminId}님 환영합니다` : '관리자님 환영합니다'}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          onClick={() => {
            logout()
            navigate('/admin/login', { replace: true })
          }}
        >
          로그아웃
        </Button>
      </Stack>

      <Typography variant="h6" sx={{ mb: 2 }}>
        전체 예매 목록
      </Typography>

      <Box sx={{ maxWidth: 640 }}>
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <Typography color="error" sx={{ py: 4 }}>
            예매 목록을 불러오지 못했습니다.
          </Typography>
        )}

        {!isLoading && !isError && reservations?.length === 0 && (
          <Typography color="text.secondary" sx={{ py: 4 }}>
            예매 내역이 없어요.
          </Typography>
        )}

        <Stack spacing={2}>
          {reservations?.map((r) => {
            const isConfirming =
              confirmMutation.isPending && confirmMutation.variables === r.reservationId
            const failed = confirmMutation.isError && confirmMutation.variables === r.reservationId

            return (
              <Card key={r.reservationId}>
                <CardContent>
                  <Stack
                    direction="row"
                    sx={{ justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}
                  >
                    <Stack spacing={0.5}>
                      <Typography variant="subtitle1">
                        {r.performance.title} · 예매번호 {r.reservationId}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {r.schedule.date} {r.schedule.time} · {r.member.nickname} ({r.member.email})
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        입금자명: {r.depositorName ?? '-'}
                      </Typography>
                      <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', rowGap: 1, mt: 0.5 }}>
                        {r.seats.map((s, i) => (
                          <Chip key={i} size="small" label={`${s.grade} ${s.row}열 ${s.number}번`} />
                        ))}
                      </Stack>
                    </Stack>

                    <Stack spacing={1} sx={{ alignItems: 'flex-end', flexShrink: 0 }}>
                      <Chip
                        label={STATUS_LABEL[r.status] ?? r.status}
                        color={r.status === 'CONFIRMED' ? 'primary' : undefined}
                        variant={r.status === 'CONFIRMED' ? 'filled' : 'outlined'}
                      />
                      {r.confirmedAt && (
                        <Typography variant="caption" color="text.secondary">
                          {new Date(r.confirmedAt).toLocaleString('ko-KR')} 확정
                        </Typography>
                      )}
                      {r.status === 'PENDING_PAYMENT' && (
                        <Button
                          size="small"
                          variant="contained"
                          disabled={isConfirming}
                          onClick={() => confirmMutation.mutate(r.reservationId)}
                        >
                          확인
                        </Button>
                      )}
                    </Stack>
                  </Stack>

                  {failed && (
                    <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                      {confirmMutation.error instanceof ApiError
                        ? confirmMutation.error.message
                        : '확정에 실패했습니다.'}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </Stack>
      </Box>
    </Container>
  )
}
