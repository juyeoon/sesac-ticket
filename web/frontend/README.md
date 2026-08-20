# 새싹티켓 프론트엔드 (`web/frontend`)

티켓 예매 서비스 새싹티켓의 프론트엔드입니다. `feature/ui` 브랜치에서 작업 중이며, 백엔드 API가 실제로 붙기 전까지 **MSW(Mock Service Worker)로 실제 동작하는 목업 API**를 붙여서 화면을 구현합니다.

> 색상·타이포 등 디자인 규칙은 [`docs/design-system.md`](./docs/design-system.md).
> 백엔드 팀과 같이 결정해야 할 것들은 [`../../docs/backend-decisions-needed.md`](../../docs/backend-decisions-needed.md)(1차)와 [`../../docs/backend-decisions-followup-1.md`](../../docs/backend-decisions-followup-1.md)(2차).
> 세션별 작업 이력(로그)은 [`../../docs/frontend-worklog.md`](../../docs/frontend-worklog.md).
> 새 대화를 시작할 때는 [`../../docs/frontend-handoff.md`](../../docs/frontend-handoff.md)부터 읽을 것.

## 기술 스택 · 버전

| 분류 | 선택 | 버전 |
|---|---|---|
| 런타임 | Node.js | 20.19+ 또는 22+ 권장 (Vite 8 요구사항) |
| 패키지 매니저 | npm | 이 프로젝트 개발 환경 기준 11.x |
| 빌드 도구 | Vite | ^8.2.0 |
| 언어 | TypeScript | ~6.0.2 |
| UI 프레임워크 | React | ^19.2.8 |
| 컴포넌트 라이브러리 | MUI | ^9.3.1 (`@mui/material`, `@mui/icons-material`) — `src/theme/theme.ts`에 커스텀 테마 |
| 스타일 엔진 | Emotion | ^11.14.x (MUI 내부 의존성) |
| 라우팅 | react-router-dom | ^7.18.2 — `src/routes/AppRoutes.tsx` |
| 서버 상태 관리 | @tanstack/react-query | ^5.101.4 — 캐싱, 폴링(대기열/Hold 타이머) |
| 폼 | react-hook-form + zod + @hookform/resolvers | ^7.85.0 / ^4.4.3 / ^5.9.1 |
| 날짜/시간 | dayjs | ^1.11.23 (로케일 `ko` 적용, `src/main.tsx`) |
| API 목업 | msw | ^2.15.0 — 실제 fetch 흐름 그대로 인터셉트, 나중에 baseURL만 바꾸면 실 백엔드로 전환 |
| 폰트 | Pretendard (CDN) | `index.html`의 `<link>` 참고, 별도 패키지 없음 |
| 린트 | oxlint | ^1.75.0 (`npm run lint`) |

정확한 버전은 항상 [`package.json`](./package.json)이 기준입니다 — 위 표는 참고용.

## 실행 방법

```bash
cd web/frontend
npm install
npm run dev       # http://localhost:5173
```

```bash
npm run build     # tsc -b && vite build — 타입체크 + 프로덕션 빌드
npm run lint      # oxlint
npm run preview   # 빌드 결과물 미리보기
```

## 프로젝트를 처음 받을 때 — 시나리오별 clone 방법

### 1) 프론트 화면만 확인하고 싶을 때

MSW mock으로 전부 동작하므로 이것만 있으면 됩니다.

```bash
git clone https://github.com/juyeoon/sesac-ticket.git
cd sesac-ticket
git checkout feature/ui
cd web/frontend
npm install
npm run dev
```

### 2) 프로젝트 전체(백엔드 코드도 같이) 로컬에서 보고 싶을 때

백엔드(`feature/integration2`)를 **완전히 독립된 별도 clone**으로 옆에 받습니다 (같은 저장소, 다른 브랜치라 하나의 작업 폴더에 동시에 체크아웃할 수 없어서 이렇게 분리함).

