import { useQuery } from '@tanstack/react-query'
import { Box, Typography } from '@mui/material'
import { systemApi } from '../../pages/system/systemApi'
import { accent, neutral } from '../../theme/tokens'

/** 제출 필수조건: Front/Server version, 서버 IP·서버명을 화면에 노출. 눈에 잘 띄도록 헤더에 배지 형태로 표시. */
export function SystemInfoBadge() {
  const { data } = useQuery({ queryKey: ['system-version'], queryFn: systemApi.version })

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        px: 1.25,
        py: 0.375,
        bgcolor: accent.yellowMain,
        maxWidth: '100%',
      }}
    >
      <Typography variant="caption" sx={{ color: neutral.eerieBlack, fontWeight: 700 }}>
        Front v{__APP_VERSION__}
        {data && (
          <>
            {' · '}Server v{data.apiVersion}
            {' · '}X-Forwarded-For: {data.clientIp}
            {' · '}web-ip: {data.webIp} · api-ip: {data.apiIp}
          </>
        )}
      </Typography>
    </Box>
  )
}
