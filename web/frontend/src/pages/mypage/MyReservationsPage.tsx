import { useQuery } from '@tanstack/react-query'
import { Box, Card, CardContent, Chip, CircularProgress, Stack, Typography } from '@mui/material'
import dayjs from 'dayjs'
import { Link as RouterLink } from 'react-router-dom'
import { reservationsApi } from './reservationsApi'

const STATUS_LABEL: Record<string, string> = {
  PENDING_PAYMENT: '입금 대기중',
  CONFIRMED: '예매 확정',
  CANCELLED: '예매 취소',
  EXPIRED: '기한 만료',
}

export default function MyReservationsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['my-reservations'],
    queryFn: reservationsApi.list,
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (isError) {
    return (
      <Typography color="error" sx={{ py: 8, textAlign: 'center' }}>
        예매 목록을 불러오지 못했습니다.
      </Typography>
    )
  }

  const content = data?.content ?? []

  if (content.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
        아직 예매한 공연이 없어요.
      </Typography>
    )
  }

  return (
    <Stack spacing={2}>
      {content.map((r) => (
        <Card
          key={r.reservationId}
          component={RouterLink}
          to={`/reservations/bank-transfer/${r.reservationId}`}
          sx={{
            display: 'block',
            textDecoration: 'none',
            color: 'inherit',
            transition: 'border-color 0.15s ease',
            '&:hover': { borderColor: 'text.primary' },
          }}
        >
          <CardContent>
            <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
              <Stack spacing={0.5}>
                <Typography variant="h6">{r.performanceTitle}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {r.date ? dayjs(r.date).format('YYYY.MM.DD (ddd)') : ''} · 예매번호 {r.reservationId}
                </Typography>
              </Stack>
              <Chip
                label={STATUS_LABEL[r.status] ?? r.status}
                color={r.status === 'CONFIRMED' ? 'primary' : undefined}
                variant={r.status === 'CONFIRMED' ? 'filled' : 'outlined'}
              />
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Stack>
  )
}
