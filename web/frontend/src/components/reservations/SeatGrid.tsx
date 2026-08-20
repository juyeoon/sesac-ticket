import { useMemo } from 'react'
import { Box, Typography } from '@mui/material'
import { seat as seatTokens, neutral } from '../../theme/tokens'
import type { SeatStatus } from '../../pages/reservations/seatApi'
import { getGradeColor, type GradeColor } from './gradeColor'

export interface MergedSeat {
  seatId: number
  x: number
  y: number
  row: string
  number: number
  grade: string
  status: SeatStatus
}

interface SeatGridProps {
  seats: MergedSeat[]
  selectedSeatIds: number[]
  onToggle: (seatId: number) => void
  gradeColors: Map<string, GradeColor>
}

const CELL = 36

function seatStyle(status: SeatStatus, isSelected: boolean, gradeColor: GradeColor) {
  if (isSelected) return { bgcolor: seatTokens.selectedBg, color: seatTokens.selectedText, border: 'none', boxShadow: 'none' }
  if (status === 'RESERVED') return { bgcolor: seatTokens.reservedBg, color: seatTokens.reservedText, border: 'none', boxShadow: 'none' }
  if (status === 'HELD') return { bgcolor: seatTokens.heldBg, color: seatTokens.heldText, border: `1px solid ${seatTokens.heldBorder}`, boxShadow: 'none' }
  return {
    bgcolor: gradeColor.soft,
    color: gradeColor.main,
    border: `1px solid ${gradeColor.main}55`,
    boxShadow: 'inset 0 2px 0 rgba(255,255,255,0.55)',
  }
}

/** 무대를 곡선으로 표현 — 좌석이 부채꼴로 펼쳐진 공연장 느낌을 살리기 위함. */
function StageArc({ width }: { width: number }) {
  const w = Math.max(280, width)
  const h = 56
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4, minWidth: w }}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block' }}>
        <path
          d={`M 16 ${h - 10} Q ${w / 2} 2 ${w - 16} ${h - 10}`}
          fill="none"
          stroke={neutral.gray300}
          strokeWidth={4}
          strokeLinecap="round"
        />
      </svg>
      <Typography variant="overline" sx={{ letterSpacing: 6, color: 'text.disabled', mt: -1.5, fontWeight: 700 }}>
        STAGE
      </Typography>
    </Box>
  )
}

export function SeatGrid({ seats, selectedSeatIds, onToggle, gradeColors }: SeatGridProps) {
  const maxX = Math.max(1, ...seats.map((s) => s.x))
  const maxY = Math.max(1, ...seats.map((s) => s.y))
  const totalWidth = (maxX + 2) * (CELL + 6)

  const rowLabelByY = useMemo(() => {
    const map = new Map<number, string>()
    for (const s of seats) if (!map.has(s.y)) map.set(s.y, s.row)
    return map
  }, [seats])

  return (
    <Box sx={{ overflowX: 'auto', pb: 1 }}>
      <StageArc width={maxX * (CELL + 6)} />

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: `28px repeat(${maxX}, ${CELL}px) 28px`,
          gridTemplateRows: `repeat(${maxY}, ${CELL}px)`,
          gap: '6px',
          minWidth: totalWidth,
          alignItems: 'center',
        }}
      >
        {[...rowLabelByY.entries()].flatMap(([y, label]) => [
          <Typography
            key={`l-${y}`}
            variant="caption"
            sx={{ gridColumn: 1, gridRow: y, textAlign: 'center', color: 'text.disabled', fontWeight: 600 }}
          >
            {label}
          </Typography>,
          <Typography
            key={`r-${y}`}
            variant="caption"
            sx={{ gridColumn: maxX + 2, gridRow: y, textAlign: 'center', color: 'text.disabled', fontWeight: 600 }}
          >
            {label}
          </Typography>,
        ])}

        {seats.map((seat) => {
          const isSelected = selectedSeatIds.includes(seat.seatId)
          const disabled = seat.status !== 'AVAILABLE' && !isSelected
          const style = seatStyle(seat.status, isSelected, getGradeColor(gradeColors, seat.grade))
          return (
            <Box
              key={seat.seatId}
              onClick={() => !disabled && onToggle(seat.seatId)}
              title={`${seat.grade} · ${seat.row}열 ${seat.number}번`}
              data-seat-id={seat.seatId}
              data-seat-status={isSelected ? 'SELECTED' : seat.status}
              sx={{
                gridColumn: seat.x + 1,
                gridRow: seat.y,
                width: CELL,
                height: CELL,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '10px 10px 4px 4px',
                fontSize: 11,
                fontWeight: 700,
                userSelect: 'none',
                cursor: disabled ? 'not-allowed' : 'pointer',
                transition: 'transform 0.12s ease',
                '&:hover': disabled ? undefined : { transform: 'scale(1.1)' },
                ...style,
              }}
            >
              {seat.number}
            </Box>
          )
        })}
      </Box>
    </Box>
  )
}
