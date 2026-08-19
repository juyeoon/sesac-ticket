import { Chip } from '@mui/material'
import type { PerformanceListItem } from '../../pages/performances/performanceApi'

const STATUS_META: Record<PerformanceListItem['status'], { label: string; bg: string; color: string }> = {
  UPCOMING: { label: '오픈 예정', bg: 'accent.blueSoft', color: 'accent.blueMain' },
  ON_SALE: { label: '예매중', bg: 'accent.greenSoft', color: 'accent.greenMain' },
  CLOSED: { label: '판매 종료', bg: 'grey.100', color: 'text.disabled' },
}

export function StatusBadge({ status }: { status: PerformanceListItem['status'] }) {
  const meta = STATUS_META[status]
  return (
    <Chip
      label={meta.label}
      size="small"
      sx={{ bgcolor: meta.bg, color: meta.color, fontWeight: 600 }}
    />
  )
}
