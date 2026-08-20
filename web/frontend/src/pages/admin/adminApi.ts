import { api } from '../../api/client'

export interface AdminAccessTokenResult {
  accessToken: string
  tokenType: string
  expiresIn: number
}

export const adminApi = {
  login: (adminId: string, password: string) =>
    api.post<AdminAccessTokenResult>('/admin/auth/login', { adminId, password }),
}
