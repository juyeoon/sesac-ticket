# 새싹티켓 프론트엔드 (`web/frontend`)

티켓 예매 서비스 새싹티켓의 프론트엔드입니다. `feature/ui` 브랜치에서 작업 중이며, 백엔드 API가 준비되기 전까지 **MSW(Mock Service Worker)로 실제 동작하는 목업 API**를 붙여서 화면을 구현합니다.

> 화면/테스트 방법은 [`docs/testing-guide.md`](./docs/testing-guide.md), 색상·타이포 등 디자인 규칙은 [`docs/design-system.md`](./docs/design-system.md)를 참고하세요.
> 백엔드 팀과 같이 결정해야 할 것들은 [`../../docs/backend-decisions-needed.md`](../../docs/backend-decisions-needed.md)에 정리해뒀습니다.

## 기술 스택

| 분류 | 선택 | 비고 |
|---|---|---|
| 빌드 도구 | Vite | |
| 언어 | TypeScript | |
| UI 프레임워크 | React 19 | |
| 컴포넌트 라이브러리 | MUI (v9) | `src/theme/theme.ts`에 커스텀 테마 |
| 라우팅 | react-router-dom v7 | `src/routes/AppRoutes.tsx` |
| 서버 상태 관리 | TanStack Query | 캐싱, 폴링(대기열/Hold 타이머 등) |
| 폼 | react-hook-form + zod | 유효성 검증 |
| 날짜/시간 | dayjs | |
| API 목업 | MSW | 실제 fetch 흐름 그대로 인터셉트. 나중에 baseURL만 바꾸면 실 백엔드로 전환 |
| 폰트 | Pretendard (CDN) | `index.html` 참고 |
| 린트 | oxlint | `npm run lint` |

## 시작하기

```bash
git checkout feature/ui
git pull
cd web/frontend
npm install
npm run dev
```

`http://localhost:5173` 접속. 로그인 등 테스트 방법은 [`docs/testing-guide.md`](./docs/testing-guide.md)를 확인하세요.

## 폴더 구조

```
src/
├── api/          공용 fetch 클라이언트 (baseURL, 에러 처리)
├── auth/         로그인 상태 Context, 로그인 유도 모달
├── components/   화면 간 공유 컴포넌트 (layout, auth, common)
├── mocks/        MSW 핸들러 — 화면별로 handlers/ 하위에 파일 분리
├── pages/        라우트에 매핑되는 실제 화면
├── routes/       라우트 표 (AppRoutes.tsx)
└── theme/        디자인 토큰 + MUI 테마
```

## 작업 진행 상황

Phase 단위 체크포인트로 진행 중입니다. 상세 내용은 [`docs/testing-guide.md`](./docs/testing-guide.md)의 진행 상황 표를 참고하세요.

- [x] Phase 0 — 공통 레이아웃, 인증 상태 관리 기반
- [x] Phase 1 — 로그인 / 회원가입 / 비밀번호 재설정
- [x] Phase 2 — 공연 목록 / 상세 / 회차 선택
- [x] Phase 3 — 대기열 / 좌석 선택·Hold / 무통장입금 예매
- [ ] Phase 4 — 마이페이지
- [ ] Phase 5 — 관리자 로그인 / 고객센터
