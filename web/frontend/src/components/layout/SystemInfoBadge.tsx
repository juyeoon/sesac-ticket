import { useQuery } from '@tanstack/react-query'
import { Typography } from '@mui/material'
import { systemApi } from '../../pages/system/systemApi'

/** 제출 필수조건: Front/Server version, 서버 IP·서버명을 화면에 노출. */
export function SystemInfoBadge() {
  const { data } = useQuery({ queryKey: ['system-version'], queryFn: systemApi.version })

  return (
    <Typography variant="caption" color="text.secondary">
      Front v{__APP_VERSION__}
      {data && (
        <>
          {' · '}Server v{data.apiVersion}
          {' · '}X-Forwarded-For: {data.clientIp}
          {' · '}web-ip: {data.webIp} · api-ip: {data.apiIp}
        </>
      )}
    </Typography>
  )
}
