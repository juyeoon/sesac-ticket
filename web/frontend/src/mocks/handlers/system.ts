import { http, HttpResponse } from 'msw'

const BASE = '/api/v1'

/** API-SYS-003(GET /version)에 서버 식별 필드(server)와 clientIp를 얹는 형태로 확정됨 (docs/backend-decisions-followup-1_ANSWER.md). */
export const systemHandlers = [
  http.get(`${BASE}/version`, ({ request }) => {
    // 실제 배포 환경에선 nginx/ALB가 X-Forwarded-For를 채워줌. mock 단계에선 흉내만 낸다.
    const forwardedFor = request.headers.get('x-forwarded-for') ?? '127.0.0.1 (mock — 실제 프록시 체인 없음)'
    return HttpResponse.json({
      apiVersion: '1.0.0-mock',
      server: { instanceId: 'api-a', az: 'ap-northeast-2a' },
      clientIp: forwardedFor,
    })
  }),
]
