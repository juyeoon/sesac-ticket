import { db } from './db'

/** MSW 핸들러 공용 인증 체크. Authorization 헤더의 mock accessToken에서 userId를 뽑아 사용자를 찾는다. */
export function requireAuth(request: Request) {
  const auth = request.headers.get('authorization')
  if (!auth?.startsWith('Bearer ')) return null
  const token = auth.slice('Bearer '.length)
  const userId = Number(token.split('-')[1])
  return db.users.find((u) => u.id === userId) ?? null
}
