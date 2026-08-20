import { api } from '../../api/client'

export interface PerformanceListItem {
  id: number
  title: string
  thumbnailUrl: string | null
  category: { id: number; name: string }
  venue: { id: number; name: string; address: string }
  dateFrom: string
  dateTo: string
  ticketOpenAt: string
  ticketCloseAt: string
  /** 실제 백엔드가 확인해준 값은 현재 "ACTIVE" 하나뿐 — 다른 값이 뭔지 미확정이라 string으로 느슨하게 둠 */
  status: string
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
  /** 실제 백엔드 상세 응답엔 status 필드 자체가 없음 — 목록 조회에만 있음. 없으면 배지 자체를 안 그림. */
  status?: string
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
