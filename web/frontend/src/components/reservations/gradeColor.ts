import { accent } from '../../theme/tokens'

/** 좌석 등급을 가격 높은 순으로 훑으며 파스텔 액센트 컬러를 순서대로 배정한다 (등급 이름은 백엔드가 자유롭게 정하므로 이름이 아니라 순서로 매핑). */
const PALETTE = [
  { soft: accent.yellowSoft, main: accent.yellowMain },
  { soft: accent.blueSoft, main: accent.blueMain },
  { soft: accent.greenSoft, main: accent.greenMain },
]
const FALLBACK = { soft: '#E5E4EA', main: '#6B6A76' }

export interface GradeColor {
  soft: string
  main: string
}

export function buildGradeColorMap(seatGrades: { grade: string; price: number }[]): Map<string, GradeColor> {
  const sorted = [...seatGrades].sort((a, b) => b.price - a.price)
  const map = new Map<string, GradeColor>()
  sorted.forEach((g, i) => map.set(g.grade, PALETTE[i] ?? FALLBACK))
  return map
}

export function getGradeColor(map: Map<string, GradeColor>, grade: string): GradeColor {
  return map.get(grade) ?? FALLBACK
}
