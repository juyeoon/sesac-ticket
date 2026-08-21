import { api } from '../../api/client'

export interface MyInfoPatch {
  nickname: string
  gender: string
  ageRange: string
  verificationCode: string
}

export const userApi = {
  update: (patch: MyInfoPatch) => api.patch<{ updated: boolean }>('/users/me', patch),
}
