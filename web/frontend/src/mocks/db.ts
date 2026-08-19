/**
 * MSW 핸들러가 공유하는 인메모리 mock DB.
 * 브라우저 세션(탭) 동안만 유지된다 — 새로고침하면 초기화됨. 실 백엔드 연동 시 이 파일 전체를 걷어낸다.
 */

export interface MockUser {
  id: number
  email: string
  password: string
  nickname: string
  gender?: string
  ageRange?: string
  preferredGenres: string[]
  emailVerified: boolean
  favoritePerformanceIds: number[]
}

export const db = {
  users: [
    {
      id: 1,
      email: 'test@example.com',
      password: 'passwd123',
      nickname: 'testUser',
      gender: 'F',
      ageRange: '20대',
      preferredGenres: [],
      emailVerified: true,
      favoritePerformanceIds: [],
    },
  ] as MockUser[],

  pendingEmailCodes: new Map<string, string>(), // email -> code
  passwordResetTokens: new Map<string, string>(), // token -> email
  refreshTokens: new Map<string, number>(), // refreshToken -> userId
  nextUserId: 2,
}

export function findUserByEmail(email: string) {
  return db.users.find((u) => u.email === email)
}

export function issueMockToken(prefix: string, userId: number) {
  return `${prefix}-${userId}-${Math.random().toString(36).slice(2)}`
}
