import { useState } from 'react'
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, Typography } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import CheckIcon from '@mui/icons-material/Check'

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
  const [copied, setCopied] = useState(false)

  const handleClose = () => {
    setCopied(false)
    onClose()
  }

  const handleCopy = async () => {
    if (!shareUrl) return
    if (await copyToClipboard(shareUrl)) {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    }
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        공유하기
        <IconButton onClick={handleClose} size="small">
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ p: 1.5, bgcolor: 'grey.50', wordBreak: 'break-all' }}>
          {shareUrl}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          variant="contained"
          fullWidth
          onClick={handleCopy}
          startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
          sx={{
            transition: 'background-color 0.2s ease',
            ...(copied && {
              bgcolor: 'success.main',
              '&:hover': { bgcolor: 'success.main' },
            }),
          }}
        >
          {copied ? '복사 완료' : '링크 복사'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
