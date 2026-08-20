import { Box, Stack, Typography } from '@mui/material'
import { seat as seatTokens } from '../../theme/tokens'

const ITEMS = [
  { label: '예매 가능', bg: seatTokens.availableBg, border: seatTokens.availableBorder },
  { label: '선택중', bg: seatTokens.selectedBg, border: seatTokens.selectedBg },
  { label: '선점중', bg: seatTokens.heldBg, border: seatTokens.heldBorder },
  { label: '예매 완료', bg: seatTokens.reservedBg, border: seatTokens.reservedBg },
]

export function SeatLegend() {
  return (
    <Stack direction="row" spacing={2.5} sx={{ flexWrap: 'wrap', rowGap: 1 }}>
      {ITEMS.map((item) => (
        <Stack key={item.label} direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
          <Box
            sx={{
              width: 18,
              height: 18,
              borderRadius: '5px',
              bgcolor: item.bg,
              border: `1px solid ${item.border}`,
            }}
          />
          <Typography variant="caption" color="text.secondary">
            {item.label}
          </Typography>
        </Stack>
      ))}
    </Stack>
  )
}
