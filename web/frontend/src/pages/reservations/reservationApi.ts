import { api } from '../../api/client'

export interface BankTransferReservation {
  reservationId: number
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'CANCELLED' | 'EXPIRED'
  paymentMethod: 'BANK_TRANSFER'
  /** 실제 백엔드가 문자열 하나로 관리함(BANK_ACCOUNT_INFO 환경변수) — 구조화된 객체 아님 */
  bankAccountInfo: string
  paymentDueAt: string
}

export interface BankTransferReservationDetail extends BankTransferReservation {
  performance: { id: number; title: string } | null
  schedule: { scheduleId: number; date: string; time: string } | null
  seats: { seatId: number; section?: string; row?: number; number?: number; grade?: string }[]
  depositorName: string
}

export const reservationApi = {
  createBankTransfer: (holdId: string, depositorName: string) =>
    api.post<BankTransferReservation>('/reservations/bank-transfer', { holdId, depositorName }),
  getBankTransfer: (reservationId: number) =>
    api.get<BankTransferReservationDetail>(`/reservations/bank-transfer/${reservationId}`),
}
