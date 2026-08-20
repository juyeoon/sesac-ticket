import { useQuery } from '@tanstack/react-query'
import { Typography } from '@mui/material'
import { systemApi } from '../../pages/system/systemApi'

/**
 * 제출 필수조건: Front/Server version, 서버 IP·서버명을 화면에 노출.
 * docs/backend-decisions-needed.md 4번 참고 — server 필드는 백엔드 확정 전까지 mock.
 */
export function SystemInfoBadge() {
  const { data } = useQuery({ queryKey: ['system-version'], queryFn: systemApi.version })

  return (
    <Typography variant="caption" color="text.secondary">
      Front v{__APP_VERSION__}
      {data && (
        <>
          {' · '}Server v{data.apiVersion} ({data.server.instanceId} · {data.server.az})
        </>
      )}
    </Typography>
  )
}
