import { Box, Stack, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { seat as seatTokens } from '../../theme/tokens'

/** 좌석 상태(선택/선점/예매완료) 범례. 등급별 색상·가격은 SeatGradeLegend가 따로 보여준다. */
export function SeatLegend() {
  return (
    <Stack direction="row" spacing={2.5} sx={{ flexWrap: 'wrap', rowGap: 1 }}>
      <LegendItem label="선택중" bg={seatTokens.selectedBg} border={seatTokens.selectedBg} />
      <LegendItem label="선점중" bg={seatTokens.heldBg} border={seatTokens.heldBorder} />
      <LegendItem label="예매 완료" bg={seatTokens.reservedBg} border={seatTokens.reservedBg} showX />
    </Stack>
  )
}

function LegendItem({ label, bg, border, showX }: { label: string; bg: string; border: string; showX?: boolean }) {
  return (
    <Stack direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
      <Box
        sx={{
          width: 16,
          height: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: bg,
          border: `1px solid ${border}`,
        }}
      >
        {showX && <CloseIcon sx={{ fontSize: 12, color: seatTokens.reservedText }} />}
      </Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  )
}
