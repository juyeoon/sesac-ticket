/**
 * 관리자 전용 API 클라이언트. 회원용 `client.ts`와 완전히 분리 —
 * 실 백엔드도 `adminRefreshToken` 쿠키(경로 `/api/v1/admin/auth`)를 회원용
 * `refreshToken`과 별도로 관리하므로, accessToken도 별도 모듈 변수로 보관한다.
 */

import { ApiError } from './client'

const BASE_URL = '/api/v1'
const REFRESH_PATH = '/admin/auth/refresh'

let adminAccessToken: string | null = null

export function setAdminAccessToken(token: string | null) {
  adminAccessToken = token
}

interface AdminAccessTokenResult {
  accessToken: string
  expiresIn: number
}

export async function refreshAdminAccessToken(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}${REFRESH_PATH}`, { method: 'POST' })
    if (!res.ok) return false
    const body = (await res.json()) as AdminAccessTokenResult
    setAdminAccessToken(body.accessToken)
    return true
  } catch {
    return false
  }
}

let refreshInFlight: Promise<boolean> | null = null

function refreshOnce(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = refreshAdminAccessToken().finally(() => {
      refreshInFlight = null
    })
  }
  return refreshInFlight
}

async function rawRequest(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(adminAccessToken ? { Authorization: `Bearer ${adminAccessToken}` } : {}),
      ...init?.headers,
    },
  })
}

async function parseBody<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T
  const body = await res.json().catch(() => null)
  if (!res.ok) {
    throw new ApiError(res.status, body?.message ?? '요청에 실패했습니다.', body?.errorCode)
  }
  return body as T
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await rawRequest(path, init)

  if (res.status === 401 && path !== REFRESH_PATH) {
    const refreshed = await refreshOnce()
    if (refreshed) {
      const retryRes = await rawRequest(path, init)
      return parseBody<T>(retryRes)
    }
  }

  return parseBody<T>(res)
}

export const adminApiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
}
