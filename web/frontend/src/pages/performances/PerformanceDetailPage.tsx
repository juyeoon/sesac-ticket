import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Container,
  Divider,
  IconButton,
  Stack,
  Typography,
} from '@mui/material'
import FavoriteIcon from '@mui/icons-material/Favorite'
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder'
import ShareOutlinedIcon from '@mui/icons-material/ShareOutlined'
import dayjs from 'dayjs'
import { useNavigate, useParams } from 'react-router-dom'
import { PlaceholderImage } from '../../components/common/PlaceholderImage'
import { StatusBadge } from '../../components/performances/StatusBadge'
import { ShareDialog } from '../../components/performances/ShareDialog'
import { useAuth } from '../../auth/AuthContext'
import { useRequireAuth } from '../../auth/useRequireAuth'
import { performanceApi } from './performanceApi'
import { favoritesApi } from '../mypage/favoritesApi'

function formatDate(iso: string) {
  return dayjs(iso).format('YYYY.MM.DD')
}

export default function PerformanceDetailPage() {
  const { performanceId } = useParams()
  const id = Number(performanceId)
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const requireAuth = useRequireAuth()
  const queryClient = useQueryClient()

  const [shareOpen, setShareOpen] = useState(false)
  const [shareUrl, setShareUrl] = useState<string | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['performance', id],
    queryFn: () => performanceApi.detail(id),
  })

  const { data: favorites } = useQuery({
    queryKey: ['favorites'],
    queryFn: favoritesApi.list,
    enabled: isAuthenticated,
  })
  const isFavorited = favorites?.content.includes(id) ?? false

  const favoriteMutation = useMutation({
    mutationFn: async (): Promise<{ favorited: boolean }> =>
      isFavorited ? favoritesApi.remove(id) : favoritesApi.add(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['favorites'] }),
  })

  const shareMutation = useMutation({
    mutationFn: () => performanceApi.shareLink(id),
    onSuccess: async ({ shareUrl: url }) => {
      setShareUrl(url)
      setShareOpen(true)
      try {
        await navigator.clipboard.writeText(url)
      } catch {
        // 클립보드 권한이 없어도 다이얼로그에서 다시 복사할 수 있으니 무시
      }
    },
  })

  if (isLoading) return null
  if (isError || !data) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Typography color="error">공연 정보를 불러오지 못했습니다.</Typography>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={4}>
        <Box sx={{ width: { xs: '100%', sm: 280 }, flexShrink: 0 }}>
          <PlaceholderImage aspectRatio="3 / 4" iconSize={56} />
        </Box>

        <Box sx={{ flex: 1 }}>
          <Stack direction="row" spacing={1} sx={{ mb: 1.5 }}>
            <StatusBadge status={data.status} />
          </Stack>
          <Typography variant="h2" sx={{ mb: 3 }}>
            {data.title}
          </Typography>

          <Stack spacing={1.5} sx={{ mb: 3 }}>
            <InfoRow label="공연 종류" value={data.category.name} />
            <InfoRow label="공연장" value={`${data.venue.name} (${data.venue.address})`} />
            <InfoRow
              label="예매 기간"
              value={`${formatDate(data.ticketOpenAt)} - ${formatDate(data.ticketCloseAt)}`}
            />
            <InfoRow
              label="가격"
              value={`${data.priceInfo.minPrice.toLocaleString()}원 ~ ${data.priceInfo.maxPrice.toLocaleString()}원`}
            />
            <InfoRow label="관람 시간" value={`${data.runningTimeMin}분`} />
            <InfoRow label="관람 연령" value={data.ageLimit} />
          </Stack>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 3, whiteSpace: 'pre-line' }}>
            {data.description}
          </Typography>

          <Stack direction="row" spacing={1.5}>
            <Button
              variant="contained"
              size="large"
              onClick={() => requireAuth(() => navigate(`/performances/${id}/schedules`))}
            >
              예매하기
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<ShareOutlinedIcon />}
              onClick={() => shareMutation.mutate()}
            >
              공유하기
            </Button>
            <IconButton
              onClick={() => requireAuth(() => favoriteMutation.mutate())}
              sx={{ border: 1, borderColor: 'grey.200' }}
              aria-label={isFavorited ? '관심 공연 해제' : '관심 공연 등록'}
            >
              {isFavorited ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
            </IconButton>
          </Stack>
        </Box>
      </Stack>

      <Divider sx={{ my: 5 }} />

      <PlaceholderImage aspectRatio="16 / 9" iconSize={56} />

      <ShareDialog open={shareOpen} onClose={() => setShareOpen(false)} shareUrl={shareUrl} />
    </Container>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <Stack direction="row" spacing={2}>
      <Typography variant="body2" sx={{ width: 88, flexShrink: 0, fontWeight: 600 }}>
        {label}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {value}
      </Typography>
    </Stack>
  )
}
