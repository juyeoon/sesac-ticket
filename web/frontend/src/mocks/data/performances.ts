export interface MockSeatGrade {
  grade: string
  price: number
  remaining?: number
}

export interface MockSchedule {
  scheduleId: number
  date: string // YYYY-MM-DD
  time: string // HH:mm
  seatGrades: MockSeatGrade[]
}

export type PerformanceStatus = 'UPCOMING' | 'ON_SALE' | 'CLOSED'

export interface MockPerformance {
  id: number
  title: string
  category: string
  status: PerformanceStatus
  description: string
  ticketOpenAt: string
  ticketCloseAt: string
  dateFrom: string
  dateTo: string
  runningTimeMin: number
  ageLimit: string
  venue: { id: number; name: string; address: string }
  seatGrades: MockSeatGrade[]
  schedules: MockSchedule[]
}

export const CATEGORIES = ['콘서트', '뮤지컬', '연극', '전시'] as const

export const performances: MockPerformance[] = [
  {
    id: 1,
    title: '여름밤 재즈 페스티벌',
    category: '콘서트',
    status: 'ON_SALE',
    description:
      '도심 속에서 즐기는 야외 재즈 페스티벌입니다. 국내외 재즈 뮤지션들의 라이브 무대를 스탠딩으로 즐길 수 있습니다.',
    ticketOpenAt: '2026-08-01T10:00:00',
    ticketCloseAt: '2026-09-10T23:59:59',
    dateFrom: '2026-09-12',
    dateTo: '2026-09-13',
    runningTimeMin: 150,
    ageLimit: '전체 관람가',
    venue: { id: 1, name: '한강 잔디마당', address: '서울 영등포구 여의동로 330' },
    seatGrades: [
      { grade: 'STANDING', price: 88000 },
      { grade: 'VIP', price: 132000 },
    ],
    schedules: [
      { scheduleId: 101, date: '2026-09-12', time: '19:00', seatGrades: [{ grade: 'STANDING', price: 88000, remaining: 340 }, { grade: 'VIP', price: 132000, remaining: 42 }] },
      { scheduleId: 102, date: '2026-09-13', time: '19:00', seatGrades: [{ grade: 'STANDING', price: 88000, remaining: 512 }, { grade: 'VIP', price: 132000, remaining: 60 }] },
    ],
  },
  {
    id: 2,
    title: '뮤지컬 별의 시간',
    category: '뮤지컬',
    status: 'ON_SALE',
    description: '시간을 거슬러 첫사랑을 찾아가는 이야기를 그린 창작 뮤지컬. 감성적인 넘버와 화려한 무대 연출이 돋보입니다.',
    ticketOpenAt: '2026-07-15T10:00:00',
    ticketCloseAt: '2026-10-30T23:59:59',
    dateFrom: '2026-08-20',
    dateTo: '2026-10-31',
    runningTimeMin: 160,
    ageLimit: '만 12세 이상',
    venue: { id: 2, name: '예술의전당 오페라극장', address: '서울 서초구 남부순환로 2406' },
    seatGrades: [
      { grade: 'R석', price: 154000 },
      { grade: 'S석', price: 121000 },
      { grade: 'A석', price: 88000 },
    ],
    schedules: [
      { scheduleId: 201, date: '2026-08-22', time: '19:30', seatGrades: [{ grade: 'R석', price: 154000, remaining: 12 }, { grade: 'S석', price: 121000, remaining: 58 }, { grade: 'A석', price: 88000, remaining: 120 }] },
      { scheduleId: 202, date: '2026-08-23', time: '14:00', seatGrades: [{ grade: 'R석', price: 154000, remaining: 30 }, { grade: 'S석', price: 121000, remaining: 70 }, { grade: 'A석', price: 88000, remaining: 140 }] },
      { scheduleId: 203, date: '2026-08-23', time: '19:30', seatGrades: [{ grade: 'R석', price: 154000, remaining: 0 }, { grade: 'S석', price: 121000, remaining: 15 }, { grade: 'A석', price: 88000, remaining: 90 }] },
    ],
  },
  {
    id: 3,
    title: '연극 파도가 지날 때',
    category: '연극',
    status: 'ON_SALE',
    description: '작은 항구 마을을 배경으로 세 자매의 이야기를 그린 소극장 연극.',
    ticketOpenAt: '2026-08-05T10:00:00',
    ticketCloseAt: '2026-09-25T23:59:59',
    dateFrom: '2026-09-01',
    dateTo: '2026-09-27',
    runningTimeMin: 100,
    ageLimit: '만 7세 이상',
    venue: { id: 3, name: '대학로 소극장 온', address: '서울 종로구 대학로 12길 21' },
    seatGrades: [{ grade: '전석', price: 44000 }],
    schedules: [
      { scheduleId: 301, date: '2026-09-05', time: '19:00', seatGrades: [{ grade: '전석', price: 44000, remaining: 48 }] },
      { scheduleId: 302, date: '2026-09-06', time: '19:00', seatGrades: [{ grade: '전석', price: 44000, remaining: 20 }] },
    ],
  },
  {
    id: 4,
    title: '고전미술전: 색의 결',
    category: '전시',
    status: 'ON_SALE',
    description: '동시대 작가들의 색채 연구를 조명하는 기획 전시.',
    ticketOpenAt: '2026-07-01T10:00:00',
    ticketCloseAt: '2026-11-30T23:59:59',
    dateFrom: '2026-08-01',
    dateTo: '2026-11-30',
    runningTimeMin: 90,
    ageLimit: '전체 관람가',
    venue: { id: 4, name: '서울시립미술관', address: '서울 중구 덕수궁길 61' },
    seatGrades: [{ grade: '입장권', price: 18000 }],
    schedules: [
      { scheduleId: 401, date: '2026-09-01', time: '10:00', seatGrades: [{ grade: '입장권', price: 18000, remaining: 300 }] },
      { scheduleId: 402, date: '2026-09-01', time: '14:00', seatGrades: [{ grade: '입장권', price: 18000, remaining: 300 }] },
    ],
  },
  {
    id: 5,
    title: '가을 클래식 갈라 콘서트',
    category: '콘서트',
    status: 'UPCOMING',
    description: '국내 정상급 오케스트라와 협연 아티스트가 함께하는 갈라 콘서트.',
    ticketOpenAt: '2026-09-01T10:00:00',
    ticketCloseAt: '2026-10-20T23:59:59',
    dateFrom: '2026-10-24',
    dateTo: '2026-10-24',
    runningTimeMin: 110,
    ageLimit: '만 8세 이상',
    venue: { id: 5, name: '롯데콘서트홀', address: '서울 송파구 올림픽로 300' },
    seatGrades: [
      { grade: 'R석', price: 110000 },
      { grade: 'S석', price: 77000 },
    ],
    schedules: [
      { scheduleId: 501, date: '2026-10-24', time: '19:30', seatGrades: [{ grade: 'R석', price: 110000, remaining: 200 }, { grade: 'S석', price: 77000, remaining: 300 }] },
    ],
  },
  {
    id: 6,
    title: '뮤지컬 도시의 밤',
    category: '뮤지컬',
    status: 'CLOSED',
    description: '네온 불빛 가득한 도시를 배경으로 한 청춘 군상극.',
    ticketOpenAt: '2026-05-01T10:00:00',
    ticketCloseAt: '2026-07-31T23:59:59',
    dateFrom: '2026-06-01',
    dateTo: '2026-07-31',
    runningTimeMin: 145,
    ageLimit: '만 12세 이상',
    venue: { id: 6, name: '충무아트센터 대극장', address: '서울 중구 퇴계로 387' },
    seatGrades: [
      { grade: 'R석', price: 132000 },
      { grade: 'S석', price: 99000 },
    ],
    schedules: [
      { scheduleId: 601, date: '2026-07-30', time: '19:30', seatGrades: [{ grade: 'R석', price: 132000, remaining: 0 }, { grade: 'S석', price: 99000, remaining: 0 }] },
    ],
  },
]
