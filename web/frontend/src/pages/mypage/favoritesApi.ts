import { api } from '../../api/client'

export const favoritesApi = {
  list: () => api.get<{ content: number[]; totalElements: number }>('/users/me/favorites'),
  add: (performanceId: number) =>
    api.post<{ favorited: true }>(`/users/me/favorites/${performanceId}`),
  remove: (performanceId: number) =>
    api.delete<{ favorited: false }>(`/users/me/favorites/${performanceId}`),
}
