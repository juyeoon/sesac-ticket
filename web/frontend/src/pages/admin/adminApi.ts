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

export const adminApi = {
  login: (adminId: string, password: string) =>
    adminApiClient.post<AdminAccessTokenResult>('/admin/auth/login', { adminId, password }),
  // 관리자가 예매 상세를 조회하는 API 자체가 없어서(회원 전용 엔드포인트라 admin 토큰으론
  // 403/401), 예매번호를 직접 입력받아 확정만 할 수 있다 — RESV-005 그대로.
  confirmBankTransfer: (reservationId: number) =>
    adminApiClient.post<ConfirmBankTransferResult>(`/reservations/bank-transfer/${reservationId}/confirm`),
}
