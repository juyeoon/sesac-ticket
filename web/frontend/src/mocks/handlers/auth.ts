import { http, HttpResponse } from 'msw'
import { db, findUserByEmail, issueMockToken } from '../db'
import { requireAuth } from '../requireAuth'

const BASE = '/api/v1'

function randomCode() {
  return String(Math.floor(100000 + Math.random() * 900000))
}

export const authHandlers = [
  http.post(`${BASE}/auth/signup`, async ({ request }) => {
    const { email, password, nickname } = (await request.json()) as {
      email: string
      password: string
      nickname: string
    }
    if (!email || !password || !nickname) {
      return HttpResponse.json({ message: '입력값을 확인해주세요.' }, { status: 400 })
    }
    if (findUserByEmail(email)) {
      return HttpResponse.json({ message: '이미 가입된 이메일입니다.' }, { status: 409 })
    }
    const user = {
      id: db.nextUserId++,
      email,
      password,
      nickname,
      preferredGenres: [],
      emailVerified: false,
      favoritePerformanceIds: [],
    }
    db.users.push(user)
    return HttpResponse.json({ userId: user.id }, { status: 201 })
  }),

  http.post(`${BASE}/auth/login`, async ({ request }) => {
    const { email, password } = (await request.json()) as { email: string; password: string }
    const user = findUserByEmail(email)
    if (!user || user.password !== password) {
      return HttpResponse.json({ message: '이메일 또는 비밀번호가 올바르지 않습니다.' }, { status: 401 })
    }
    const accessToken = issueMockToken('access', user.id)
    return HttpResponse.json({ accessToken, tokenType: 'Bearer', expiresIn: 1800 })
  }),

  http.post(`${BASE}/auth/logout`, () => HttpResponse.json({ loggedOut: true })),

  http.post(`${BASE}/auth/email/verify-request`, async ({ request }) => {
    const { email } = (await request.json()) as { email: string }
    const code = randomCode()
    db.pendingEmailCodes.set(email, code)
    // eslint-disable-next-line no-console
    console.info(`[mock] ${email} 인증코드: ${code}`)
    return HttpResponse.json({ sent: true })
  }),

  http.post(`${BASE}/auth/email/verify`, async ({ request }) => {
    const { email, code } = (await request.json()) as { email: string; code: string }
    if (db.pendingEmailCodes.get(email) !== code) {
      return HttpResponse.json({ message: '인증코드가 일치하지 않습니다.' }, { status: 400 })
    }
    db.pendingEmailCodes.delete(email)
    const user = findUserByEmail(email)
    if (user) user.emailVerified = true
    return HttpResponse.json({ verified: true })
  }),

  http.post(`${BASE}/auth/password/reset-request`, async ({ request }) => {
    const { email } = (await request.json()) as { email: string }
    if (!findUserByEmail(email)) {
      return HttpResponse.json({ sent: true }) // 이메일 존재 여부 노출 방지
    }
    const code = randomCode()
    db.passwordResetTokens.set(code, email)
    // eslint-disable-next-line no-console
    console.info(`[mock] ${email} 비밀번호 재설정 인증번호: ${code}`)
    return HttpResponse.json({ sent: true })
  }),

  http.post(`${BASE}/auth/password/reset`, async ({ request }) => {
    const { resetToken, newPassword } = (await request.json()) as {
      resetToken: string
      newPassword: string
    }
    const email = db.passwordResetTokens.get(resetToken)
    if (!email) {
      return HttpResponse.json({ message: '토큰이 만료되었거나 올바르지 않습니다.' }, { status: 400 })
    }
    const user = findUserByEmail(email)
    if (user) user.password = newPassword
    db.passwordResetTokens.delete(resetToken)
    return HttpResponse.json({ reset: true })
  }),

  http.get(`${BASE}/users/me`, ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })
    const { password: _password, ...safeUser } = user
    return HttpResponse.json(safeUser)
  }),

  http.patch(`${BASE}/users/me`, async ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })
    const body = (await request.json()) as Partial<
      Pick<typeof user, 'nickname' | 'gender' | 'ageRange' | 'preferredGenres'>
    >
    Object.assign(user, body)
    return HttpResponse.json({ updated: true })
  }),

  http.get(`${BASE}/users/me/favorites`, ({ request }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })
    return HttpResponse.json({
      content: user.favoritePerformanceIds,
      totalElements: user.favoritePerformanceIds.length,
    })
  }),

  http.post(`${BASE}/users/me/favorites/:performanceId`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })
    const id = Number(params.performanceId)
    if (!user.favoritePerformanceIds.includes(id)) user.favoritePerformanceIds.push(id)
    return HttpResponse.json({ favorited: true }, { status: 201 })
  }),

  http.delete(`${BASE}/users/me/favorites/:performanceId`, ({ request, params }) => {
    const user = requireAuth(request)
    if (!user) return HttpResponse.json({ message: '인증이 필요합니다.' }, { status: 401 })
    const id = Number(params.performanceId)
    user.favoritePerformanceIds = user.favoritePerformanceIds.filter((f) => f !== id)
    return HttpResponse.json({ favorited: false })
  }),
]
