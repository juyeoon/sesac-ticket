import { Box, CircularProgress } from '@mui/material'
import { AppRoutes } from './routes/AppRoutes'
import { useAuth } from './auth/AuthContext'

function App() {
  const { isInitializing } = useAuth()

  // refreshToken 쿠키로 로그인 상태를 복원하는 짧은 순간, 로그인/로그아웃 UI가 번갈아 보이는 걸 방지
  if (isInitializing) {
    return (
      <Box sx={{ minHeight: '100dvh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  return <AppRoutes />
}

export default App
