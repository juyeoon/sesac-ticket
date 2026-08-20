import { Chip, Container, Stack, Typography } from '@mui/material'
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { CenteredMessagePage } from '../../components/common/CenteredMessagePage'

const NAV = [
  { path: '/mypage', label: '내 정보' },
  { path: '/mypage/reservations', label: '내 예매 목록' },
  { path: '/mypage/favorites', label: '관심 공연' },
]

export default function MyPageLayout() {
  const { isAuthenticated } = useAuth()
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
      <Typography variant="h3" sx={{ mb: 3 }}>
        마이페이지
      </Typography>
      <Stack direction="row" spacing={1} sx={{ mb: 4, flexWrap: 'wrap', rowGap: 1 }}>
        {NAV.map((item) => (
          <Chip
            key={item.path}
            component={RouterLink}
            to={item.path}
            clickable
            label={item.label}
            color={activePath === item.path ? 'primary' : undefined}
            variant={activePath === item.path ? 'filled' : 'outlined'}
          />
        ))}
      </Stack>
      <Outlet />
    </Container>
  )
}
