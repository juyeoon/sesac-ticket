const TTL_MS = 9 * 60 * 1000 // 서버의 entryTicket 유효기간(10분)보다 살짝 짧게 잡아서 만료 직전 재사용을 방지

export interface QueueContext {
  ticket: string
  venueId: number
  performanceId: number
  performanceTitle: string
}

interface StoredQueueContext extends QueueContext {
  savedAt: number
}

function key(scheduleId: number) {
  return `entryTicket:${scheduleId}`
}

/** 회차 새로고침/재진입 시 대기열을 다시 안 타도 되도록, 티켓과 함께 표시에 필요한 컨텍스트도 저장한다. */
export function saveQueueContext(scheduleId: number, ctx: QueueContext) {
  const stored: StoredQueueContext = { ...ctx, savedAt: Date.now() }
  sessionStorage.setItem(key(scheduleId), JSON.stringify(stored))
}

export function getValidQueueContext(scheduleId: number): QueueContext | null {
  const raw = sessionStorage.getItem(key(scheduleId))
  if (!raw) return null
  try {
    const stored = JSON.parse(raw) as StoredQueueContext
    if (Date.now() - stored.savedAt > TTL_MS) return null
    return stored
  } catch {
    return null
  }
}

export function clearQueueContext(scheduleId: number) {
  sessionStorage.removeItem(key(scheduleId))
}
