import { api } from '../../api/client'

export interface SupportPostItem {
  id: number
  title: string
  category: string | null
  createdAt: string
}

export interface SupportPostDetail extends SupportPostItem {
  content: string
}

export const supportApi = {
  list: (page: number, size: number, category?: string) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) })
    if (category) params.set('category', category)
    return api.get<{ content: SupportPostItem[]; totalElements: number }>(`/support/posts?${params}`)
  },
  detail: (postId: number) => api.get<SupportPostDetail>(`/support/posts/${postId}`),
}
