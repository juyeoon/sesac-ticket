import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Stack,
  Typography,
} from '@mui/material'
import dayjs from 'dayjs'
import { Link as RouterLink, useParams } from 'react-router-dom'
import { reservationApi } from './reservationApi'

const STATUS_LABEL: Record<string, string> = {
  PENDING_PAYMENT: '입금 대기중',
  CONFIRMED: '예매 확정',
  CANCELLED: '예매 취소',
  EXPIRED: '기한 만료',
}

export default function ReservationConfirmPage() {
  const { reservationId } = useParams()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['reservation', reservationId],
    queryFn: () => reservationApi.getBankTransfer(Number(reservationId)),
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (isError || !data) {
    return (
      <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
        <Typography color="error">예매 내역을 불러오지 못했습니다.</Typography>
      </Container>
    )
  }

  return (
    <Container maxWidth="sm" sx={{ py: 5 }}>
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <Chip label={STATUS_LABEL[data.status] ?? data.status} color="primary" />
      </Stack>
      <Typography variant="h3" sx={{ mb: 0.5 }}>
        예매가 접수됐어요
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        예매번호 {data.reservationId}
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 1 }}>
            {data.performance?.title}
          </Typography>
          {data.schedule && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {dayjs(data.schedule.date).format('YYYY.MM.DD (ddd)')} {data.schedule.time}
            </Typography>
          )}
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', rowGap: 1 }}>
            {data.seats.map((s) => (
              <Chip key={s.seatId} size="small" label={`${s.grade ?? ''} ${s.row ?? ''}열 ${s.number ?? ''}번`} />
            ))}
          </Stack>
        </CardContent>
      </Card>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>
            입금 안내
          </Typography>
          <Stack spacing={1.25}>
            <InfoRow label="입금 계좌" value={data.bankAccountInfo} />
            <InfoRow label="입금자명" value={data.depositorName} />
            <Divider />
            <InfoRow label="입금 기한" value={dayjs(data.paymentDueAt).format('YYYY.MM.DD HH:mm')} emphasize />
          </Stack>
        </CardContent>
      </Card>

      <Stack direction="row" spacing={1.5}>
        <Button component={RouterLink} to="/mypage/reservations" variant="outlined" fullWidth>
          내 예매 목록
        </Button>
        <Button component={RouterLink} to="/" variant="contained" fullWidth>
          홈으로
        </Button>
      </Stack>
    </Container>
  )
}

function InfoRow({ label, value, emphasize }: { label: string; value: string; emphasize?: boolean }) {
  return (
    <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: emphasize ? 700 : 500 }}>
        {value}
      </Typography>
    </Stack>
  )
}
