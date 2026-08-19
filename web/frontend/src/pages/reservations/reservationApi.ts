import { api } from '../../api/client'

export interface BankAccountInfo {
  bankName: string
  accountNumber: string
  accountHolder: string
}

export interface BankTransferReservation {
  reservationId: number
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'EXPIRED'
  paymentMethod: 'BANK_TRANSFER'
  bankAccountInfo: BankAccountInfo
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
