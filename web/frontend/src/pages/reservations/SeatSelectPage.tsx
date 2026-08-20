import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Paper,
  Snackbar,
  Stack,
  Typography,
} from '@mui/material'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { SeatGrid, type MergedSeat } from '../../components/reservations/SeatGrid'
import { SeatLegend } from '../../components/reservations/SeatLegend'
import { SeatGradeLegend } from '../../components/reservations/SeatGradeLegend'
import { buildGradeColorMap, getGradeColor } from '../../components/reservations/gradeColor'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'
import { PlaceholderImage } from '../../components/common/PlaceholderImage'
import { seatApi } from './seatApi'
import { performanceApi } from '../performances/performanceApi'
import { queueApi } from '../queue/queueApi'
import { getValidQueueContext, type QueueContext } from '../queue/entryTicketStorage'
import { useHoldCountdown, formatCountdown } from './useHoldCountdown'

const MAX_SEATS = 2

interface LocationState {
  performanceId?: number
  performanceTitle?: string
  venueId?: number
}

export default function SeatSelectPage() {
  const { scheduleId: scheduleIdParam } = useParams()
  const scheduleId = Number(scheduleIdParam)
  const location = useLocation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const locState = (location.state as LocationState | null) ?? null

  const [context, setContext] = useState<QueueContext | 'checking'>('checking')
  const [selectedSeatIds, setSelectedSeatIds] = useState<number[]>([])
  const [holdId, setHoldId] = useState<string | null>(null)
  const [limitAlertOpen, setLimitAlertOpen] = useState(false)
  const [recoverFailed, setRecoverFailed] = useState(false)

  interface QueueEntryVars {
    performanceId: number
    performanceTitle: string
    venueId: number
  }

  const enterQueueMutation = useMutation({
    mutationFn: (vars: QueueEntryVars) => queueApi.enter(vars.performanceId, scheduleId),
    onSuccess: (res, vars) => {
      navigate(`/queue/${res.queueToken}`, {
        replace: true,
        state: {
          scheduleId,
          performanceId: vars.performanceId,
          performanceTitle: vars.performanceTitle,
          venueId: vars.venueId,
        },
      })
    },
  })

  useEffect(() => {
    let cancelled = false

    async function init() {
      const cached = getValidQueueContext(scheduleId)
      if (cached) {
        setContext(cached)
        return
      }
      if (locState?.performanceId && locState.venueId) {
        enterQueueMutation.mutate({
          performanceId: locState.performanceId,
          performanceTitle: locState.performanceTitle ?? '',
          venueId: locState.venueId,
        })
        return
      }
      // 새로고침 등으로 라우터 state가 사라진 경우, 회차→공연 역참조 API로 복구해서 대기열에 새로 진입한다.
      try {
        const backref = await performanceApi.scheduleBackref(scheduleId)
        if (cancelled) return
        enterQueueMutation.mutate({
          performanceId: backref.performanceId,
          performanceTitle: backref.performanceTitle,
          venueId: backref.venueId,
        })
      } catch {
        if (!cancelled) setRecoverFailed(true)
      }
    }

    init()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scheduleId])

  const { data: venueSeatMap } = useQuery({
    queryKey: ['venue-seat-map', context && context !== 'checking' ? context.venueId : null],
    queryFn: () => seatApi.venueSeatMap((context as QueueContext).venueId),
    enabled: !!context && context !== 'checking',
  })
  const { data: scheduleSeats } = useQuery({
    queryKey: ['schedule-seats', scheduleId],
    queryFn: () => seatApi.scheduleSeats(scheduleId),
    enabled: !!context && context !== 'checking',
  })
  const { data: performance } = useQuery({
    queryKey: ['performance', context && context !== 'checking' ? context.performanceId : null],
    queryFn: () => performanceApi.detail((context as QueueContext).performanceId),
    enabled: !!context && context !== 'checking',
  })

  const mergedSeats: MergedSeat[] = useMemo(() => {
    if (!venueSeatMap || !scheduleSeats) return []
    const statusBySeatId = new Map(scheduleSeats.map((s) => [s.seatId, s.status]))
    return venueSeatMap.sections
      .flatMap((s) => s.seats)
      .map((seat) => ({
        seatId: seat.seatId,
        x: seat.x,
        y: seat.y,
        row: seat.row,
        number: seat.number,
        grade: seat.grade,
        status: statusBySeatId.get(seat.seatId) ?? 'AVAILABLE',
      }))
  }, [venueSeatMap, scheduleSeats])

  const priceByGrade = useMemo(() => {
    const map = new Map<string, number>()
    for (const g of performance?.seatGrades ?? []) map.set(g.grade, g.price)
    return map
  }, [performance])

  const gradeColors = useMemo(() => buildGradeColorMap(performance?.seatGrades ?? []), [performance])

  const selectedSeats = mergedSeats.filter((s) => selectedSeatIds.includes(s.seatId))
  const totalPrice = selectedSeats.reduce((sum, s) => sum + (priceByGrade.get(s.grade) ?? 0), 0)

  const holdMutation = useMutation({
    mutationFn: () => seatApi.createHold(scheduleId, selectedSeatIds, (context as QueueContext).ticket),
    onSuccess: (res) => setHoldId(res.holdId),
  })

  const releaseMutation = useMutation({
    mutationFn: () => seatApi.releaseHold(holdId!),
    onSuccess: () => {
      setHoldId(null)
      setSelectedSeatIds([])
      queryClient.invalidateQueries({ queryKey: ['schedule-seats', scheduleId] })
    },
  })

  const { remainingSeconds, expired } = useHoldCountdown(holdId)

  useEffect(() => {
    if (expired && holdId) {
      setHoldId(null)
      setSelectedSeatIds([])
      queryClient.invalidateQueries({ queryKey: ['schedule-seats', scheduleId] })
    }
  }, [expired, holdId, queryClient, scheduleId])

  const toggleSeat = (seatId: number) => {
    setSelectedSeatIds((prev) => {
      if (prev.includes(seatId)) return prev.filter((id) => id !== seatId)
      if (prev.length >= MAX_SEATS) {
        setLimitAlertOpen(true)
        return prev
      }
      return [...prev, seatId]
    })
  }

  const handleProceedToPayment = () => {
    navigate('/reservations/bank-transfer/new', {
      state: {
        holdId,
        performanceId: context !== 'checking' ? (context as QueueContext).performanceId : undefined,
        performanceTitle: performance?.title,
        scheduleId,
        seats: selectedSeats.map((s) => ({ seatId: s.seatId, grade: s.grade, row: s.row, number: s.number })),
        totalPrice,
      },
    })
  }

  if (recoverFailed) {
    return (
      <CenteredMessagePage
        eyebrow="좌석 선택"
        title="다시 선택해주세요"
        description="회차 정보를 찾을 수 없어요. 공연 상세 페이지에서 회차를 다시 선택해주세요."
      />
    )
  }

  if (context === 'checking' || enterQueueMutation.isPending) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="md" sx={{ py: 5, pb: 16 }}>
      <Stack direction="row" spacing={2} sx={{ alignItems: 'center', mb: 4 }}>
        <Box sx={{ width: 64, flexShrink: 0 }}>
          <PlaceholderImage seed={String(context.performanceId)} aspectRatio="1 / 1" />
        </Box>
        <Box>
          <Typography variant="overline" color="text.secondary">
            좌석 선택
          </Typography>
          <Typography variant="h4">{performance?.title ?? context.performanceTitle}</Typography>
          {performance && (
            <Typography variant="body2" color="text.secondary">
              {performance.venue.name}
            </Typography>
          )}
        </Box>
      </Stack>

      <Stack spacing={1.5} sx={{ mb: 3 }}>
        <SeatGradeLegend seatGrades={performance?.seatGrades ?? []} gradeColors={gradeColors} />
        <SeatLegend />
      </Stack>

      <Box sx={{ p: { xs: 1.5, sm: 3 }, borderRadius: '20px', border: 1, borderColor: 'grey.100' }}>
        {mergedSeats.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <SeatGrid seats={mergedSeats} selectedSeatIds={selectedSeatIds} onToggle={toggleSeat} gradeColors={gradeColors} />
        )}
      </Box>

      <Paper
        sx={{
          position: 'fixed',
          left: 0,
          right: 0,
          bottom: 0,
          borderRadius: 0,
          borderTop: 1,
          borderColor: 'divider',
          boxShadow: '0 -8px 24px -12px rgba(33,33,33,0.18)',
          py: 2,
        }}
        elevation={0}
      >
        <Container maxWidth="md">
          {!holdId ? (
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: { sm: 'center' } }}>
              <Box sx={{ flex: 1 }}>
                {selectedSeats.length === 0 ? (
                  <Typography color="text.secondary">좌석을 선택해주세요 (최대 {MAX_SEATS}석)</Typography>
                ) : (
                  <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', rowGap: 1 }}>
                    {selectedSeats.map((s) => {
                      const color = getGradeColor(gradeColors, s.grade)
                      return (
                        <Chip
                          key={s.seatId}
                          label={`${s.grade} ${s.row}열 ${s.number}번`}
                          sx={{ bgcolor: color.soft, color: color.main, fontWeight: 600 }}
                        />
                      )
                    })}
                  </Stack>
                )}
              </Box>
              <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
                <Typography variant="h6">{totalPrice.toLocaleString()}원</Typography>
                <Button
                  variant="contained"
                  size="large"
                  disabled={selectedSeats.length === 0 || holdMutation.isPending}
                  onClick={() => holdMutation.mutate()}
                >
                  선점하기
                </Button>
              </Stack>
            </Stack>
          ) : (
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: { sm: 'center' } }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  선점 완료 · 남은 시간{' '}
                  <Box component="span" sx={{ fontWeight: 700, color: 'error.main' }}>
                    {remainingSeconds !== null ? formatCountdown(remainingSeconds) : '--:--'}
                  </Box>
                </Typography>
                <Typography variant="h6">{totalPrice.toLocaleString()}원</Typography>
              </Box>
              <Stack direction="row" spacing={1.5}>
                <Button variant="outlined" onClick={() => releaseMutation.mutate()} disabled={releaseMutation.isPending}>
                  선택 취소
                </Button>
                <Button variant="contained" size="large" onClick={handleProceedToPayment}>
                  예매하기
                </Button>
              </Stack>
            </Stack>
          )}
        </Container>
      </Paper>

      {holdMutation.isError && (
        <Alert severity="error" sx={{ position: 'fixed', bottom: 90, left: 16, right: 16, maxWidth: 448, mx: 'auto' }}>
          이미 다른 사람이 선점했거나 판매된 좌석이 있어요. 다시 선택해주세요.
        </Alert>
      )}

      <Snackbar
        open={limitAlertOpen}
        autoHideDuration={2500}
        onClose={() => setLimitAlertOpen(false)}
        message={`최대 ${MAX_SEATS}석까지 선택할 수 있어요.`}
      />
    </Container>
  )
}
