import { api } from '../../api/client'

export interface PerformanceListItem {
  id: number
  title: string
  thumbnailUrl: string | null
  category: string
  venue: { id: number; name: string }
  dateFrom: string
  dateTo: string
  ticketOpenAt: string
  ticketCloseAt: string
  status: 'UPCOMING' | 'ON_SALE' | 'CLOSED'
}

export interface SeatGrade {
  grade: string
  price: number
  remaining?: number
}

export interface Schedule {
  scheduleId: number
  date: string
  time: string
  seatGrades: SeatGrade[]
}

export interface PerformanceDetail {
  id: number
  title: string
  category: { id: number; name: string }
  description: string
  ticketOpenAt: string
  ticketCloseAt: string
  status: 'UPCOMING' | 'ON_SALE' | 'CLOSED'
  schedules: Schedule[]
  priceInfo: { minPrice: number; maxPrice: number }
  runningTimeMin: number
  ageLimit: string
  seatGrades: SeatGrade[]
  venue: { id: number; name: string; address: string }
  images: { imageUrl: string; sortOrder: number }[]
}

export const performanceApi = {
  list: () => api.get<{ content: PerformanceListItem[]; totalElements: number }>('/performances'),
  search: (keyword: string) =>
    api.get<{ content: PerformanceListItem[]; totalElements: number }>(
      `/performances/search?keyword=${encodeURIComponent(keyword)}`,
    ),
  detail: (performanceId: number) => api.get<PerformanceDetail>(`/performances/${performanceId}`),
  schedules: (performanceId: number) => api.get<Schedule[]>(`/performances/${performanceId}/schedules`),
  shareLink: (performanceId: number) =>
    api.get<{ shareUrl: string }>(`/performances/${performanceId}/share-link`),
}
