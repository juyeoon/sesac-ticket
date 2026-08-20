import { api } from '../../api/client'

export interface FavoriteItem {
  performanceId: number
  title: string
  thumbnailUrl: string | null
}

export const favoritesApi = {
  list: () => api.get<{ content: FavoriteItem[]; totalElements: number }>('/users/me/favorites'),
  add: (performanceId: number) =>
    api.post<{ favorited: true }>(`/users/me/favorites/${performanceId}`),
  remove: (performanceId: number) =>
    api.delete<{ favorited: false }>(`/users/me/favorites/${performanceId}`),
}
