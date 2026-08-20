import { api } from '../../api/client'

export interface VersionResult {
  apiVersion: string
  server: { instanceId: string; az: string }
  /** X-Forwarded-For — ALB/nginx 프록시 체인이 실제로 클라이언트 IP를 전달하는지 확인용 */
  clientIp: string
}

/**
 * docs/backend-decisions-needed.md 4번 항목 — 실제 백엔드가 이 형태로 확정되면
 * 이 파일만 고치면 됨(화면 쪽은 손댈 필요 없음).
 */
export const systemApi = {
  version: () => api.get<VersionResult>('/version'),
}
