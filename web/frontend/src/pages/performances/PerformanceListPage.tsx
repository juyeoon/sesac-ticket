import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, Chip, CircularProgress, Container, Stack, Typography } from '@mui/material'
import { useSearchParams } from 'react-router-dom'
import { PerformanceCard } from '../../components/performances/PerformanceCard'
import { performanceApi } from './performanceApi'
import { CATEGORIES } from '../../mocks/data/performances'

export default function PerformanceListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const keyword = searchParams.get('keyword') ?? ''
  const category = searchParams.get('category') ?? '전체'

  const { data, isLoading, isError } = useQuery({
    queryKey: ['performances', keyword],
    queryFn: () => (keyword ? performanceApi.search(keyword) : performanceApi.list()),
  })

  const filtered = useMemo(() => {
    const content = data?.content ?? []
    if (category === '전체') return content
    return content.filter((p) => p.category.name === category)
  }, [data, category])

  const handleCategoryClick = (next: string) => {
    const params = new URLSearchParams(searchParams)
    if (next === '전체') params.delete('category')
    else params.set('category', next)
    setSearchParams(params)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 5 }}>
      <Typography variant="h3" sx={{ mb: 0.5 }}>
        {keyword ? `"${keyword}" 검색 결과` : '공연 목록'}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        보고 싶은 공연을 골라보세요.
      </Typography>

      <Stack direction="row" spacing={1} sx={{ mb: 4, flexWrap: 'wrap', rowGap: 1 }}>
        {['전체', ...CATEGORIES].map((c) => (
          <Chip
            key={c}
            label={c}
            onClick={() => handleCategoryClick(c)}
            color={category === c ? 'primary' : undefined}
            variant={category === c ? 'filled' : 'outlined'}
          />
        ))}
      </Stack>

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
