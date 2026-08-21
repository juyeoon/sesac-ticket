import { useMemo } from 'react'
import { Box, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
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

// 좌석 수가 실제로 많을 수 있어(예: 45열) 셀을 작게 잡아야 가로 스크롤 없이 한 화면에 들어온다.
const CELL = 18
const GAP = 4
const LABEL_W = 18

// 좌석 배치도에는 선택중/선점중/예매완료 3가지 상태만 구분해서 보여준다.
// PENDING_PAYMENT(입금대기중)는 좌석을 고를 수 없다는 점에서 예매완료와 동일하게 취급한다.
function isReservedLook(status: SeatStatus) {
  return status === 'RESERVED' || status === 'PENDING_PAYMENT'
}

function seatStyle(status: SeatStatus, isSelected: boolean, gradeColor: GradeColor) {
  if (isSelected) return { bgcolor: seatTokens.selectedBg, border: `1px solid ${seatTokens.selectedBg}` }
  if (isReservedLook(status)) return { bgcolor: seatTokens.reservedBg, border: `1px solid ${seatTokens.reservedBg}` }
  if (status === 'HELD') return { bgcolor: seatTokens.heldBg, border: `1px solid ${seatTokens.heldBorder}` }
  return { bgcolor: gradeColor.soft, border: `1px solid ${gradeColor.main}66` }
}

/** 무대를 곡선으로 표현 — 좌석이 부채꼴로 펼쳐진 공연장 느낌을 살리기 위함. */
function StageArc({ width }: { width: number }) {
  const w = Math.max(280, width)
  const h = 40
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3, minWidth: w }}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: 'block' }}>
        <path
          d={`M 16 ${h - 8} Q ${w / 2} 2 ${w - 16} ${h - 8}`}
          fill="none"
          stroke={neutral.gray300}
          strokeWidth={3}
          strokeLinecap="round"
        />
      </svg>
      <Typography variant="overline" sx={{ letterSpacing: 5, color: 'text.disabled', mt: -1, fontWeight: 600, fontSize: 10 }}>
        STAGE
      </Typography>
    </Box>
  )
}

export function SeatGrid({ seats, selectedSeatIds, onToggle, gradeColors }: SeatGridProps) {
  // 서버가 내려주는 x/y는 그리드 인덱스가 아니라 실제 배치 좌표(20px 단위 등)라서,
  // 그대로 grid-column/row로 쓰면 대부분 빈 칸인 초대형 그리드가 만들어진다.
  // 좌석들이 실제로 사용한 x/y 값들만 뽑아 순번을 매겨 촘촘한 그리드 인덱스로 변환한다.
  const { colIndex, rowIndex, maxCol, maxRow } = useMemo(() => {
    const xs = [...new Set(seats.map((s) => s.x))].sort((a, b) => a - b)
    const ys = [...new Set(seats.map((s) => s.y))].sort((a, b) => a - b)
    const colIndex = new Map(xs.map((x, i) => [x, i]))
    const rowIndex = new Map(ys.map((y, i) => [y, i]))
    return { colIndex, rowIndex, maxCol: Math.max(1, xs.length), maxRow: Math.max(1, ys.length) }
  }, [seats])

  const rowLabelByIndex = useMemo(() => {
    const map = new Map<number, string>()
    for (const s of seats) {
      const idx = rowIndex.get(s.y) ?? 0
      if (!map.has(idx)) map.set(idx, s.row)
    }
    return map
  }, [seats, rowIndex])

  const totalWidth = LABEL_W * 2 + maxCol * CELL + (maxCol + 1) * GAP

  return (
    <Box sx={{ overflowX: 'auto', pb: 1 }}>
      <StageArc width={maxCol * (CELL + GAP)} />
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: `${LABEL_W}px repeat(${maxCol}, ${CELL}px) ${LABEL_W}px`,
          gridTemplateRows: `repeat(${maxRow}, ${CELL}px)`,
          gap: `${GAP}px`,
          minWidth: totalWidth,
          alignItems: 'center',
        }}
      >
        {[...rowLabelByIndex.entries()].flatMap(([idx, label]) => [
          <Typography
            key={`l-${idx}`}
            variant="caption"
            sx={{ gridColumn: 1, gridRow: idx + 1, textAlign: 'center', color: 'text.disabled', fontWeight: 600, fontSize: 10 }}
          >
            {label}
          </Typography>,
          <Typography
            key={`r-${idx}`}
            variant="caption"
            sx={{ gridColumn: maxCol + 2, gridRow: idx + 1, textAlign: 'center', color: 'text.disabled', fontWeight: 600, fontSize: 10 }}
          >
            {label}
          </Typography>,
        ])}

        {seats.map((seat) => {
          const isSelected = selectedSeatIds.includes(seat.seatId)
          const disabled = seat.status !== 'AVAILABLE' && !isSelected
          const style = seatStyle(seat.status, isSelected, getGradeColor(gradeColors, seat.grade))
          const col = (colIndex.get(seat.x) ?? 0) + 2
          const row = (rowIndex.get(seat.y) ?? 0) + 1
          return (
            <Box
              key={seat.seatId}
              onClick={() => !disabled && onToggle(seat.seatId)}
              title={`${seat.grade} · ${seat.row}열 ${seat.number}번`}
              data-seat-id={seat.seatId}
              data-seat-status={isSelected ? 'SELECTED' : seat.status}
              sx={{
                gridColumn: col,
                gridRow: row,
                width: CELL,
                height: CELL,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                userSelect: 'none',
                cursor: disabled ? 'not-allowed' : 'pointer',
                opacity: disabled ? 0.5 : 1,
                transition: 'opacity 0.1s ease, outline-color 0.1s ease',
                outline: '1px solid transparent',
                outlineOffset: '1px',
                '&:hover': disabled ? undefined : { outlineColor: neutral.eerieBlack },
                ...style,
              }}
            >
              {isReservedLook(seat.status) && !isSelected && (
                <CloseIcon sx={{ fontSize: CELL - 4, color: seatTokens.reservedText }} />
              )}
            </Box>
          )
        })}
      </Box>
    </Box>
  )
}
