import { findSchedule } from './data/performances'
import { getSeatMap } from './data/venues'
import { store, type SeatStatus } from './data/store'

/**
 * 회차별 좌석 상태를 지연 생성한다. performances 핸들러(잔여석 표시)와
 * reservations 핸들러(좌석 배치도) 양쪽에서 같은 저장소를 참조해야 예매 후
 * "잔여" 숫자가 실제 배치도 상태와 어긋나지 않는다.
 */
export function getOrInitSeatStatus(scheduleId: number) {
  if (store.seatStatusBySchedule.has(scheduleId)) return store.seatStatusBySchedule.get(scheduleId)!

  const found = findSchedule(scheduleId)
  if (!found) return null
  const seatMap = getSeatMap(found.performance.venue.id)
  if (!seatMap) return null

  const statusMap = new Map<number, SeatStatus>()
  for (const seat of seatMap.sections.flatMap((s) => s.seats)) {
    // 데모용 고정 시드 — 일부 좌석을 미리 판매완료/선점중으로 채워서 3가지 상태를 전부 보여준다
    let status: SeatStatus = 'AVAILABLE'
    if (seat.seatId % 7 === 0) status = 'RESERVED'
    else if (seat.seatId % 11 === 0) status = 'HELD'
    statusMap.set(seat.seatId, status)
  }
  store.seatStatusBySchedule.set(scheduleId, statusMap)
  return statusMap
}

export function countRemainingByGrade(scheduleId: number): Map<string, number> | null {
  const statusMap = getOrInitSeatStatus(scheduleId)
  const found = findSchedule(scheduleId)
  if (!statusMap || !found) return null
  const seatMap = getSeatMap(found.performance.venue.id)!
  const seatsById = new Map(seatMap.sections.flatMap((s) => s.seats).map((s) => [s.seatId, s]))

  const counts = new Map<string, number>()
  for (const [seatId, status] of statusMap) {
    if (status !== 'AVAILABLE') continue
    const grade = seatsById.get(seatId)?.grade
    if (!grade) continue
    counts.set(grade, (counts.get(grade) ?? 0) + 1)
  }
  return counts
}
