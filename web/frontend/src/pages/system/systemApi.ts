import { api } from '../../api/client'

export interface VersionResult {
  apiVersion: string
  server: { instanceId: string; az: string }
  /** X-Forwarded-For — ALB/nginx 프록시 체인이 실제로 클라이언트 IP를 전달하는지 확인용 */
  clientIp: string
}

/** docs/backend-decisions-followup-1_ANSWER.md — 이 응답 형태(clientIp 포함) 그대로 확정됨. */
export const systemApi = {
  version: () => api.get<VersionResult>('/version'),
}
