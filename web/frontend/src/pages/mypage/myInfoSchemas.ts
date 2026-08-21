import { z } from 'zod'

export const myInfoSchema = z.object({
  nickname: z.string().min(2, '2자 이상 입력해주세요.').max(20, '20자 이하로 입력해주세요.'),
  gender: z.string().min(1, '성별을 선택해주세요.'),
  ageRange: z.string().min(1, '나이대를 선택해주세요.'),
  verificationCode: z.string().min(1, '이메일로 전송된 인증 코드를 입력해주세요.'),
})
export type MyInfoFormValues = z.infer<typeof myInfoSchema>
