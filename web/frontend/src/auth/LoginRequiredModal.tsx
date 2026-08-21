import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'

interface LoginRequiredModalProps {
  open: boolean
  onClose: () => void
}

/** docs/design-system.md 8장 규칙: 버튼 비활성화 대신 모달로 로그인 유도. */
export function LoginRequiredModal({ open, onClose }: LoginRequiredModalProps) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>로그인이 필요합니다</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary">
          이 기능은 로그인 후 이용할 수 있어요.
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} color="inherit">
          취소
        </Button>
        <Button
          variant="contained"
          onClick={() => {
            onClose()
            navigate('/login', { state: { from: location } })
          }}
        >
          로그인하러 가기
        </Button>
      </DialogActions>
    </Dialog>
  )
}
