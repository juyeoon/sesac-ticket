import { Box, Card, CardContent, Stack, Typography } from '@mui/material'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { Link as RouterLink } from 'react-router-dom'
import { PlaceholderImage } from '../common/PlaceholderImage'
import { StatusBadge } from './StatusBadge'
import type { PerformanceListItem } from '../../pages/performances/performanceApi'

export function PerformanceCard({ performance }: { performance: PerformanceListItem }) {
  return (
    <Card
      component={RouterLink}
      to={`/performances/${performance.id}`}
      sx={{
        display: 'block',
        textDecoration: 'none',
        color: 'inherit',
        height: '100%',
        transition: 'border-color 0.15s ease',
        '&:hover': { borderColor: 'text.primary' },
      }}
    >
      <Box sx={{ p: 1.5, pb: 0 }}>
        <PlaceholderImage aspectRatio="4 / 3" />
      </Box>
      <CardContent>
        <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
          <StatusBadge status={performance.status} />
        </Stack>
        <Typography variant="h6" sx={{ mb: 0.5 }}>
          {performance.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {performance.venue.name}
          {performance.dateFrom && performance.dateTo && ` · ${performance.dateFrom} ~ ${performance.dateTo}`}
        </Typography>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', color: 'text.primary' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            예매하러 가기
          </Typography>
          <ArrowForwardIcon sx={{ fontSize: 16 }} />
        </Stack>
      </CardContent>
    </Card>
  )
}
