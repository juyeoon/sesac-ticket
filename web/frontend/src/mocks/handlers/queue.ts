import { http, HttpResponse } from 'msw'
import { requireAuth } from '../requireAuth'
import { issueMockToken } from '../db'
import { QUEUE_WAIT_MS, store } from '../data/store'

const BASE = '/api/v1'

export const queueHandlers = [
  http.post(`${BASE}/queue/enter`, async ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const { performanceId, scheduleId } = (await request.json()) as {
      performanceId: number
      scheduleId: number
    }
    const queueToken = issueMockToken('queue', user.id)
    store.queueEntries.set(queueToken, {
      enteredAt: Date.now(),
      performanceId,
      scheduleId,
      userId: user.id,
    })
    return HttpResponse.json({ queueToken, position: 3, estimatedWaitSeconds: Math.round(QUEUE_WAIT_MS / 1000) })
  }),

  http.get(`${BASE}/queue/:queueToken/status`, ({ params }) => {
    const entry = store.queueEntries.get(String(params.queueToken))
    if (!entry) return HttpResponse.json({ message: '대기열 토큰을 찾을 수 없습니다.' }, { status: 404 })

    const elapsed = Date.now() - entry.enteredAt
    if (elapsed < QUEUE_WAIT_MS) {
      const remainingSteps = Math.ceil((QUEUE_WAIT_MS - elapsed) / 3000)
      return HttpResponse.json({
        status: 'WAITING',
        position: Math.max(1, Math.min(3, remainingSteps)),
        estimatedWaitSeconds: Math.max(0, Math.round((QUEUE_WAIT_MS - elapsed) / 1000)),
        entryTicket: null,
      })
    }

    const entryTicket = issueMockToken('entry', entry.userId)
    store.entryTickets.set(entryTicket, {
      scheduleId: entry.scheduleId,
      userId: entry.userId,
      expiresAt: Date.now() + 10 * 60 * 1000,
    })
    return HttpResponse.json({ status: 'READY', position: 0, estimatedWaitSeconds: 0, entryTicket })
  }),
]
