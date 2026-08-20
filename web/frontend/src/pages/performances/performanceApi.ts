import { api } from '../../api/client'

export interface PerformanceListItem {
  id: number
  title: string
  thumbnailUrl: string | null
  category: { id: number; name: string }
  venue: { id: number; name: string; address: string | null }
  dateFrom: string | null
  dateTo: string | null
  ticketOpenAt: string | null
  ticketCloseAt: string | null
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
  description: string | null
  ticketOpenAt: string | null
  ticketCloseAt: string | null
  /** 공연 목록 조회에만 있고 상세 응답엔 없음 — 있으면 배지, 없으면 렌더링 생략 */
  status?: string
  schedules: Schedule[]
  priceInfo: { minPrice: number; maxPrice: number }
  runningTimeMin: number | null
  ageLimit: string | null
  seatGrades: SeatGrade[]
  venue: { id: number; name: string; address: string | null }
  images: { imageUrl: string; sortOrder: number }[]
}

export interface ScheduleBackref {
  scheduleId: number
  performanceId: number
  performanceTitle: string
  venueId: number
  venueName: string
  date: string
  time: string
  seatGrades: SeatGrade[]
}

export const performanceApi = {
  list: () => api.get<{ content: PerformanceListItem[]; totalElements: number }>('/performances'),
  search: (keyword: string) =>
    api.get<{ content: PerformanceListItem[]; totalElements: number }>(
      `/performances/search?keyword=${encodeURIComponent(keyword)}`,
    ),
  detail: (performanceId: number) => api.get<PerformanceDetail>(`/performances/${performanceId}`),
  /** 회차 → 공연/공연장 역참조. 좌석 선택 화면을 새로고침해서 라우터 state가 사라졌을 때 복구용으로 쓴다. */
  scheduleBackref: (scheduleId: number) => api.get<ScheduleBackref>(`/schedules/${scheduleId}`),
}
