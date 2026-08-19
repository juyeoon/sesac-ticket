import { useState, type MouseEvent } from 'react'
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Container,
  IconButton,
  InputAdornment,
  Menu,
  MenuItem,
  Stack,
  TextField,
  Toolbar,
  Typography,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import { Link as RouterLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'

function UserMenu() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)

  const handleOpen = (e: MouseEvent<HTMLElement>) => setAnchorEl(e.currentTarget)
  const handleClose = () => setAnchorEl(null)

  return (
    <>
      <IconButton onClick={handleOpen} size="small">
        <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
          {user?.nickname?.[0]?.toUpperCase()}
        </Avatar>
      </IconButton>
      <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={handleClose}>
        <MenuItem
          onClick={() => {
            handleClose()
            navigate('/mypage')
          }}
        >
          마이페이지
        </MenuItem>
        <MenuItem
          onClick={async () => {
            handleClose()
            await logout()
            navigate('/')
          }}
        >
          로그아웃
        </MenuItem>
      </Menu>
    </>
  )
}

export function RootLayout() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')

  const handleSearch = () => {
    navigate(keyword.trim() ? `/?keyword=${encodeURIComponent(keyword.trim())}` : '/')
  }

  return (
    <Box sx={{ minHeight: '100dvh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="sticky">
        <Toolbar sx={{ gap: { xs: 1, sm: 3 }, minHeight: 80, '@media (min-width: 600px)': { minHeight: 80 } }}>
          <Typography
            component={RouterLink}
            to="/"
            variant="h6"
            sx={{ fontWeight: 700, textDecoration: 'none', color: 'text.primary', flexShrink: 0 }}
          >
            새싹티켓
          </Typography>

          <TextField
            size="small"
            placeholder="공연 정보를 검색하세요"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            sx={{ flex: 1, maxWidth: 420, display: { xs: 'none', sm: 'block' } }}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={handleSearch}>
                      <SearchIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />

          <Box sx={{ flexGrow: 1 }} />

          {isAuthenticated ? (
            <UserMenu />
          ) : (
            <Stack direction="row" spacing={1}>
              <Button component={RouterLink} to="/login" variant="outlined">
                로그인
              </Button>
              <Button component={RouterLink} to="/signup" variant="contained">
                회원가입
              </Button>
            </Stack>
          )}
        </Toolbar>
      </AppBar>

      <Box component="main" sx={{ flex: 1 }}>
        <Outlet />
      </Box>

      <Box component="footer" sx={{ borderTop: 1, borderColor: 'divider', py: 3, mt: 4 }}>
        <Container maxWidth="lg">
          <Typography variant="caption" color="text.secondary">
            © 2026 새싹티켓 · 새싹 티켓팅 프로그램 프로젝트
          </Typography>
        </Container>
      </Box>
    </Box>
  )
}
