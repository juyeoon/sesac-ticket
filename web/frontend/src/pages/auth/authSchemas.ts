import { z } from 'zod'

const emailField = z.string().min(1, '이메일을 입력해주세요.').email('이메일 형식이 올바르지 않습니다.')

const passwordField = z
  .string()
  .min(8, '8자리 이상 입력해주세요.')
  .regex(/[A-Za-z]/, '영문을 포함해주세요.')
  .regex(/[0-9]/, '숫자를 포함해주세요.')

export const loginSchema = z.object({
  email: emailField,
  password: z.string().min(1, '비밀번호를 입력해주세요.'),
})
export type LoginFormValues = z.infer<typeof loginSchema>

export const signupSchema = z
  .object({
    email: emailField,
    nickname: z.string().min(2, '2자 이상 입력해주세요.').max(20, '20자 이하로 입력해주세요.'),
    password: passwordField,
    passwordConfirm: z.string(),
  })
  .refine((values) => values.password === values.passwordConfirm, {
    message: '비밀번호가 일치하지 않습니다.',
    path: ['passwordConfirm'],
  })
export type SignupFormValues = z.infer<typeof signupSchema>

export const passwordResetSchema = z
  .object({
    email: emailField,
    verificationCode: z.string().min(1, '이메일로 전송된 인증 코드를 입력해주세요.'),
    newPassword: passwordField,
    newPasswordConfirm: z.string(),
  })
  .refine((values) => values.newPassword === values.newPasswordConfirm, {
    message: '비밀번호가 일치하지 않습니다.',
    path: ['newPasswordConfirm'],
  })
export type PasswordResetFormValues = z.infer<typeof passwordResetSchema>
