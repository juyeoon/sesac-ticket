import { useQuery } from '@tanstack/react-query'
import { Box, Card, CardContent, Chip, CircularProgress, Container, Pagination, Stack, Typography } from '@mui/material'
import dayjs from 'dayjs'
import { Link as RouterLink, useSearchParams } from 'react-router-dom'
import { SUPPORT_CATEGORIES } from '../../mocks/data/support'
import { supportApi } from './supportApi'

const PAGE_SIZE = 6

export default function SupportListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = searchParams.get('category') ?? '전체'
  const page = Number(searchParams.get('page') ?? '0')

  const { data, isLoading, isError } = useQuery({
    queryKey: ['support-posts', category, page],
    queryFn: () => supportApi.list(page, PAGE_SIZE, category === '전체' ? undefined : category),
  })

  const handleCategoryClick = (next: string) => {
    const params = new URLSearchParams(searchParams)
    if (next === '전체') params.delete('category')
    else params.set('category', next)
    params.delete('page')
    setSearchParams(params)
  }

  const handlePageChange = (nextPage: number) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', String(nextPage - 1))
    setSearchParams(params)
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.totalElements / PAGE_SIZE)) : 1

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Typography variant="h3" sx={{ mb: 0.5 }}>
        고객센터
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        공지사항과 자주 묻는 질문을 확인해보세요.
      </Typography>

      <Stack direction="row" spacing={1} sx={{ mb: 3, flexWrap: 'wrap', rowGap: 1 }}>
        {['전체', ...SUPPORT_CATEGORIES].map((c) => (
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
          게시글 목록을 불러오지 못했습니다.
        </Typography>
      )}

      {!isLoading && !isError && (data?.content.length ?? 0) === 0 && (
        <Typography color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
          등록된 게시글이 없어요.
        </Typography>
      )}

      <Stack spacing={1.5} sx={{ mb: 4 }}>
        {data?.content.map((post) => (
          <Card
            key={post.id}
            component={RouterLink}
            to={`/support/${post.id}`}
            sx={{
              display: 'block',
              textDecoration: 'none',
              color: 'inherit',
              transition: 'border-color 0.15s ease',
              '&:hover': { borderColor: 'text.primary' },
            }}
          >
            <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
              <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', minWidth: 0 }}>
                {post.category && <Chip size="small" label={post.category} />}
                <Typography variant="subtitle1" sx={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {post.title}
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ flexShrink: 0 }}>
                {dayjs(post.createdAt).format('YYYY.MM.DD')}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Stack>

      {(data?.totalElements ?? 0) > PAGE_SIZE && (
        <Stack direction="row" sx={{ justifyContent: 'center' }}>
          <Pagination count={totalPages} page={page + 1} onChange={(_, p) => handlePageChange(p)} />
        </Stack>
      )}
    </Container>
  )
}
