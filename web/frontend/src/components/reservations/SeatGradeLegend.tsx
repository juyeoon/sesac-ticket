import { Box, Stack, Typography } from '@mui/material'
import { getGradeColor, type GradeColor } from './gradeColor'

interface SeatGradeLegendProps {
  seatGrades: { grade: string; price: number }[]
  gradeColors: Map<string, GradeColor>
}

/** 등급별 색상·가격을 한눈에 보여주는 상단 범례 — 좌석 색상만으로 등급을 구분할 수 있게 한다. */
export function SeatGradeLegend({ seatGrades, gradeColors }: SeatGradeLegendProps) {
  const sorted = [...seatGrades].sort((a, b) => b.price - a.price)

  return (
    <Stack direction="row" spacing={3} sx={{ flexWrap: 'wrap', rowGap: 1.5 }}>
      {sorted.map((g) => {
        const color = getGradeColor(gradeColors, g.grade)
        return (
          <Stack key={g.grade} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Box
              sx={{
                width: 22,
                height: 22,
                borderRadius: '7px 7px 3px 3px',
                bgcolor: color.soft,
                border: `1px solid ${color.main}55`,
                boxShadow: 'inset 0 2px 0 rgba(255,255,255,0.55)',
              }}
            />
            <Stack spacing={-0.25}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: color.main }}>
                {g.grade}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {g.price.toLocaleString()}원
              </Typography>
            </Stack>
          </Stack>
        )
      })}
    </Stack>
  )
}
