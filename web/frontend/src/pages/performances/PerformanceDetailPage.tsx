import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  IconButton,
  Stack,
  Typography,
} from '@mui/material'
import FavoriteIcon from '@mui/icons-material/Favorite'
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder'
import ShareOutlinedIcon from '@mui/icons-material/ShareOutlined'
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined'
import PlaceOutlinedIcon from '@mui/icons-material/PlaceOutlined'
import EventOutlinedIcon from '@mui/icons-material/EventOutlined'
import AccessTimeOutlinedIcon from '@mui/icons-material/AccessTimeOutlined'
import Diversity3OutlinedIcon from '@mui/icons-material/Diversity3Outlined'
import type { SvgIconComponent } from '@mui/icons-material'
import dayjs from 'dayjs'
import { useNavigate, useParams } from 'react-router-dom'
import { PlaceholderImage } from '../../components/common/PlaceholderImage'
import { StatusBadge } from '../../components/performances/StatusBadge'
import { ShareDialog } from '../../components/performances/ShareDialog'
import { useAuth } from '../../auth/AuthContext'
import { useRequireAuth } from '../../auth/useRequireAuth'
import { performanceApi } from './performanceApi'
import { favoritesApi } from '../mypage/favoritesApi'

function formatDate(iso: string | null | undefined) {
  return iso ? dayjs(iso).format('YYYY.MM.DD') : '미정'
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
  const isFavorited = favorites?.content.some((f) => f.performanceId === id) ?? false

  const favoriteMutation = useMutation({
    mutationFn: async (): Promise<{ favorited: boolean }> =>
      isFavorited ? favoritesApi.remove(id) : favoritesApi.add(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['favorites'] }),
  })

  // 실 백엔드엔 공유 링크 발급 API가 없음(share-link 엔드포인트 자체가 스펙에 없다고 확인됨) — 현재 페이지 URL을 그대로 공유 링크로 쓴다.
  const handleShare = async () => {
    const url = window.location.href
    setShareUrl(url)
    setShareOpen(true)
    try {
      await navigator.clipboard.writeText(url)
    } catch {
      // 클립보드 권한이 없어도 다이얼로그에서 다시 복사할 수 있으니 무시
    }
  }

  if (isLoading) return null
  if (isError || !data) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Typography color="error">공연 정보를 불러오지 못했습니다.</Typography>
      </Container>
    )
  }

  const seed = String(data.id)
  const posterUrl = data.images[0]?.imageUrl ?? null

  // 예매 가능 여부는 회차별 판매 상태(schedule.status)가 아니라 공연 전체의
  // status(ACTIVE/HIDDEN/ENDED)로 판단한다 — "예매하기"는 회차 선택 전
  // 공연 단위 진입 버튼이라 회차 단위 상태와는 별개다. 회차별 매진/마감
  // 처리는 ScheduleSelectPage의 회차 카드 쪽 책임이라 여기서는 건드리지 않는다.
  const isBookable = data.status === 'ACTIVE'
  const bookButtonLabel =
    data.status === 'ENDED'
      ? '예매가 종료되었습니다'
      : data.status === 'HIDDEN'
        ? '예매할 수 없는 공연입니다'
        : '예매하기'

  return (
    <Box>
      {/* 히어로 배너 — 포스터 아트를 배경으로 깔고 어두운 그러데이션 위에 타이틀을 얹는다 */}
      <Box sx={{ position: 'relative', height: { xs: 280, sm: 360 }, overflow: 'hidden' }}>
        <PlaceholderImage seed={seed} fill src={posterUrl} />
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(to top, rgba(20,18,24,0.82) 0%, rgba(20,18,24,0.25) 55%, rgba(20,18,24,0) 100%)',
          }}
        />
        <Container maxWidth="lg" sx={{ position: 'relative', height: '100%' }}>
          <Stack sx={{ position: 'absolute', left: { xs: 16, sm: 24 }, right: 16, bottom: 24 }} spacing={1.5}>
            <Stack direction="row" spacing={1}>
              {data.status && <StatusBadge status={data.status} />}
              <Chip size="small" label={data.category.name} sx={{ bgcolor: 'rgba(255,255,255,0.16)', color: 'white' }} />
            </Stack>
            <Typography variant="h2" sx={{ color: 'white', textShadow: '0 2px 12px rgba(0,0,0,0.35)' }}>
              {data.title}
            </Typography>
          </Stack>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 5 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={4}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack spacing={1.5} sx={{ mb: 4, p: 2.5, border: 1, borderColor: 'grey.100' }}>
              <InfoRow icon={CategoryOutlinedIcon} label="공연 종류" value={data.category.name} />
              <InfoRow icon={PlaceOutlinedIcon} label="공연장" value={`${data.venue.name} (${data.venue.address ?? '주소 미정'})`} />
              <InfoRow
                icon={EventOutlinedIcon}
                label="예매 기간"
                value={`${formatDate(data.ticketOpenAt)} - ${formatDate(data.ticketCloseAt)}`}
              />
              <InfoRow icon={AccessTimeOutlinedIcon} label="관람 시간" value={data.runningTimeMin ? `${data.runningTimeMin}분` : '미정'} />
              <InfoRow icon={Diversity3OutlinedIcon} label="관람 연령" value={data.ageLimit ?? '미정'} />
            </Stack>

            <Typography variant="h5" sx={{ mb: 2 }}>
              공연 소개
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4, whiteSpace: 'pre-line' }}>
              {data.description || '공연 소개가 아직 등록되지 않았어요.'}
            </Typography>

            <Divider sx={{ mb: 3 }} />
            <PlaceholderImage seed={`${seed}-poster`} aspectRatio="21 / 9" src={posterUrl} />
          </Box>

          {/* 예매 요약 카드 — 데스크톱에선 스크롤해도 따라오는 사이드 패널 */}
          <Box sx={{ width: { xs: '100%', md: 320 }, flexShrink: 0 }}>
            <Card sx={{ position: { md: 'sticky' }, top: { md: 96 } }}>
              <CardContent>
                <Typography variant="overline" color="text.secondary">
                  가격
                </Typography>
                <Typography variant="h4" sx={{ mb: 2 }}>
                  {data.priceInfo.minPrice.toLocaleString()}
                  <Typography component="span" variant="body1" color="text.secondary">
                    원 ~ {data.priceInfo.maxPrice.toLocaleString()}원
                  </Typography>
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Stack spacing={1.5} sx={{ mb: 3 }}>
                  {data.seatGrades.map((g) => (
                    <Stack key={g.grade} direction="row" sx={{ justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        {g.grade}석
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {g.price.toLocaleString()}원
                      </Typography>
                    </Stack>
                  ))}
                </Stack>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={!isBookable}
                  sx={{ mb: 1.5 }}
                  onClick={() => requireAuth(() => navigate(`/performances/${id}/schedules`))}
                >
                  {bookButtonLabel}
                </Button>
                <Stack direction="row" spacing={1.5}>
                  <Button variant="outlined" fullWidth startIcon={<ShareOutlinedIcon />} onClick={handleShare}>
                    공유하기
                  </Button>
                  <IconButton
                    onClick={() => requireAuth(() => favoriteMutation.mutate())}
                    sx={{ border: 1, borderColor: 'grey.200', borderRadius: 0 }}
                    aria-label={isFavorited ? '관심 공연 해제' : '관심 공연 등록'}
                  >
                    {isFavorited ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
                  </IconButton>
                </Stack>
              </CardContent>
            </Card>
          </Box>
        </Stack>
      </Container>

      <ShareDialog open={shareOpen} onClose={() => setShareOpen(false)} shareUrl={shareUrl} />
    </Box>
  )
}

function InfoRow({ icon: Icon, label, value }: { icon: SvgIconComponent; label: string; value: string }) {
  return (
    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
      <Icon sx={{ fontSize: 18, color: 'text.disabled', mt: '2px' }} />
      <Typography variant="body2" sx={{ width: 76, flexShrink: 0, fontWeight: 600 }}>
        {label}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {value}
      </Typography>
    </Stack>
  )
}
