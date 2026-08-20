import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import PlaceOutlinedIcon from '@mui/icons-material/PlaceOutlined'
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
        transition: 'border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease',
        '&:hover': {
          borderColor: 'text.primary',
          boxShadow: '0 12px 24px -12px rgba(33,33,33,0.28)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <Box sx={{ p: 1.5, pb: 0 }}>
        <PlaceholderImage aspectRatio="4 / 3" seed={String(performance.id)} />
      </Box>
      <CardContent>
        <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
          <StatusBadge status={performance.status} />
          <Chip size="small" variant="outlined" label={performance.category.name} />
        </Stack>
        <Typography variant="h6" sx={{ mb: 0.5 }}>
          {performance.title}
        </Typography>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', mb: 2, color: 'text.secondary' }}>
          <PlaceOutlinedIcon sx={{ fontSize: 16 }} />
          <Typography variant="body2" color="text.secondary">
            {performance.venue.name}
            {performance.dateFrom && performance.dateTo && ` · ${performance.dateFrom} ~ ${performance.dateTo}`}
          </Typography>
        </Stack>
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
