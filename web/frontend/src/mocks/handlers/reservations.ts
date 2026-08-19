import { http, HttpResponse } from 'msw'
import { requireAuth } from '../requireAuth'
import { issueMockToken } from '../db'
import { findSchedule } from '../data/performances'
import { getSeatMap } from '../data/venues'
import { BANK_ACCOUNT_INFO, HOLD_TTL_MS, store } from '../data/store'
import { getOrInitSeatStatus } from '../seatStatus'

const BASE = '/api/v1'

function releaseSeats(scheduleId: number, seatIds: number[]) {
  const statusMap = store.seatStatusBySchedule.get(scheduleId)
  if (!statusMap) return
  for (const id of seatIds) statusMap.set(id, 'AVAILABLE')
}

export const reservationHandlers = [
  http.get(`${BASE}/venues/:venueId/seat-map`, ({ params }) => {
    const seatMap = getSeatMap(Number(params.venueId))
    if (!seatMap) return HttpResponse.json({ message: '공연장을 찾을 수 없습니다.' }, { status: 404 })
    return HttpResponse.json(seatMap)
  }),

  http.get(`${BASE}/schedules/:scheduleId/seats`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const scheduleId = Number(params.scheduleId)
    const found = findSchedule(scheduleId)
    const statusMap = getOrInitSeatStatus(scheduleId)
    if (!found || !statusMap) {
      return HttpResponse.json({ message: '회차를 찾을 수 없습니다.' }, { status: 404 })
    }
    const seatMap = getSeatMap(found.performance.venue.id)!
    const seats = seatMap.sections
      .flatMap((s) => s.seats)
      .map((seat) => ({
        seatId: seat.seatId,
        section: seat.section,
        row: seat.row,
        number: seat.number,
        grade: seat.grade,
        status: statusMap.get(seat.seatId) ?? 'AVAILABLE',
      }))
    return HttpResponse.json(seats)
  }),

  http.post(`${BASE}/seats/hold`, async ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const { scheduleId, seatIds, entryTicket } = (await request.json()) as {
      scheduleId: number
      seatIds: number[]
      entryTicket: string
    }

    const ticket = store.entryTickets.get(entryTicket)
    if (!ticket || ticket.userId !== user.id || ticket.scheduleId !== scheduleId) {
      return HttpResponse.json({ message: '대기열 통과가 필요합니다.' }, { status: 403 })
    }

    const statusMap = getOrInitSeatStatus(scheduleId)
    if (!statusMap) return HttpResponse.json({ message: '회차를 찾을 수 없습니다.' }, { status: 404 })

    const unavailable = seatIds.filter((id) => statusMap.get(id) !== 'AVAILABLE')
    if (unavailable.length > 0) {
      return HttpResponse.json(
        { message: '이미 선점되었거나 판매된 좌석이 있습니다.', errorCode: 'SEAT_UNAVAILABLE' },
        { status: 409 },
      )
    }

    for (const id of seatIds) statusMap.set(id, 'HELD')
    const holdId = issueMockToken('hold', user.id)
    const expiresAt = Date.now() + HOLD_TTL_MS
    store.holds.set(holdId, { holdId, userId: user.id, scheduleId, seatIds, expiresAt })

    return HttpResponse.json({ holdId, seatIds, expiresAt: new Date(expiresAt).toISOString() })
  }),

  http.get(`${BASE}/seats/hold/:holdId`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const hold = store.holds.get(String(params.holdId))
    if (!hold) return HttpResponse.json({ message: 'Hold를 찾을 수 없습니다.' }, { status: 404 })
    if (hold.userId !== user.id) {
      return HttpResponse.json({ message: '본인의 선점이 아닙니다.' }, { status: 403 })
    }

    const remainingMs = hold.expiresAt - Date.now()
    if (remainingMs <= 0) {
      releaseSeats(hold.scheduleId, hold.seatIds)
      store.holds.delete(hold.holdId)
      return HttpResponse.json({ message: 'Hold가 만료되었습니다.' }, { status: 404 })
    }

    return HttpResponse.json({
      holdId: hold.holdId,
      seatIds: hold.seatIds,
      expiresAt: new Date(hold.expiresAt).toISOString(),
      remainingSeconds: Math.round(remainingMs / 1000),
    })
  }),

  http.delete(`${BASE}/seats/hold/:holdId`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const hold = store.holds.get(String(params.holdId))
    if (!hold) return HttpResponse.json({ message: 'Hold를 찾을 수 없습니다.' }, { status: 404 })
    if (hold.userId !== user.id) {
      return HttpResponse.json({ message: '본인의 선점이 아닙니다.' }, { status: 403 })
    }

    releaseSeats(hold.scheduleId, hold.seatIds)
    store.holds.delete(hold.holdId)
    return HttpResponse.json({ holdId: hold.holdId, released: true })
  }),

  http.post(`${BASE}/reservations/bank-transfer`, async ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const { holdId, depositorName } = (await request.json()) as { holdId: string; depositorName: string }
    const hold = store.holds.get(holdId)
    if (!hold) return HttpResponse.json({ message: 'Hold를 찾을 수 없거나 만료되었습니다.' }, { status: 404 })
    if (hold.userId !== user.id) {
      return HttpResponse.json({ message: '본인의 선점이 아닙니다.' }, { status: 403 })
    }
    if (hold.expiresAt - Date.now() <= 0) {
      releaseSeats(hold.scheduleId, hold.seatIds)
      store.holds.delete(holdId)
      return HttpResponse.json({ message: 'Hold가 만료되었습니다.' }, { status: 404 })
    }

    const statusMap = store.seatStatusBySchedule.get(hold.scheduleId)
    if (statusMap) for (const id of hold.seatIds) statusMap.set(id, 'SOLD')

    const reservationId = store.nextReservationId++
    const paymentDueAt = Date.now() + 24 * 60 * 60 * 1000
    store.reservations.push({
      reservationId,
      userId: user.id,
      scheduleId: hold.scheduleId,
      seatIds: hold.seatIds,
      depositorName,
      status: 'PENDING_PAYMENT',
      paymentDueAt,
      createdAt: Date.now(),
    })
    store.holds.delete(holdId)

    return HttpResponse.json(
      {
        reservationId,
        status: 'PENDING_PAYMENT',
        paymentMethod: 'BANK_TRANSFER',
        bankAccountInfo: BANK_ACCOUNT_INFO,
        paymentDueAt: new Date(paymentDueAt).toISOString(),
      },
      { status: 201 },
    )
  }),

  http.get(`${BASE}/reservations/bank-transfer/:reservationId`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const reservation = store.reservations.find((r) => r.reservationId === Number(params.reservationId))
    if (!reservation || reservation.userId !== user.id) {
      return HttpResponse.json({ message: '예매 내역을 찾을 수 없습니다.' }, { status: 404 })
    }

    const found = findSchedule(reservation.scheduleId)
    const seatMap = found ? getSeatMap(found.performance.venue.id) : null
    const seatById = new Map(seatMap?.sections.flatMap((s) => s.seats).map((s) => [s.seatId, s]) ?? [])

    return HttpResponse.json({
      reservationId: reservation.reservationId,
      performance: found ? { id: found.performance.id, title: found.performance.title } : null,
      schedule: found ? { scheduleId: found.schedule.scheduleId, date: found.schedule.date, time: found.schedule.time } : null,
      seats: reservation.seatIds.map((id) => {
        const seat = seatById.get(id)
        return seat ? { seatId: id, section: seat.section, row: seat.row, number: seat.number, grade: seat.grade } : { seatId: id }
      }),
      status: reservation.status,
      paymentMethod: 'BANK_TRANSFER',
      depositorName: reservation.depositorName,
      bankAccountInfo: BANK_ACCOUNT_INFO,
      paymentDueAt: new Date(reservation.paymentDueAt).toISOString(),
    })
  }),

  http.get(`${BASE}/users/me/reservations`, ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })

    const content = store.reservations
      .filter((r) => r.userId === user.id)
      .map((r) => {
        const found = findSchedule(r.scheduleId)
        return {
          reservationId: r.reservationId,
          performanceTitle: found?.performance.title ?? '',
          date: found?.schedule.date ?? '',
          status: r.status,
        }
      })
    return HttpResponse.json({ content, totalElements: content.length })
  }),
]
