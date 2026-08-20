import { useQuery } from '@tanstack/react-query'
import { Box, Button, Chip, CircularProgress, Container, Divider, Stack, Typography } from '@mui/material'
import dayjs from 'dayjs'
import { Link as RouterLink, useParams } from 'react-router-dom'
import { supportApi } from './supportApi'

export default function SupportDetailPage() {
  const { postId } = useParams()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['support-post', postId],
    queryFn: () => supportApi.detail(Number(postId)),
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (isError || !data) {
    return (
      <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
        <Typography color="error">게시글을 찾을 수 없습니다.</Typography>
      </Container>
    )
  }

  return (
    <Container maxWidth="sm" sx={{ py: 5 }}>
      <Stack direction="row" spacing={1} sx={{ mb: 1.5 }}>
        {data.category && <Chip size="small" label={data.category} />}
      </Stack>
      <Typography variant="h4" sx={{ mb: 1 }}>
        {data.title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {dayjs(data.createdAt).format('YYYY.MM.DD (ddd) HH:mm')}
      </Typography>

      <Divider sx={{ mb: 3 }} />

      <Typography variant="body1" sx={{ mb: 5, whiteSpace: 'pre-line' }}>
        {data.content}
      </Typography>

      <Button component={RouterLink} to="/support" variant="outlined">
        목록으로
      </Button>
    </Container>
  )
}
