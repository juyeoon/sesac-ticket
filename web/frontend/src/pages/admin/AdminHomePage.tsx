import { Box, Button, Container, Stack, Typography } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'
import { useAdminAuth } from '../../admin/AdminAuthContext'

export default function AdminHomePage() {
  const { adminId, isAdminAuthenticated, logout } = useAdminAuth()
  const navigate = useNavigate()

  if (!isAdminAuthenticated) {
    return (
      <CenteredMessagePage
        eyebrow="관리자"
        title="로그인이 필요해요"
        description="관리자 계정으로 로그인 후 이용할 수 있어요."
        ctaHref="/admin/login"
        ctaLabel="관리자 로그인으로 이동"
      />
    )
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ minHeight: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 1.5 }}>
        <Typography variant="overline" color="text.secondary">
          관리자
        </Typography>
        <Typography variant="h3">{adminId}님 환영합니다</Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          관리자 대시보드는 다음 단계에서 채워질 예정입니다.
        </Typography>
        <Stack direction="row" spacing={1.5}>
          <Button
            variant="outlined"
            onClick={() => {
              logout()
              navigate('/admin/login', { replace: true })
            }}
          >
            로그아웃
          </Button>
        </Stack>
      </Box>
    </Container>
  )
}