```bash
# 위 1)로 sesac-ticket/web/frontend까지 받은 상태에서 이어서
cd ../..                      # sesac-ticket/ 로 이동
git clone --branch feature/integration2 https://github.com/juyeoon/sesac-ticket.git backend
```

결과 구조:
```
sesac-ticket/
├── web/frontend/   ← feature/ui, 지금 이 프론트. git add/commit/push는 항상 여기서
├── backend/        ← feature/integration2, 완전히 별개 저장소(자체 .git). git pull은 여기서
│   └── api/app/...     실제 백엔드 코드
└── docs/
```

- `backend/`는 루트 `.gitignore`에 등록돼 있어서 `feature/ui` 쪽 git 작업엔 절대 안 잡힙니다.
- 백엔드 최신화: `cd backend && git pull`
- 백엔드를 실제로 띄우려면 `backend/api/.env.example`을 복사해 `.env`를 만들고 DB/Valkey 접속 정보, `JWT_SECRET`, SMTP 계정을 채운 뒤 (`uv sync && uv run uvicorn app.main:app --reload --port 8000`) — 이 값들은 이 저장소에 커밋된 적 없는 팀 내부 공유 값이니 팀에 문의.
- **주의**: 지금 프론트는 개발 모드에서 항상 MSW mock을 쓰도록 되어 있어서(`src/main.tsx`), 백엔드를 로컬에 띄워도 프론트가 자동으로 그쪽을 호출하진 않습니다. 실제 연동은 아직 안 된 상태 — Phase 진행 상황 참고.

## 폴더 구조

```
src/
├── api/          공용 fetch 클라이언트 (baseURL, 에러 처리)
├── auth/         로그인 상태 Context, 로그인 유도 모달, useRequireAuth
├── components/   화면 간 공유 컴포넌트 (layout, auth, common, performances, reservations)
├── mocks/        MSW 핸들러(handlers/) + mock 데이터(data/) — 화면(도메인)별로 파일 분리
├── pages/        라우트에 매핑되는 실제 화면 (auth/, performances/, queue/, reservations/, system/)
├── routes/       라우트 표 (AppRoutes.tsx)
└── theme/        디자인 토큰(tokens.ts) + MUI 테마(theme.ts)
```

## Mock API 동작 원리

백엔드 API가 아직 완전히 붙지 않은 상태라, 모든 데이터는 **MSW(Mock Service Worker)**가 브라우저에서 실제 `fetch`를 가로채서 응답합니다. 새로고침하면 초기화되는 인메모리 mock입니다.

- `src/mocks/handlers/`에 화면(도메인)별로 핸들러 파일을 나눠 관리합니다. 실제 API 스펙(구글시트 `api 설계서` 탭)의 endpoint·요청/응답 형식을 그대로 따르는 게 원칙입니다.
- 개발 모드(`npm run dev`)에서만 자동으로 켜집니다(`src/main.tsx`의 `enableMocking()`). 프로덕션 빌드엔 포함되지 않습니다.
- 콘솔에 `[MSW] Mocking enabled`가 뜨고, 이후 API 요청마다 `[MSW] ... (200 OK)` 로그 그룹이 남습니다 — 요청/응답 확인은 브라우저 개발자도구 콘솔이 가장 빠릅니다.
- 이메일 인증코드, 비밀번호 재설정 인증코드처럼 "실제로는 이메일로 오는" 값은 전부 **브라우저 콘솔에 `[mock] ... 인증코드: 123456` 형태로 출력**됩니다.
- 공연 목록의 카테고리 필터는 API 파라미터가 아니라 **프론트에서 클라이언트 사이드로 필터링**합니다 (스펙에 해당 쿼리 파라미터가 없어서). mock 공연 데이터는 `src/mocks/data/performances.ts`.

## 테스트 계정

목업 DB(`src/mocks/db.ts`)에 미리 심어둔 계정입니다. **브라우저 탭을 새로고침(F5)하면 그 사이 회원가입한 계정은 사라지고 이 계정만 남습니다.**

| 이메일 | 비밀번호 |
|---|---|
| `test@example.com` | `passwd123` |

