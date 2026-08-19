import {
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material'

/**
 * 임시 테마 미리보기 페이지.
 * 실제 화면(로그인/공연목록 등)이 라우트로 들어오기 전까지
 * 테마 토큰이 의도대로 적용되는지 확인하는 용도.
 */
function App() {
  return (
    <Box>
      <AppBar position="static">
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            새싹티켓
          </Typography>
          <Button variant="outlined" color="primary">
            로그인
          </Button>
          <Button variant="contained" color="primary">
            회원가입
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ py: 6 }}>
        <Typography variant="h2" gutterBottom>
          디자인 시스템 미리보기
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          docs/design-system.md 의 토큰이 MUI 테마에 정상 반영됐는지 확인하는 임시 화면입니다.
        </Typography>

        <Stack direction="row" spacing={1.5} sx={{ mb: 4 }}>
          <Chip label="전체" color="primary" />
          <Chip label="콘서트" variant="outlined" />
          <Chip label="뮤지컬" variant="outlined" />
          <Chip label="전시" variant="outlined" />
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 4 }}>
          <Card sx={{ flex: 1, bgcolor: 'accent.blueSoft', border: 'none' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                예매 오픈
              </Typography>
              <Typography variant="h4">128건</Typography>
            </CardContent>
          </Card>
          <Card sx={{ flex: 1, bgcolor: 'accent.greenSoft', border: 'none' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                예매 완료
              </Typography>
              <Typography variant="h4">34,750건</Typography>
            </CardContent>
          </Card>
          <Card sx={{ flex: 1, bgcolor: 'accent.yellowSoft', border: 'none' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                총 매출
              </Typography>
              <Typography variant="h4">₩231,224,000</Typography>
            </CardContent>
          </Card>
        </Stack>

        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              2025 AKMU STANDING CONCERT [악동들]
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              예매 기간 2026.08.08 - 2026.08.27 · 관람연령 만 12세 이상
            </Typography>
            <Stack direction="row" spacing={1.5}>
              <Button variant="contained" size="large">
                예매하기
              </Button>
              <Button variant="outlined" size="large">
                공유하기
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Container>
    </Box>
  )
}

export default App
