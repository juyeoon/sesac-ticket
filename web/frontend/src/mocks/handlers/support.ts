import { http, HttpResponse } from 'msw'
import { supportPosts } from '../data/support'

const BASE = '/api/v1'

export const supportHandlers = [
  http.get(`${BASE}/support/posts`, ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page') ?? '0')
    const size = Number(url.searchParams.get('size') ?? '20')
    const category = url.searchParams.get('category')

    const filtered = category ? supportPosts.filter((p) => p.category === category) : supportPosts
    const sorted = [...filtered].sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    const content = sorted.slice(page * size, page * size + size).map(({ content: _content, ...item }) => item)

    return HttpResponse.json({ content, totalElements: sorted.length })
  }),

  http.get(`${BASE}/support/posts/:postId`, ({ params }) => {
    const post = supportPosts.find((p) => p.id === Number(params.postId))
    if (!post) {
      return HttpResponse.json(
        { message: '게시글을 찾을 수 없습니다.', errorCode: 'SUPPORT_POST_NOT_FOUND' },
        { status: 404 },
      )
    }
    return HttpResponse.json(post)
  }),
]
