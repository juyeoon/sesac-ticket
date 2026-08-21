import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, CircularProgress, Container, Typography } from '@mui/material'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { queueApi } from './queueApi'
import { saveQueueContext } from './entryTicketStorage'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'

interface QueueLocationState {
  scheduleId: number
  performanceId: number
  performanceTitle: string
  venueId: number
}

export default function QueuePage() {
  const { queueToken } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as QueueLocationState | null

  const { data } = useQuery({
    queryKey: ['queue-status', queueToken],
    queryFn: () => queueApi.status(String(queueToken)),
    enabled: !!state,
    refetchInterval: (query) => (query.state.data?.status === 'READY' ? false : 3000), // 3초 폴링, 롱폴링 금지 규칙 준수
  })

  useEffect(() => {
    if (data?.status === 'READY' && data.entryTicket && state) {
      saveQueueContext(state.scheduleId, {
        ticket: data.entryTicket,
        venueId: state.venueId,
        performanceId: state.performanceId,
        performanceTitle: state.performanceTitle,
      })
      navigate(`/schedules/${state.scheduleId}/seats`, {
        replace: true,
        state: { performanceId: state.performanceId, performanceTitle: state.performanceTitle, venueId: state.venueId },
      })
    }
  }, [data, state, navigate])

  if (!state) {
    return (
      <CenteredMessagePage
        eyebrow="대기열"
        title="진행 상태를 확인할 수 없어요"
        description="공연 상세 페이지에서 다시 예매를 시작해주세요."
      />
    )
  }

  return (
    <Container maxWidth="xs" sx={{ py: 10, textAlign: 'center' }}>
      <Typography variant="overline" color="text.secondary">
        대기열
      </Typography>
      <Typography variant="h3" sx={{ mb: 1 }}>
        {state.performanceTitle}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 5 }}>
        접속량이 많아 순서대로 입장하고 있어요. 잠시만 기다려주세요.
      </Typography>

      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
        <CircularProgress size={56} thickness={3} />
      </Box>

      <Typography variant="h4" sx={{ mb: 0.5 }}>
        {data ? `${data.position}번째` : '확인 중…'}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {data ? `예상 대기시간 약 ${data.estimatedWaitSeconds}초` : ''}
      </Typography>
      <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 4 }}>
        3초마다 자동으로 순번을 확인해요. 이 화면을 벗어나지 마세요.
      </Typography>
    </Container>
  )
}
