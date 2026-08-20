import { Box, Typography } from '@mui/material'
import { seat as seatTokens } from '../../theme/tokens'
import type { SeatStatus } from '../../pages/reservations/seatApi'

export interface MergedSeat {
  seatId: number
  x: number
  y: number
  row: number
  number: number
  grade: string
  status: SeatStatus
}

interface SeatGridProps {
  seats: MergedSeat[]
  selectedSeatIds: number[]
  onToggle: (seatId: number) => void
}

function seatStyle(status: SeatStatus, isSelected: boolean) {
  if (isSelected) return { bgcolor: seatTokens.selectedBg, color: seatTokens.selectedText, border: 'none' }
  if (status === 'RESERVED') return { bgcolor: seatTokens.reservedBg, color: seatTokens.reservedText, border: 'none' }
  if (status === 'HELD') return { bgcolor: seatTokens.heldBg, color: seatTokens.heldText, border: `1px solid ${seatTokens.heldBorder}` }
  return { bgcolor: seatTokens.availableBg, color: 'text.primary', border: `1px solid ${seatTokens.availableBorder}` }
}

export function SeatGrid({ seats, selectedSeatIds, onToggle }: SeatGridProps) {
  const maxX = Math.max(1, ...seats.map((s) => s.x))
  const maxY = Math.max(1, ...seats.map((s) => s.y))

  return (
    <Box sx={{ overflowX: 'auto', pb: 1 }}>
      <Box sx={{ minWidth: maxX * 42, mb: 3 }}>
        <Box sx={{ bgcolor: 'grey.800', color: 'common.white', textAlign: 'center', py: 1.5, borderRadius: 2 }}>
          <Typography variant="subtitle2">STAGE</Typography>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: `repeat(${maxX}, 34px)`,
          gridTemplateRows: `repeat(${maxY}, 34px)`,
          gap: '6px',
          minWidth: maxX * 42,
        }}
      >
        {seats.map((seat) => {
          const isSelected = selectedSeatIds.includes(seat.seatId)
          const disabled = seat.status !== 'AVAILABLE' && !isSelected
          const style = seatStyle(seat.status, isSelected)
          return (
            <Box
              key={seat.seatId}
              onClick={() => !disabled && onToggle(seat.seatId)}
              title={`${seat.grade} · ${seat.row}열 ${seat.number}번`}
              data-seat-id={seat.seatId}
              data-seat-status={isSelected ? 'SELECTED' : seat.status}
              sx={{
                gridColumn: seat.x,
                gridRow: seat.y,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '8px',
                fontSize: 11,
                fontWeight: 700,
                userSelect: 'none',
                cursor: disabled ? 'not-allowed' : 'pointer',
                transition: 'transform 0.1s ease',
                '&:hover': disabled ? undefined : { transform: 'scale(1.08)' },
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
