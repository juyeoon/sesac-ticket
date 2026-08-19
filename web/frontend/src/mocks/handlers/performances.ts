import { http, HttpResponse } from 'msw'
import { performances } from '../data/performances'
import { countRemainingByGrade } from '../seatStatus'

const BASE = '/api/v1'

/** 잔여석은 mock 데이터의 고정값이 아니라 실제 좌석 상태 저장소(store.seatStatusBySchedule) 기준으로 계산한다.
 * 그래야 좌석을 선점/예매했을 때 목록·상세 화면의 "잔여" 숫자도 같이 줄어든다. */
function withLiveRemaining(schedule: (typeof performances)[number]['schedules'][number]) {
  const live = countRemainingByGrade(schedule.scheduleId)
  return {
    ...schedule,
    seatGrades: schedule.seatGrades.map((g) => ({
      ...g,
      remaining: live?.get(g.grade) ?? g.remaining,
    })),
  }
}

function toListItem(p: (typeof performances)[number]) {
  return {
    id: p.id,
    title: p.title,
    thumbnailUrl: null,
    category: p.category,
    venue: { id: p.venue.id, name: p.venue.name },
    dateFrom: p.dateFrom,
    dateTo: p.dateTo,
    ticketOpenAt: p.ticketOpenAt,
    ticketCloseAt: p.ticketCloseAt,
    status: p.status,
  }
}

export const performanceHandlers = [
  // /search를 /:performanceId보다 먼저 선언해야 "search"가 id 파라미터로 잘못 매칭되지 않는다
  http.get(`${BASE}/performances/search`, ({ request }) => {
    const keyword = new URL(request.url).searchParams.get('keyword')
    if (!keyword) {
      return HttpResponse.json({ message: 'keyword는 필수입니다.' }, { status: 400 })
    }
    const content = performances.filter((p) => p.title.includes(keyword)).map(toListItem)
    return HttpResponse.json({ content, totalElements: content.length })
  }),

  http.get(`${BASE}/performances`, () => {
    const content = performances.map(toListItem)
    return HttpResponse.json({ content, totalElements: content.length })
  }),

  http.get(`${BASE}/performances/:performanceId/share-link`, ({ request, params }) => {
    const performance = performances.find((p) => p.id === Number(params.performanceId))
    if (!performance) return HttpResponse.json({ message: '공연을 찾을 수 없습니다.' }, { status: 404 })
    const origin = new URL(request.url).origin
    return HttpResponse.json({ shareUrl: `${origin}/performances/${performance.id}` })
  }),

  http.get(`${BASE}/performances/:performanceId/schedules`, ({ params }) => {
    const performance = performances.find((p) => p.id === Number(params.performanceId))
    if (!performance) return HttpResponse.json({ message: '공연을 찾을 수 없습니다.' }, { status: 404 })
    return HttpResponse.json(performance.schedules.map(withLiveRemaining))
  }),

  http.get(`${BASE}/performances/:performanceId`, ({ params }) => {
    const performance = performances.find((p) => p.id === Number(params.performanceId))
    if (!performance) return HttpResponse.json({ message: '공연을 찾을 수 없습니다.' }, { status: 404 })

    const prices = performance.seatGrades.map((g) => g.price)
    return HttpResponse.json({
      id: performance.id,
      title: performance.title,
      category: { id: 0, name: performance.category },
      description: performance.description,
      ticketOpenAt: performance.ticketOpenAt,
      ticketCloseAt: performance.ticketCloseAt,
      status: performance.status,
      schedules: performance.schedules.map(withLiveRemaining),
      priceInfo: { minPrice: Math.min(...prices), maxPrice: Math.max(...prices) },
      runningTimeMin: performance.runningTimeMin,
      ageLimit: performance.ageLimit,
      seatGrades: performance.seatGrades,
      venue: performance.venue,
      images: [],
    })
  }),
]
