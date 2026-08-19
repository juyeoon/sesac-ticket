import { Box, Card, CardContent, Container, Typography } from '@mui/material'
import type { ReactNode } from 'react'

interface AuthCardProps {
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
}

/** 로그인/회원가입/비밀번호 재설정 공통 카드 레이아웃. figma 와이어프레임의 중앙 정렬 카드 구조를 그대로 따르되 새 디자인 시스템을 입힘. */
export function AuthCard({ title, description, children, footer }: AuthCardProps) {
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: 'calc(100dvh - 140px)', py: { xs: 4, sm: 8 } }}>
      <Container maxWidth="xs">
        <Card>
          <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
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
              <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
                {footer}
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  )
}
