import { adminApiClient } from '../../api/adminClient'

export interface AdminAccessTokenResult {
  accessToken: string
  tokenType: string
  expiresIn: number
}

export const adminApi = {
  login: (adminId: string, password: string) =>
    adminApiClient.post<AdminAccessTokenResult>('/admin/auth/login', { adminId, password }),
}
