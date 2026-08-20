import { Box, Container, Stack, Typography } from '@mui/material'
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'

const NAV = [
  { path: '/mypage', label: '내 정보' },
  { path: '/mypage/reservations', label: '내 예매 목록' },
  { path: '/mypage/favorites', label: '관심 공연' },
]

export default function MyPageLayout() {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return (
      <CenteredMessagePage
        eyebrow="마이페이지"
        title="로그인이 필요해요"
        description="로그인 후 내 정보와 예매 내역을 확인할 수 있어요."
      />
    )
  }

  const activePath = location.pathname === '/mypage/edit' ? '/mypage' : location.pathname

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Stack direction="row" spacing={2} sx={{ alignItems: 'center', mb: 4 }}>
        <Box
          sx={{
            width: 64,
            height: 64,
            flexShrink: 0,
            bgcolor: 'text.primary',
            color: 'background.paper',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24,
            fontWeight: 700,
          }}
        >
          {user?.nickname?.[0]?.toUpperCase()}
        </Box>
        <Box>
          <Typography variant="h5">{user?.nickname}님</Typography>
          <Typography variant="body2" color="text.secondary">
            {user?.email}
          </Typography>
        </Box>
      </Stack>

      <Stack direction="row" spacing={3} sx={{ mb: 4, borderBottom: 1, borderColor: 'grey.100' }}>
        {NAV.map((item) => {
          const active = activePath === item.path
          return (
            <Box
              key={item.path}
              component={RouterLink}
              to={item.path}
              sx={{
                pb: 1.5,
                textDecoration: 'none',
                color: active ? 'text.primary' : 'text.secondary',
                fontWeight: active ? 700 : 500,
                fontSize: '0.9375rem',
                borderBottom: active ? 2 : 2,
                borderColor: active ? 'text.primary' : 'transparent',
                mb: '-1px',
              }}
            >
              {item.label}
            </Box>
          )
        })}
      </Stack>

      <Outlet />
    </Container>
  )
}
