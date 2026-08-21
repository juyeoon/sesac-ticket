import { adminApiClient } from '../../api/adminClient'

export interface AdminAccessTokenResult {
  accessToken: string
  tokenType: string
  expiresIn: number
}

export interface ConfirmBankTransferResult {
  reservationId: number
  status: 'CONFIRMED'
  confirmedAt: string
}

export interface AdminReservationSeatItem {
  section: string
  row: string
  number: number
  grade: string
  price: number
}

export interface AdminReservationListItem {
  reservationId: number
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED' | 'EXPIRED'
  depositorName: string | null
  member: { memberId: number; nickname: string; email: string }
  performance: { performanceId: number; title: string }
  schedule: { scheduleId: number; date: string; time: string }
  seats: AdminReservationSeatItem[]
}

export const adminApi = {
  login: (adminId: string, password: string) =>
    adminApiClient.post<AdminAccessTokenResult>('/admin/auth/login', { adminId, password }),
  // GET /reservations/list — 관리자 전용 전체 예매 목록 (페이지네이션 없음).
  listReservations: () => adminApiClient.get<AdminReservationListItem[]>('/reservations/list'),
  confirmBankTransfer: (reservationId: number) =>
    adminApiClient.post<ConfirmBankTransferResult>(`/reservations/bank-transfer/${reservationId}/confirm`),
}
