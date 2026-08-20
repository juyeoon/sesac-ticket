import { http, HttpResponse } from 'msw'
import { issueMockToken } from '../db'

const BASE = '/api/v1'

/** 목업 관리자 계정 — 실 백엔드엔 admin 테이블에 별도로 시드돼 있음 */
const MOCK_ADMIN = { adminId: 'admin', password: 'admin1234' }

export const adminHandlers = [
  http.post(`${BASE}/admin/auth/login`, async ({ request }) => {
    const { adminId, password } = (await request.json()) as { adminId: string; password: string }
    if (adminId !== MOCK_ADMIN.adminId || password !== MOCK_ADMIN.password) {
      return HttpResponse.json({ message: '관리자 ID 또는 비밀번호가 올바르지 않습니다.' }, { status: 401 })
    }
    const accessToken = issueMockToken('admin-access', 0)
    return HttpResponse.json({ accessToken, tokenType: 'Bearer', expiresIn: 1800 })
  }),
]
