import { api } from '../../api/client'

export interface VenueSeat {
  seatId: number
  section: string
  row: string
  number: number
  x: number
  y: number
  grade: string
}

export interface VenueSeatMap {
  venueId: number
  sections: { sectionName: string; seats: VenueSeat[] }[]
}

// PENDING_PAYMENT: 예매 생성됨(무통장입금 접수) but 관리자 확정 전 — 백엔드가
// 2026-08-21부터 HELD -> PENDING_PAYMENT -> RESERVED 3단계로 분리함(이전엔
// 예매 생성 즉시 RESERVED였음). 화면에선 선점중(HELD)과 유사하게 선택 불가로
// 표시하되 라벨만 "입금대기중"으로 구분한다.
export type SeatStatus = 'AVAILABLE' | 'HELD' | 'PENDING_PAYMENT' | 'RESERVED'

export interface ScheduleSeat {
  seatId: number
  section: string
  row: string
  number: number
  grade: string
  status: SeatStatus
}

export interface HoldResult {
  holdId: string
  seatIds: number[]
  expiresAt: string
}

export interface HoldDetail extends HoldResult {
  remainingSeconds: number
}

export const seatApi = {
  venueSeatMap: (venueId: number) => api.get<VenueSeatMap>(`/venues/${venueId}/seat-map`),
  scheduleSeats: (scheduleId: number) => api.get<ScheduleSeat[]>(`/schedules/${scheduleId}/seats`),
  createHold: (scheduleId: number, seatIds: number[], entryTicket: string) =>
    api.post<HoldResult>('/seats/hold', { scheduleId, seatIds, entryTicket }),
  getHold: (holdId: string) => api.get<HoldDetail>(`/seats/hold/${holdId}`),
  releaseHold: (holdId: string) => api.delete<{ holdId: string; released: boolean }>(`/seats/hold/${holdId}`),
}
