import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'

interface ShareDialogProps {
  open: boolean
  onClose: () => void
  shareUrl: string | null
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}

export function ShareDialog({ open, onClose, shareUrl }: ShareDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        공유하기
        <IconButton onClick={onClose} size="small">
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          링크가 복사되었습니다.
        </Typography>
        <Typography
          variant="body2"
          sx={{ p: 1.5, bgcolor: 'grey.50', borderRadius: 2, wordBreak: 'break-all' }}
        >
          {shareUrl}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button variant="contained" fullWidth onClick={() => shareUrl && copyToClipboard(shareUrl)}>
          링크 복사
        </Button>
      </DialogActions>
    </Dialog>
  )
}
