import { Box, Stack, Typography } from '@mui/material'
import type { ReactNode } from 'react'
import { PlaceholderImage } from '../common/PlaceholderImage'

interface AuthCardProps {
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
}

/**
 * 로그인/회원가입/비밀번호 재설정 공통 레이아웃. 예전엔 중앙 정렬 카드 하나였는데,
 * 인터파크 티켓·야놀자 등 실 서비스의 로그인 화면처럼 좌측에 브랜드 비주얼을 두고
 * 우측에 폼을 배치하는 2단 구성으로 바꿨다 — 모바일에선 비주얼을 숨기고 폼만 보여준다.
 */
export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  return (
    <Box sx={{ minHeight: 'calc(100dvh - 140px)', display: 'flex' }}>
      <Box sx={{ display: { xs: 'none', md: 'block' }, position: 'relative', flex: 1 }}>
        <PlaceholderImage seed="auth-hero" fill />
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(160deg, rgba(20,18,24,0.15) 0%, rgba(20,18,24,0.65) 100%)',
          }}
        />
        <Stack sx={{ position: 'absolute', left: 48, bottom: 56, right: 48 }} spacing={1}>
          <Typography variant="h2" sx={{ color: 'white' }}>
            새싹티켓
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.85)' }}>
            보고 싶었던 공연, 지금 바로 예매하세요.
          </Typography>
        </Stack>
      </Box>

      <Box
        sx={{
          flex: { xs: 1, md: '0 0 440px' },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: { xs: 3, sm: 6 },
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 360 }}>
          <Typography variant="h4" gutterBottom>
            {title}
          </Typography>
          {description && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {description}
            </Typography>
          )}
          {children}
          {footer && (
            <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>{footer}</Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}