## Phase 진행 상황

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 공통 레이아웃, 라우팅 골격, 인증 상태 관리(Context), 로그인 유도 모달 | ✅ |
| 1 | 로그인 / 회원가입(이메일 인증) / 비밀번호 재설정 | ✅ |
| 2 | 공연 목록·검색·카테고리 필터, 공연 상세(공유·관심공연), 회차 선택 | ✅ |
| 3 | 대기열, 좌석 선택+Hold+타이머, 무통장입금 예매 생성/확인 | ✅ |
| 4 | 마이페이지(내정보 조회/수정, 예매목록, 관심공연) | ⬜ 다음 작업 |
| 5 | 관리자 로그인, 고객센터(플레이스홀더) | ⬜ |

## 화면별 테스트 시나리오

### 로그인 (`/login`)
1. `test@example.com` / `passwd123` 입력 후 로그인
2. 헤더 우측이 로그인/회원가입 버튼 → 아바타 메뉴로 바뀌는지 확인
3. 잘못된 비밀번호 입력 시 "이메일 또는 비밀번호가 올바르지 않습니다" 에러가 뜨는지 확인

### 회원가입 (`/signup`)
1. 새 이메일 입력 → "인증번호 발송" 클릭
2. 브라우저 콘솔에서 `[mock] {이메일} 인증코드: 123456` 확인 후 그 값을 인증번호 칸에 입력
3. 닉네임(2~20자) / 비밀번호(8자 이상, 영문+숫자 포함) / 비밀번호 확인 입력 후 제출
4. `/login`으로 이동하는지, 방금 만든 계정으로 로그인이 되는지 확인 (탭을 새로고침하지 않은 상태에서)

### 비밀번호 재설정 (`/password/reset`)
1. `test@example.com` 입력 → "인증번호 발송"
2. 콘솔에서 재설정 인증코드 확인 후 입력
3. 새 비밀번호 입력 후 제출 → `/login`으로 이동
4. 바뀐 비밀번호로 로그인되는지 확인 (되돌리려면 새로고침으로 mock DB 초기화)

### 공연 목록 (`/`)
1. 카드가 6개 보이는지 (mock 데이터, `src/mocks/data/performances.ts`)
2. 카테고리 칩(콘서트/뮤지컬/연극/전시) 클릭 시 클라이언트에서 필터링되는지
3. 헤더 검색창에 "재즈" 입력 후 Enter → 검색 결과만 보이는지, URL에 `?keyword=` 붙는지

### 공연 상세 (`/performances/:id`)
1. 공유하기 클릭 → 다이얼로그에 링크 표시 + 클립보드 복사
2. 비로그인 상태에서 하트(관심 공연) 클릭 → 로그인 유도 모달 → "로그인하러 가기" → 로그인 후 **원래 보던 상세 페이지로 자동 복귀**하는지
3. 로그인 상태에서 하트 클릭 → 채워진 하트로 바뀌는지 (다시 누르면 해제)
4. "예매하기" 클릭 → 로그인 상태면 바로 회차 선택으로, 비로그인이면 로그인 모달

### 회차 선택 (`/performances/:id/schedules`)
1. 날짜별로 그룹핑되어 보이는지, 요일이 한국어(토/일)로 표시되는지
2. 잔여 좌석 0인 등급만 있는 회차는 "매진"으로 비활성화되는지
3. "선택" 클릭 시 `/schedules/:scheduleId/seats`로 이동하는지

