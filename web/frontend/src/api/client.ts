/**
 * 회원(member) 전용 API 클라이언트. 관리자는 완전히 분리된 `adminClient.ts`를 쓴다 —
 * 실 백엔드도 회원/관리자 refresh 쿠키를 이름·경로부터 분리해서 관리하기 때문.
 *
 * baseURL은 `/api/v1` 상대경로 — 개발 중엔 vite.config.ts의 proxy가, 운영에선 nginx가
 * 같은 오리진으로 묶어줘서 refreshToken(HttpOnly 쿠키) 왕복에 별도 CORS 설정이 필요 없다.
 */

const BASE_URL = '/api/v1'
const REFRESH_PATH = '/auth/refresh'

export class ApiError extends Error {
  status: number
  errorCode?: string

  constructor(status: number, message: string, errorCode?: string) {
    super(message)
    this.status = status
    this.errorCode = errorCode
  }
}

let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

interface AccessTokenResult {
  accessToken: string
  expiresIn: number
}

/** refreshToken 쿠키로 새 accessToken을 발급받는다. 앱 시작 시 로그인 상태 복원, 401 재시도에 둘 다 쓰인다. */
export async function refreshAccessToken(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}${REFRESH_PATH}`, { method: 'POST' })
    if (!res.ok) return false
    const body = (await res.json()) as AccessTokenResult
    setAccessToken(body.accessToken)
    return true
  } catch {
    return false
  }
}

let refreshInFlight: Promise<boolean> | null = null

function refreshOnce(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = refreshAccessToken().finally(() => {
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
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
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

  // accessToken 만료(401) 시 refreshToken 쿠키로 한 번만 재발급 시도 후 원요청 재시도.
  // /auth/refresh 자체의 401은 재시도하지 않는다(무한루프 방지) — 로그아웃 상태로 처리.
  if (res.status === 401 && path !== REFRESH_PATH) {
    const refreshed = await refreshOnce()
    if (refreshed) {
      const retryRes = await rawRequest(path, init)
      return parseBody<T>(retryRes)
    }
  }

  return parseBody<T>(res)
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  patch: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'PATCH', body: data ? JSON.stringify(data) : undefined }),
  put: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'PUT', body: data ? JSON.stringify(data) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}
