import { api } from '../../api/client'

export interface VenueSeat {
  seatId: number
  section: string
  row: number
  number: number
  x: number
  y: number
  grade: string
}

export interface VenueSeatMap {
  venueId: number
  sections: { sectionName: string; seats: VenueSeat[] }[]
}

export type SeatStatus = 'AVAILABLE' | 'HELD' | 'RESERVED'

export interface ScheduleSeat {
  seatId: number
  section: string
  row: number
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