### 대기열 → 좌석 선택 → Hold → 무통장입금 예매
1. 로그인 상태에서 공연 상세 → "예매하기" → 회차 "선택" 클릭
2. 대기열 화면이 뜨고 약 7초 후 자동으로 좌석 선택 화면으로 넘어가는지 (데모용 고정 대기시간 — 아래 설계 결정 참고)
3. 좌석 배치도 범례 4가지(예매가능/선택중/선점중/판매완료) 색이 다르게 보이는지
4. 좌석 2~3개 선택 → 하단 바에 칩과 합계금액 → 5석째 선택 시도하면 "최대 4석" 스낵바
5. "선점하기" → 하단 바가 "선점 완료 · 남은시간 mm:ss" + "선택 취소"/"예매하기" 버튼으로 전환
6. "선택 취소" → 좌석 선택 모드로 복귀, 방금 선점했던 좌석이 다시 "예매 가능"으로 보이는지
7. 다시 선점 → "예매하기" → 무통장입금 폼(카운트다운 이어짐) → 입금자명 입력 후 제출
8. 예매 확인 페이지에서 예매번호/좌석/입금 은행·계좌·예금주·입금기한 확인
9. (선택) Hold 만료 재현: `src/mocks/data/store.ts`의 `HOLD_TTL_MS`를 잠깐 짧게 바꿔서 확인 후 원복

## 설계 결정 (스펙에 없어서 프론트에서 임의로 정한 것들)

| 항목 | 결정 | 이유 |
|---|---|---|
| 대기열 대기시간 | 진입 시 항상 약 7초(`QUEUE_WAIT_MS`) 대기 후 READY | 매번 대기열 화면을 보여주면서도 오래 안 기다리게 고정값으로 시뮬레이션 |
| entryTicket 캐시 | 스케줄별 세션스토리지 9분 캐시 | 같은 세션 재방문 시 대기열 재진입 방지 |
| 좌석 최대 선택 수 | 4석 | 스펙에 명시 없음 — 일반적인 티켓팅 관례로 추가 |
| 좌석 상태 시드 | seatId 7의 배수=SOLD, 11의 배수=HELD, 나머지=AVAILABLE | 데모에서 3가지 상태를 항상 골고루 보여주려고 |
| Hold TTL | 5분 | 스펙 "5~10분" 중 짧은 쪽, 실제 서버 `HOLD_TTL_SEC=300`과도 일치 확인됨 |
| 회차 → 공연/공연장 역참조 | API 스펙에 없음 — 좌석 선택 화면이 회차 선택 화면에서 넘겨준 state에 의존, 없으면 "다시 선택해주세요" 안내 | 백엔드에 조회 API 추가 요청 중 (`backend-decisions-needed.md` 1번) |

### figma 와이어프레임과 다르게 만든 부분 (의도적 변경)

| 화면 | 변경 내용 | 이유 |
|---|---|---|
| 로그인 | 구글/카카오 소셜 로그인 버튼 제외 | 소셜 로그인은 3차 범위 — 백엔드 미지원 |
| 로그인 | "Remember me" 체크박스 제외 | API 스펙에 대응 파라미터 없음 |
| 회원가입 | "성/이름" 2개 필드 → "닉네임" 1개 필드 | `member` 테이블에 실명 필드 없음, `nickname`만 존재 |
| 비밀번호 재설정 | 새 비밀번호/확인 필드 추가, 요청+재설정 화면 통합 | figma 와이어프레임에 새 비밀번호 입력란이 없었음(초안 누락으로 판단) |

## 트러블슈팅

**"요청에 실패했습니다" 같은 뭉뚱그려진 에러가 뜬다면:**
1. **새 Phase를 pull 받은 직후라면 `npm install`부터 다시 하고, `npm run dev`를 껐다가 다시 켜세요.** 새 npm 패키지가 추가된 상태에서 기존 dev 서버를 그대로 쓰면 Vite 의존성 사전 번들링이 꼬여서 API 요청이 실패하는 경우가 있습니다.
2. 브라우저 개발자도구 콘솔에서 `[MSW] Mocking enabled`가 찍혀 있는지 확인. 안 보이면 강력 새로고침(Ctrl+Shift+R) 후 재시도.
3. 그래도 안 되면 Network 탭에서 실패한 `/api/v1/...` 요청 응답이 JSON인지 HTML(404 페이지)인지 확인 — HTML이면 MSW가 못 가로챈 것, 1번으로 해결.

**콘솔의 인증코드를 못 찾겠다면:** 콘솔 필터에 `[mock]`으로 검색.
