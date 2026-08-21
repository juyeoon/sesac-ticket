import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'
import { useAdminAuth } from '../../admin/AdminAuthContext'
import { ApiError } from '../../api/client'
import { adminApi } from './adminApi'

export default function AdminHomePage() {
  const { adminId, isAdminAuthenticated, isInitializing, logout } = useAdminAuth()
  const navigate = useNavigate()
  const [reservationIdInput, setReservationIdInput] = useState('')

  const confirmMutation = useMutation({
    mutationFn: (reservationId: number) => adminApi.confirmBankTransfer(reservationId),
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

  const handleConfirm = () => {
    const reservationId = Number(reservationIdInput)
    if (!reservationIdInput || Number.isNaN(reservationId)) return
    confirmMutation.mutate(reservationId)
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: '60vh', py: 6, display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="overline" color="text.secondary">
            관리자
          </Typography>
          <Typography variant="h4">{adminId ? `${adminId}님 환영합니다` : '관리자님 환영합니다'}</Typography>
        </Box>

        <Paper variant="outlined" sx={{ p: 3 }}>
          <Stack spacing={2}>
            <Typography variant="h6">무통장입금 예매 확정</Typography>
            <Typography variant="body2" color="text.secondary">
              입금 확인 후 예매번호를 입력해 확정하세요. 확정하면 좌석 상태가 &quot;입금대기중&quot;에서
              &quot;예매 완료&quot;로 바뀝니다.
            </Typography>

            <TextField
              label="예매번호"
              placeholder="예: 4"
              value={reservationIdInput}
              onChange={(e) => setReservationIdInput(e.target.value.replace(/[^0-9]/g, ''))}
              fullWidth
            />

            <Button
              variant="contained"
              size="large"
              disabled={!reservationIdInput || confirmMutation.isPending}
              onClick={handleConfirm}
            >
              확정하기
            </Button>

            {confirmMutation.isSuccess && (
              <Alert severity="success">
                예매번호 {confirmMutation.data.reservationId} 확정 완료 ({confirmMutation.data.status})
              </Alert>
            )}
            {confirmMutation.isError && (
              <Alert severity="error">
                {confirmMutation.error instanceof ApiError
                  ? confirmMutation.error.message
                  : '확정에 실패했습니다.'}
              </Alert>
            )}
          </Stack>
        </Paper>

        <Divider />

        <Box sx={{ textAlign: 'center' }}>
          <Button
            variant="outlined"
            onClick={() => {
              logout()
              navigate('/admin/login', { replace: true })
            }}
          >
            로그아웃
          </Button>
        </Box>
      </Box>
    </Container>
  )
}
