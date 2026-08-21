import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Box, Card, CardContent, CircularProgress, IconButton, Stack, Typography } from '@mui/material'
import FavoriteIcon from '@mui/icons-material/Favorite'
import { Link as RouterLink } from 'react-router-dom'
import { PlaceholderImage } from '../../components/common/PlaceholderImage'
import { favoritesApi } from './favoritesApi'

export default function MyFavoritesPage() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['favorites'],
    queryFn: favoritesApi.list,
  })

  const removeMutation = useMutation({
    mutationFn: (performanceId: number) => favoritesApi.remove(performanceId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['favorites'] }),
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  const favorited = data?.content ?? []

  if (favorited.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
        아직 관심 등록한 공연이 없어요.
      </Typography>
    )
  }

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
        gap: 3,
      }}
    >
      {favorited.map((p) => (
        <Card key={p.performanceId} sx={{ height: '100%' }}>
          <Box sx={{ p: 1.5, pb: 0, position: 'relative' }}>
            <Box component={RouterLink} to={`/performances/${p.performanceId}`} sx={{ display: 'block' }}>
              <PlaceholderImage aspectRatio="4 / 3" seed={String(p.performanceId)} />
            </Box>
            <IconButton
              size="small"
              onClick={() => removeMutation.mutate(p.performanceId)}
              disabled={removeMutation.isPending}
              sx={{ position: 'absolute', top: 20, right: 20, bgcolor: 'background.paper', border: 1, borderColor: 'grey.200' }}
              aria-label="관심 공연 해제"
            >
              <FavoriteIcon color="error" fontSize="small" />
            </IconButton>
          </Box>
          <CardContent component={RouterLink} to={`/performances/${p.performanceId}`} sx={{ display: 'block', textDecoration: 'none', color: 'inherit' }}>
            <Stack direction="row" spacing={1}>
              <Typography variant="h6">{p.title}</Typography>
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Box>
  )
}
