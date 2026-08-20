/**
 * 대기열 / 좌석상태 / Hold / 예매를 위한 인메모리 mock 저장소.
 * 브라우저 세션(탭) 동안만 유지된다.
 */

export type SeatStatus = 'AVAILABLE' | 'HELD' | 'SOLD'

export const QUEUE_WAIT_MS = 7000 // 데모용으로 짧게 — 실제로는 트래픽에 따라 가변

interface QueueEntry {
  enteredAt: number
  performanceId: number
  scheduleId: number
  userId: number
}

interface EntryTicket {
  scheduleId: number
  userId: number
  expiresAt: number
}

export const HOLD_TTL_MS = 5 * 60 * 1000 // 5분 (실제 스펙값 그대로)

interface HoldRecord {
  holdId: string
  userId: number
  scheduleId: number
  seatIds: number[]
  expiresAt: number
}

export interface ReservationRecord {
  reservationId: number
  userId: number
  scheduleId: number
  seatIds: number[]
  depositorName: string
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'EXPIRED'
  paymentDueAt: number
  createdAt: number
}

export const store = {
  queueEntries: new Map<string, QueueEntry>(),
  entryTickets: new Map<string, EntryTicket>(),
  /** scheduleId -> (seatId -> status). 회차별로 최초 조회 시 지연 생성. */
  seatStatusBySchedule: new Map<number, Map<number, SeatStatus>>(),
  holds: new Map<string, HoldRecord>(),
  reservations: [] as ReservationRecord[],
  nextReservationId: 1000,
}

/** 실제 백엔드는 이걸 문자열 하나(BANK_ACCOUNT_INFO 환경변수)로 관리함 — 형식 그대로 맞춤 */
export const BANK_ACCOUNT_INFO = '국민은행 123456-78-901234 (예금주: 새싹티켓)'
