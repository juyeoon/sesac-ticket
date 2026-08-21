import { api } from '../../api/client'

export interface VersionResult {
  apiVersion: string
  /** X-Forwarded-For — ALB/nginx 프록시 체인이 실제로 클라이언트 IP를 전달하는지 확인용 */
  clientIp: string | null
  /** X-Forwarded-For 마지막 항목 = web(nginx) 인스턴스의 IP */
  webIp: string | null
  /** 이 요청을 받은 API(WAS) 인스턴스의 실제 IP (request.scope["server"] 실측값) */
  apiIp: string | null
}

/** docs/backend-decisions-followup-1_ANSWER.md — 이 응답 형태(clientIp 포함) 그대로 확정됨. */
export const systemApi = {
  version: () => api.get<VersionResult>('/version'),
}
