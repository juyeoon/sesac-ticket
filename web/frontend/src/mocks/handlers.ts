import type { HttpHandler } from 'msw'
import { authHandlers } from './handlers/auth'

/**
 * 화면별 mock 핸들러를 이 배열에 추가한다.
 * docs/api-contract.md(구글시트 api 설계서 기준) 의 Endpoint/응답 형식을 그대로 따를 것 —
 * 나중에 실제 백엔드로 바꿀 때 baseURL만 교체하면 되도록.
 */
export const handlers: HttpHandler[] = [...authHandlers]
