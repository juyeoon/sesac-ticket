import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { seatApi } from './seatApi'

/**
 * Hold 남은시간 표시용. 서버(진실)를 5초마다 재확인하면서, 화면은 1초마다 로컬로 감소시켜 부드럽게 보여준다.
 *
 * `expired`는 반드시 서버 응답(404) 기준으로만 true가 된다 — 로컬 카운트가 0에 도달한 시점과
 * 서버가 실제로 좌석을 해제하는 시점 사이에 시차가 있어서, 로컬 값만으로 만료를 판단하면
 * 화면은 "선택 모드"로 돌아갔는데 좌석은 아직 HELD로 보이는 상태가 잠깐 발생한다.
 * 대신 로컬 카운트가 0이 되는 즉시 서버 재확인을 강제로 트리거해서 그 시차를 최소화한다.
 */
export function useHoldCountdown(holdId: string | null) {
  const queryClient = useQueryClient()
  const { data, isError } = useQuery({
    queryKey: ['hold', holdId],
    queryFn: () => seatApi.getHold(holdId!),
    enabled: !!holdId,
    refetchInterval: 5000,
    retry: false,
  })

  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null)

  useEffect(() => {
    if (data) setRemainingSeconds(data.remainingSeconds)
  }, [data])

  useEffect(() => {
    const timer = setInterval(() => {
      setRemainingSeconds((prev) => (prev === null ? prev : Math.max(0, prev - 1)))
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (remainingSeconds === 0 && holdId) {
      queryClient.refetchQueries({ queryKey: ['hold', holdId] })
    }
  }, [remainingSeconds, holdId, queryClient])

  return { remainingSeconds, expired: isError, hold: data }
}

export function formatCountdown(totalSeconds: number) {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}
