import { api } from '../../api/client'

export interface BankTransferReservation {
  reservationId: number
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED' | 'EXPIRED'
  paymentMethod: 'BANK_TRANSFER'
  /** 실 백엔드가 문자열 하나로 관리함(BANK_ACCOUNT_INFO 환경변수) — 구조화된 객체 아님 */
  bankAccountInfo: string
  paymentDueAt: string
}

export interface ReservationSeatItem {
  section: string
  row: string
  number: number
  grade: string
  price: number
}

export interface BankTransferReservationDetail extends BankTransferReservation {
  performance: { performanceId: number; title: string } | null
  schedule: { scheduleId: number; date: string; time: string } | null
  seats: ReservationSeatItem[]
  confirmedAt: string | null
}

export const reservationApi = {
  createBankTransfer: (holdId: string, depositorName: string) =>
    api.post<BankTransferReservation>('/reservations/bank-transfer', { holdId, depositorName }),
  getBankTransfer: (reservationId: number) =>
    api.get<BankTransferReservationDetail>(`/reservations/bank-transfer/${reservationId}`),
}
