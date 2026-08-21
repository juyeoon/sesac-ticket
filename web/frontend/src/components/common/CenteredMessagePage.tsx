import { Box, Button, Container, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

interface CenteredMessagePageProps {
  eyebrow: string
  title: string
  description: string
  ctaHref?: string
  ctaLabel?: string
}

export function CenteredMessagePage({
  eyebrow,
  title,
  description,
  ctaHref = '/',
  ctaLabel = '홈으로 가기',
}: CenteredMessagePageProps) {
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '60vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: 1.5,
        }}
      >
        <Typography variant="overline" color="text.secondary">
          {eyebrow}
        </Typography>
        <Typography variant="h3">{title}</Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
        <Button component={RouterLink} to={ctaHref} variant="contained" size="large">
          {ctaLabel}
        </Button>
      </Box>
    </Container>
  )
}
