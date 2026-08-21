import { Chip } from '@mui/material'

/**
 * 실제 백엔드가 확인해준 값은 "ACTIVE"뿐이라, 나머지(UPCOMING/CLOSED 등)는 추측값이다.
 * 모르는 값이 오면 원문 그대로 회색 배지로 보여줘서 죽지 않게 한다.
 */
const STATUS_META: Record<string, { label: string; bg: string; color: string }> = {
  ACTIVE: { label: '예매중', bg: 'accent.greenSoft', color: 'accent.greenMain' },
  ON_SALE: { label: '예매중', bg: 'accent.greenSoft', color: 'accent.greenMain' },
  UPCOMING: { label: '오픈 예정', bg: 'accent.blueSoft', color: 'accent.blueMain' },
  CLOSED: { label: '판매 종료', bg: 'grey.100', color: 'text.disabled' },
  ENDED: { label: '예매 종료', bg: 'grey.100', color: 'text.disabled' },
  HIDDEN: { label: '비공개', bg: 'grey.100', color: 'text.disabled' },
}

export function StatusBadge({ status }: { status: string }) {
  const meta = STATUS_META[status] ?? { label: status, bg: 'grey.100', color: 'text.secondary' }
  return (
    <Chip
      label={meta.label}
      size="small"
      sx={{ bgcolor: meta.bg, color: meta.color, fontWeight: 600 }}
    />
  )
}
