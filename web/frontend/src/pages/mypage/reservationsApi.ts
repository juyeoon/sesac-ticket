import { api } from '../../api/client'

export interface MyReservationListItem {
  reservationId: number
  performanceTitle: string
  date: string
  status: 'PENDING_PAYMENT' | 'CONFIRMED' | 'EXPIRED'
}

export const reservationsApi = {
  list: () =>
    api.get<{ content: MyReservationListItem[]; totalElements: number }>('/users/me/reservations'),
}
