import { api } from '../../api/client'

export const authApi = {
  requestEmailVerification: (email: string) =>
    api.post<{ sent: boolean }>('/auth/email/verify-request', { email }),
  signup: (email: string, password: string, nickname: string) =>
    api.post<{ userId: number }>('/auth/signup', { email, password, nickname }),
  requestPasswordReset: (email: string) =>
    api.post<{ sent: boolean }>('/auth/password/reset-request', { email }),
  resetPassword: (resetToken: string, newPassword: string) =>
    api.post<{ reset: boolean }>('/auth/password/reset', { resetToken, newPassword }),
}
