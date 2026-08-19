import { performances } from './performances'

export interface VenueSeat {
  seatId: number
  section: string
  row: number
  number: number
  x: number
  y: number
  grade: string
}

export interface VenueSeatMap {
  venueId: number
  sections: { sectionName: string; seats: VenueSeat[] }[]
}

const ROWS_PER_GRADE = 3
const SEATS_PER_ROW = 8

/**
 * venue_seat는 회차와 무관한 정적 좌표라 공연(=venue) 1개당 한 번만 생성해서 캐싱한다.
 * 가격이 높은 등급일수록 무대(row 1)에 가깝게 배치.
 */
const cache = new Map<number, VenueSeatMap>()

export function getSeatMap(venueId: number): VenueSeatMap | null {
  if (cache.has(venueId)) return cache.get(venueId)!

  const performance = performances.find((p) => p.venue.id === venueId)
  if (!performance) return null

  const gradesByPrice = [...performance.seatGrades].sort((a, b) => b.price - a.price)
  const seats: VenueSeat[] = []
  let seatId = venueId * 10000
  let rowCursor = 1

  for (const { grade } of gradesByPrice) {
    for (let r = 0; r < ROWS_PER_GRADE; r++) {
      for (let n = 1; n <= SEATS_PER_ROW; n++) {
        seats.push({
          seatId: seatId++,
          section: 'A구역',
          row: rowCursor,
          number: n,
          x: n,
          y: rowCursor,
          grade,
        })
      }
      rowCursor++
    }
  }

  const seatMap: VenueSeatMap = { venueId, sections: [{ sectionName: 'A구역', seats }] }
  cache.set(venueId, seatMap)
  return seatMap
}
