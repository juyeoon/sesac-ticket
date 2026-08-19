import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
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
import dayjs from 'dayjs'
import { useNavigate, useParams } from 'react-router-dom'
import { performanceApi, type Schedule } from './performanceApi'

function isSoldOut(schedule: Schedule) {
  return schedule.seatGrades.every((g) => (g.remaining ?? 0) <= 0)
}

export default function ScheduleSelectPage() {
  const { performanceId } = useParams()
  const id = Number(performanceId)
  const navigate = useNavigate()

  const { data: performance } = useQuery({
    queryKey: ['performance', id],
    queryFn: () => performanceApi.detail(id),
  })
  const { data: schedules, isLoading } = useQuery({
    queryKey: ['schedules', id],
    queryFn: () => performanceApi.schedules(id),
  })

  const grouped = useMemo(() => {
    const map = new Map<string, Schedule[]>()
    for (const s of schedules ?? []) {
      const list = map.get(s.date) ?? []
      list.push(s)
      map.set(s.date, list)
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b))
  }, [schedules])

  return (
    <Container maxWidth="sm" sx={{ py: 5 }}>
      <Typography variant="overline" color="text.secondary">
        회차 선택
      </Typography>
      <Typography variant="h3" sx={{ mb: 4 }}>
        {performance?.title ?? '공연'}
      </Typography>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      <Stack spacing={3}>
        {grouped.map(([date, items]) => (
          <Box key={date}>
            <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
              {dayjs(date).format('YYYY.MM.DD (ddd)')}
            </Typography>
            <Stack spacing={1.5}>
              {items.map((schedule) => {
                const soldOut = isSoldOut(schedule)
                return (
                  <Card key={schedule.scheduleId} variant="outlined">
                    <CardContent
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 2,
                        flexWrap: 'wrap',
                      }}
                    >
                      <Box>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 0.5 }}>
                          {schedule.time}
                        </Typography>
                        <Stack direction="row" spacing={0.75} sx={{ flexWrap: 'wrap' }}>
                          {schedule.seatGrades.map((g) => (
                            <Chip
                              key={g.grade}
                              size="small"
                              variant="outlined"
                              label={`${g.grade} ${g.price.toLocaleString()}원 · 잔여 ${g.remaining ?? 0}`}
                            />
                          ))}
                        </Stack>
                      </Box>
                      <Button
                        variant={soldOut ? 'outlined' : 'contained'}
                        disabled={soldOut}
                        onClick={() =>
                          navigate(`/schedules/${schedule.scheduleId}/seats`, {
                            state: {
                              performanceId: id,
                              performanceTitle: performance?.title ?? '',
                              venueId: performance?.venue.id,
                            },
                          })
                        }
                      >
                        {soldOut ? '매진' : '선택'}
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </Stack>
          </Box>
        ))}
      </Stack>
    </Container>
  )
}
