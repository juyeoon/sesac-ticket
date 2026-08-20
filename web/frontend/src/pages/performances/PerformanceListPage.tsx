import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, ButtonBase, CircularProgress, Container, Stack, Typography } from '@mui/material'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import MusicNoteOutlinedIcon from '@mui/icons-material/MusicNoteOutlined'
import TheaterComedyOutlinedIcon from '@mui/icons-material/TheaterComedyOutlined'
import MuseumOutlinedIcon from '@mui/icons-material/MuseumOutlined'
import CelebrationOutlinedIcon from '@mui/icons-material/CelebrationOutlined'
import AppsOutlinedIcon from '@mui/icons-material/AppsOutlined'
import type { SvgIconComponent } from '@mui/icons-material'
import { Link as RouterLink, useSearchParams } from 'react-router-dom'
import { PerformanceCard } from '../../components/performances/PerformanceCard'
import { PlaceholderImage } from '../../components/common/PlaceholderImage'
import { performanceApi, type PerformanceListItem } from './performanceApi'

function categoryIcon(name: string): SvgIconComponent {
  if (name.includes('콘서트') || name.includes('음악')) return MusicNoteOutlinedIcon
  if (name.includes('뮤지컬') || name.includes('연극')) return TheaterComedyOutlinedIcon
  if (name.includes('전시')) return MuseumOutlinedIcon
  return CelebrationOutlinedIcon
}

function HeroBanner({ performance }: { performance: PerformanceListItem }) {
  return (
    <Box
      component={RouterLink}
      to={`/performances/${performance.id}`}
      sx={{
        position: 'relative',
        display: 'block',
        height: { xs: 200, sm: 260 },
        overflow: 'hidden',
        textDecoration: 'none',
        flex: 1,
      }}
    >
      <PlaceholderImage seed={String(performance.id)} fill />
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(20,18,24,0.8) 0%, rgba(20,18,24,0.15) 60%, rgba(20,18,24,0) 100%)',
        }}
      />
      <Stack sx={{ position: 'absolute', left: 20, right: 20, bottom: 18 }} spacing={0.5}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.75)', fontWeight: 600 }}>
          {performance.category.name}
        </Typography>
        <Typography variant="h5" sx={{ color: 'white', fontWeight: 700 }}>
          {performance.title}
        </Typography>
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', color: 'white' }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            예매하러 가기
          </Typography>
          <ArrowForwardIcon sx={{ fontSize: 16 }} />
        </Stack>
      </Stack>
    </Box>
  )
}

/** 카테고리 아이콘 배지 — 야놀자/인터파크 티켓 홈 화면의 카테고리 진입점 패턴을 참고(모양은 각진 사각형으로 통일) */
function CategoryRail({
  categories,
  selected,
  onSelect,
}: {
  categories: string[]
  selected: string
  onSelect: (name: string) => void
}) {
  const items = [{ name: '전체', Icon: AppsOutlinedIcon }, ...categories.map((c) => ({ name: c, Icon: categoryIcon(c) }))]
  return (
    <Stack direction="row" spacing={3} sx={{ mb: 4, overflowX: 'auto', pb: 0.5 }}>
      {items.map(({ name, Icon }) => {
        const isSelected = selected === name
        return (
          <ButtonBase
            key={name}
            onClick={() => onSelect(name)}
            aria-label={`${name} 카테고리`}
            aria-pressed={isSelected}
            sx={{ flexDirection: 'column', gap: 0.75, p: 0.5, flexShrink: 0 }}
          >
            <Box
              sx={{
                width: 56,
                height: 56,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: isSelected ? 'text.primary' : 'grey.50',
                color: isSelected ? 'background.paper' : 'text.secondary',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon sx={{ fontSize: 24 }} />
            </Box>
            <Typography variant="caption" sx={{ fontWeight: isSelected ? 700 : 500, color: isSelected ? 'text.primary' : 'text.secondary' }}>
              {name}
            </Typography>
          </ButtonBase>
        )
      })}
    </Stack>
  )
}

export default function PerformanceListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const keyword = searchParams.get('keyword') ?? ''
  const category = searchParams.get('category') ?? '전체'

  const { data, isLoading, isError } = useQuery({
    queryKey: ['performances', keyword],
    queryFn: () => (keyword ? performanceApi.search(keyword) : performanceApi.list()),
  })

  const content = useMemo(() => data?.content ?? [], [data])

  // 카테고리 목록을 조회하는 별도 API가 없어서, 지금 불러온 목록에 실제로 존재하는 값으로 구성한다.
  const categories = useMemo(
    () => Array.from(new Set(content.map((p) => p.category.name))),
    [content],
  )

  const filtered = useMemo(() => {
    if (category === '전체') return content
    return content.filter((p) => p.category.name === category)
  }, [content, category])

  const handleCategoryClick = (next: string) => {
    const params = new URLSearchParams(searchParams)
    if (next === '전체') params.delete('category')
    else params.set('category', next)
    setSearchParams(params)
  }

  // 카테고리를 바꿔도 히어로 배너는 그대로 고정 — 검색 중일 때만 숨긴다.
  const showHero = !keyword && content.length > 0

  return (
    <Container maxWidth="lg" sx={{ py: 5 }}>
      {showHero && (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 5 }}>
          {content.slice(0, 2).map((p) => (
            <HeroBanner key={p.id} performance={p} />
          ))}
        </Stack>
      )}

      <Typography variant="h3" sx={{ mb: 0.5 }}>
        {keyword ? `"${keyword}" 검색 결과` : '지금 예매 가능한 공연'}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        보고 싶은 공연을 골라보세요.
      </Typography>

      <CategoryRail categories={categories} selected={category} onSelect={handleCategoryClick} />

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Typography color="error" sx={{ py: 8, textAlign: 'center' }}>
          공연 목록을 불러오지 못했습니다.
        </Typography>
      )}

      {!isLoading && !isError && filtered.length === 0 && (
        <Typography color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
          조건에 맞는 공연이 없어요.
        </Typography>
      )}

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)', lg: 'repeat(4, 1fr)' },
          gap: 3,
        }}
      >
        {filtered.map((p) => (
          <PerformanceCard key={p.id} performance={p} />
        ))}
      </Box>
    </Container>
  )
}
