# 새싹티켓 프론트엔드 (`web/frontend`)

티켓 예매 서비스 새싹티켓의 프론트엔드입니다. `feature/ui` 브랜치. **2026-08-20부로 MSW mock을 완전히 제거하고 실 백엔드(`feature/integration2`)에 직접 연동된 상태**입니다 — 개발 서버가 항상 실제 API를 호출합니다.

> 색상·타이포 등 디자인 규칙은 [`docs/design-system.md`](./docs/design-system.md).
> 백엔드 팀과 같이 결정했던 것들의 기록은 [`../../docs/backend-decisions-needed.md`](../../docs/backend-decisions-needed.md) 등(전부 답변 완료).
> 세션별 작업 이력(로그)은 [`../../docs/frontend-worklog.md`](../../docs/frontend-worklog.md).
> 새 대화를 시작할 때는 [`../../docs/frontend-handoff.md`](../../docs/frontend-handoff.md)부터 읽을 것.

## 기술 스택 · 버전

| 분류 | 선택 | 버전 |
|---|---|---|
| 런타임 | Node.js | 20.19+ 또는 22+ 권장 (Vite 8 요구사항) |
| 패키지 매니저 | npm | 이 프로젝트 개발 환경 기준 11.x |
| 빌드 도구 | Vite | ^8.2.0 — `vite.config.ts`의 `server.proxy`가 `/api/v1`을 실 백엔드로 전달 |
| 언어 | TypeScript | ~6.0.2 |
| UI 프레임워크 | React | ^19.2.8 |
| 컴포넌트 라이브러리 | MUI | ^9.3.1 (`@mui/material`, `@mui/icons-material`) — `src/theme/theme.ts`에 커스텀 테마 |
| 스타일 엔진 | Emotion | ^11.14.x (MUI 내부 의존성) |
| 라우팅 | react-router-dom | ^7.18.2 — `src/routes/AppRoutes.tsx` |
| 서버 상태 관리 | @tanstack/react-query | ^5.101.4 — 캐싱, 폴링(대기열/Hold 타이머) |
| 폼 | react-hook-form + zod + @hookform/resolvers | ^7.85.0 / ^4.4.3 / ^5.9.1 |
| 날짜/시간 | dayjs | ^1.11.23 (로케일 `ko` 적용, `src/main.tsx`) |
| 폰트 | Pretendard (CDN) | `index.html`의 `<link>` 참고, 별도 패키지 없음 |
| 린트 | oxlint | ^1.75.0 (`npm run lint`) |

정확한 버전은 항상 [`package.json`](./package.json)이 기준입니다 — 위 표는 참고용. (`msw`는 실 API 연동 후 제거됨.)

## 실행 방법 — 백엔드가 먼저 떠 있어야 함

이 프론트는 더 이상 mock으로 동작하지 않습니다. **`http://127.0.0.1:8000`에 실 백엔드가 떠 있어야 화면이 정상 동작**합니다.

```bash
# 1) 백엔드 (별도 터미널, 아래 "백엔드 로컬 실행" 참고)
cd ../../api/api
uv run uvicorn app.main:app --port 8000
# + 워커 3개(대기열 dispatcher, hold/reservation sweeper)도 각각 별도 터미널에서:
uv run python -m app.workers.queue_dispatcher
uv run python -m app.workers.hold_sweeper
uv run python -m app.workers.reservation_sweeper

# 2) 프론트
cd web/frontend
npm install
npm run dev       # http://localhost:5173, /api/v1/* 는 vite proxy로 :8000에 전달됨
```

```bash
npm run build     # tsc -b && vite build — 타입체크 + 프로덕션 빌드
npm run lint      # oxlint
npm run preview   # 빌드 결과물 미리보기 (주의: preview는 vite dev proxy가 없음 — 실 배포에선 nginx가 이 역할)
```

## 백엔드 로컬 실행 (Docker + uv)

배포된 공유 서버가 꺼져있을 때를 대비한 완전한 로컬 셋업. 자세한 트러블슈팅은 [`frontend-handoff.md`](../../docs/frontend-handoff.md) 참고.

```bash
# MySQL + Valkey 컨테이너 (최초 1회, 이후엔 docker start만 하면 됨)
docker run -d --name sesac-mysql -e MYSQL_ROOT_PASSWORD=sesacroot -e MYSQL_DATABASE=sesac_ticket -p 3306:3306 mysql:8.0
docker run -d --name sesac-valkey -p 6379:6379 valkey/valkey:7

# 스키마 적용 (최초 1회)
cd ../../api/api
cat scripts/sql/sesac_ticket_init.sql | docker exec -i sesac-mysql mysql -uroot -psesacroot sesac_ticket

# .env 생성 (레포에 커밋 안 됨 — .env.example 기준, 아래는 로컬 전용 값)
#   DB_WRITER_URL/DB_READER_URL=mysql+pymysql://root:sesacroot@127.0.0.1:3306/sesac_ticket
#   VALKEY_MASTER_HOST/VALKEY_REPLICA_HOST=127.0.0.1, COOKIE_SECURE=false, JWT_SECRET=아무 랜덤 문자열
#   나머지는 .env.example 기본값 그대로

uv sync
uv run python -m scripts.admin_seed   # adminId=admin01, password=test1234!
uv run python -m scripts.perf_seed    # venue 1, 좌석 450석, 공연 5개, 회차 15개
```

**⚠️ 알려진 환경 이슈**: `redis-py==8.1.0`(백엔드 `uv.lock`에 고정된 버전) + `protocol=2` 조합에서 `ZPOPMIN` 명령이 Valkey 7.2 서버로부터 `unknown command`를 응답받는 버그를 로컬에서 확인함(2026-08-20). 이 명령은 **대기열 dispatcher**(`workers/queue_dispatcher.py`)가 대기 인원을 방출할 때 사용 — 이 버그가 있으면 대기열이 영원히 `WAITING`에 머물러 좌석 선택까지 못 감. `ZADD`/`ZRANGE` 등 다른 zset 명령은 정상 동작해서 `ZPOPMIN`에 국한된 문제로 보임. **백엔드 팀에 확인 필요** — 배포 서버(다른 Valkey 버전/redis-py 버전 조합일 수 있음)에선 재현 안 될 수도 있음.

## 실 API 연동 방식

- `vite.config.ts`의 `server.proxy`가 `/api/v1` 요청을 `http://127.0.0.1:8000`으로 전달합니다. 브라우저 입장에선 프론트/백엔드가 같은 오리진이라 refreshToken(HttpOnly 쿠키) 왕복에 CORS 설정이 필요 없습니다. 운영에서도 nginx가 같은 방식(reverse proxy)으로 묶을 예정이라 로컬 개발 환경과 구조가 동일합니다.
- `src/api/client.ts`(회원용)와 `src/api/adminClient.ts`(관리자용)는 완전히 분리된 클라이언트입니다 — accessToken을 각자 모듈 변수로 관리하고, 401을 받으면 각자의 refresh 엔드포인트(`/auth/refresh` vs `/admin/auth/refresh`)로 한 번 재시도합니다.
- 앱 시작 시(`AuthContext`/`AdminAuthContext`) refreshToken 쿠키로 로그인 상태 복원을 시도합니다 — **새로고침해도 로그인 상태가 유지됩니다** (예전 mock 단계의 "새로고침하면 로그아웃" 제약이 실 연동으로 해소됨). 관리자는 실 백엔드에 "whoami" API가 없어서 복원 시 관리자 ID 표시는 안 되지만(그냥 "관리자님"으로 표시) 인증 상태 자체는 정상 복원됩니다.

## 테스트 계정

| 이메일 | 비밀번호 | 비고 |
|---|---|---|
| (직접 회원가입) | - | 회원가입에 이메일 인증이 필요 없음 — 아래 "가입 흐름" 참고 |

관리자 계정(`scripts/admin_seed.py`로 시드):

| 관리자 ID | 비밀번호 |
|---|---|
| `admin01` | `test1234!` |

### 가입 흐름 — mock 단계와 달라진 부분

실 백엔드의 `POST /auth/email/verify-request`는 **이미 가입된 회원에게만** 인증 코드를 발급합니다(가입 안 한 이메일로 요청하면 조용히 무시하고 `{sent:true}`만 반환 — 사용자 열거 공격 방지 목적). 즉 **가입 전에는 이메일 인증 코드를 받을 방법이 아예 없습니다.** 그래서 회원가입 화면은 이메일 인증 없이 바로 `POST /auth/signup`을 호출하도록 수정했습니다(mock 단계엔 가입 전 인증을 요구했었는데, 실제 계약을 확인하고 제거함). 로그인도 `email_verified` 여부를 확인하지 않습니다. 이메일 인증 코드 발급/확인 API 자체는 "마이페이지 > 정보 수정"에서 본인 확인 용도로 정상적으로 씁니다(이 시점엔 이미 회원이므로 정상 발급됨).

이메일로 오는 값(인증 코드, 비밀번호 재설정 토큰)은 `SMTP_HOST`가 비어있으면 실제 발송 없이 서버 로그에 남기도록 설계돼 있는데(`app/core/mailer.py`), **로컬에서 uvicorn 기본 로깅 설정이 이 로그를 가로채서 콘솔/로그파일 어디에도 안 남는 문제를 확인함.** 로컬 테스트 시엔 Valkey에서 직접 조회하는 게 확실합니다:
```bash
docker exec sesac-valkey valkey-cli GET "auth:email-verify:{이메일}"        # 인증 코드
docker exec sesac-valkey valkey-cli KEYS "auth:password-reset:*"           # 재설정 토큰 (토큰이 키 이름에 포함)
```

## 폴더 구조

```
src/
├── api/          회원용 fetch 클라이언트(client.ts) + 관리자용(adminClient.ts) — 완전히 분리, 각자 401 재발급 인터셉터 보유
├── auth/         로그인 상태 Context(새로고침 시 refreshToken으로 복원), 로그인 유도 모달, useRequireAuth
├── admin/        관리자 전용 인증 Context(AdminAuthContext) — 일반 회원 auth/와 완전히 분리
├── components/   화면 간 공유 컴포넌트 (layout, auth, common, performances, reservations)
├── pages/        라우트에 매핑되는 실제 화면 (auth/, performances/, queue/, reservations/, mypage/, support/, admin/, system/)
├── routes/       라우트 표 (AppRoutes.tsx)
└── theme/        디자인 토큰(tokens.ts) + MUI 테마(theme.ts)
```

## Phase 진행 상황

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 공통 레이아웃, 라우팅 골격, 인증 상태 관리(Context), 로그인 유도 모달 | ✅ |
| 1 | 로그인 / 회원가입 / 비밀번호 재설정 | ✅ |
| 2 | 공연 목록·검색·카테고리 필터, 공연 상세(공유·관심공연), 회차 선택 | ✅ |
| 3 | 대기열, 좌석 선택+Hold+타이머, 무통장입금 예매 생성/확인 | ✅ |
| 4 | 마이페이지(내정보 조회/수정, 예매목록, 관심공연) | ✅ |
| 5 | 관리자 로그인, 고객센터(목록·상세) | ✅ |
| 6 | **실 API 연동** (mock 제거, refresh token, 실 계약 정합화) | ✅ 대부분 완료 — 대기열 구간은 위 환경 이슈로 로컬 완전 검증은 보류 |

## 화면별 테스트 시나리오

### 로그인 (`/login`)
1. 회원가입한 계정으로 로그인
2. 헤더 우측이 로그인/회원가입 버튼 → 아바타 메뉴로 바뀌는지 확인
3. 잘못된 비밀번호 입력 시 에러가 뜨는지 확인
4. **새로고침(F5) 해도 로그인 상태가 유지되는지** (refreshToken 쿠키 복원 — 실 연동으로 새로 생긴 동작)

### 회원가입 (`/signup`)
1. 이메일 / 닉네임(2~20자) / 비밀번호(8자 이상, 영문+숫자 포함) / 비밀번호 확인 입력 후 제출 — **이메일 인증 단계 없음**
2. `/login`으로 이동하는지, 방금 만든 계정으로 로그인이 되는지 확인
3. 이미 가입된 이메일로 재시도 시 에러가 뜨는지

### 비밀번호 재설정 (`/password/reset`)
1. 가입된 이메일 입력 → "인증번호 발송"
2. Valkey에서 재설정 토�큰 확인(`docker exec sesac-valkey valkey-cli KEYS "auth:password-reset:*"`) 후 "재설정 토큰" 칸에 붙여넣기 — 6자리 코드가 아니라 긴 랜덤 문자열임
3. 새 비밀번호 입력 후 제출 → `/login`으로 이동, 바뀐 비밀번호로 로그인되는지 확인

### 공연 목록 (`/`)
1. 카테고리 칩이 **실제 데이터에 있는 카테고리만** 동적으로 보이는지(현재 시드 기준 콘서트/뮤지컬 2개 — mock 때의 "연극/전시" 같은 가상 카테고리는 더 이상 안 보임)
2. 헤더 검색창에 키워드 입력 후 Enter → 검색 결과만 보이는지, URL에 `?keyword=` 붙는지

### 공연 상세 (`/performances/:id`)
1. 공유하기 클릭 → 다이얼로그에 현재 페이지 URL 표시 + 클립보드 복사 (실 백엔드에 공유 링크 발급 API가 없어서 클라이언트에서 현재 URL을 그대로 씀)
2. 비로그인 상태에서 하트(관심 공연) 클릭 → 로그인 유도 모달 → 로그인 후 원래 보던 상세 페이지로 복귀하는지
3. 로그인 상태에서 하트 클릭 → 채워진 하트로 바뀌는지 (다시 누르면 해제)

### 회차 선택 (`/performances/:id/schedules`)
1. 공연 상세 응답에 이미 포함된 회차/등급/가격 정보로 렌더링되는지(별도 회차 목록 API는 더 안 씀)
2. 날짜별로 그룹핑되어 보이는지, 잔여 좌석 0인 등급만 있는 회차는 "매진"으로 비활성화되는지

### 대기열 → 좌석 선택 → Hold → 무통장입금 예매
> **로컬에서 위 ZPOPMIN 환경 이슈로 대기열 자동 방출 구간은 실제 확인이 안 된 상태입니다.** 배포 서버가 살아있을 때, 또는 이 이슈가 해결된 뒤 재검증 필요.
1. 로그인 상태에서 공연 상세 → "예매하기" → 회차 "선택" 클릭 → 대기열 화면
2. (대기열 이슈 해결 후) READY 전환 → 좌석 선택 화면, 새로고침해도 회차→공연 역참조 API(`GET /schedules/{scheduleId}`)로 복구되는지
3. **좌석 최대 2석**(`MAX_SEATS_PER_HOLD=2`) 제한 확인 — 3번째 선택 시 스낵바
4. "선점하기" → "예매하기" → 무통장입금 폼 → 입금자명 입력 후 제출
5. 예매 확인 페이지에서 예매번호/좌석(구역·열·번·등급·가격)/입금 은행·계좌·입금기한 확인 — **입금자명은 응답에 없어서 화면에 안 보임**(실 계약 확인 후 제거)

### 마이페이지 (`/mypage`, `/mypage/edit`, `/mypage/reservations`, `/mypage/favorites`)
1. 비로그인 상태에서 `/mypage` 직접 접속 → "로그인이 필요해요" 안내 화면이 뜨는지
2. 로그인 후 내 정보(이메일/닉네임/성별/나이대) 조회되는지
3. "정보 수정" → 닉네임 변경 → "인증번호 발송" → Valkey에서 코드 확인 후 입력 → 저장 → 바뀐 닉네임이 보이는지
4. "내 예매 목록" → 예매 내역 클릭 시 예매 확인 페이지로 이동하는지
5. "관심 공연" → 카드에 제목/썸네일만 보이는지(실 API가 이 두 필드만 줌 — 공연 상세 정보는 카드 클릭해서 확인)

### 고객센터 (`/support`, `/support/:postId`)
1. 카테고리 칩 클릭 시 목록이 필터링되는지
2. 게시글 클릭 → 상세 페이지, "목록으로" 클릭 시 되돌아가는지
3. 로그인 여부와 무관하게 목록·상세 둘 다 조회되는지
4. (참고) seed 스크립트가 성능/관리자 데이터만 채워서 기본적으로 게시글이 없음 — 빈 상태 문구가 정상 표시되는지만 확인하거나, DB에 직접 INSERT해서 확인

### 관리자 로그인 (`/admin/login`, `/admin`)
1. `admin01` / `test1234!`로 로그인 → `/admin`으로 이동, 환영 문구 확인
2. 잘못된 계정으로 로그인 시도 → 에러
3. **새로고침(F5) 해도 로그인 상태가 유지되는지**(관리자 ID 표시는 "관리자님"으로 일반화됨 — whoami API가 없어서)
4. "로그아웃" 클릭 → `/admin/login`으로 이동

## 설계 결정 / 실 계약과 다르게 확인된 것들

| 항목 | 결정 | 이유 |
|---|---|---|
| 대기열 대기시간 | 실제 대기 인원과 dispatcher 방출 속도에 따라 가변 | mock 때는 데모용 고정 7초였으나 실 연동으로 제거 |
| entryTicket 캐시 | 스케줄별 세션스토리지 4분 캐시 | 실제 TTL 5분(`_ENTRY_TICKET_TTL_SEC=300`)보다 짧게 잡아 만료 직전 재사용 방지 |
| 좌석 최대 선택 수 | **2석** | 실 서버 `.env.example`의 `MAX_SEATS_PER_HOLD=2` — mock 때 4석은 임의값이었음, 실 연동 시 2로 수정 완료 |
| 좌석 상태 | `AVAILABLE`/`HELD`/`RESERVED` | 실제로 `SOLD`라는 상태는 없음(mock에 있던 걸 정정) |
| Hold TTL | 5분 | 실제 서버 `HOLD_TTL_SEC=300`과 일치 |
| 회차 → 공연/공연장 역참조 | `GET /schedules/{scheduleId}` 사용 | 새로고침 시 컨텍스트 복구용으로 실제 존재하는 API를 씀 |
| 공유 링크 | 클라이언트에서 `window.location.href` 그대로 사용 | 실 백엔드에 공유 링크 발급 API 자체가 없음(mock에만 있던 가상 엔드포인트였음) |
| 회원가입 이메일 인증 | 제거함(가입 전엔 인증 코드 발급이 원천적으로 불가능한 구조) | 위 "가입 흐름" 참고 |
| 관심 공연 카드 정보 | 제목/썸네일만 표시 | 실 `GET /users/me/favorites`가 `{performanceId, title, thumbnailUrl}`만 반환 — mock처럼 카테고리/venue/날짜까지는 안 줌 |
| 예매 확인 페이지 | 입금자명(depositorName) 표시 제거, 좌석별 가격 추가 | 실 `ReservationDetailResponse`엔 입금자명 필드가 없고, 좌석 항목엔 `price`가 있음(seatId는 없음 — index를 key로 씀) |
| 마이페이지 나이대 선택지 | "10대/20대/30대/40대/50대 이상" 5개 고정 | 스펙엔 `ageRange`가 문자열 optional일 뿐 값 목록이 없음 |
| 고객센터 카테고리 목록 | "공지/이용안내/자주묻는질문" 3개 고정(로컬 상수) | 카테고리 목록 조회 API 자체가 없음 — 운영 데이터의 실제 카테고리로 교체 필요 |
| 고객센터 페이지 크기 | 6개(백엔드 기본값은 20) | 페이지네이션 동작 확인용 |
| 관리자 홈(`/admin`) | 로그인 성공 후 환영 문구 + 로그아웃 버튼만 있는 placeholder | 백엔드 admin 도메인엔 로그인/재발급 API만 있고 관리 기능 API가 아직 없음 |

### figma 와이어프레임과 다르게 만든 부분 (의도적 변경)

| 화면 | 변경 내용 | 이유 |
|---|---|---|
| 로그인 | 구글/카카오 소셜 로그인 버튼 제외 | 소셜 로그인은 3차 범위 — 백엔드 미지원 |
| 로그인 | "Remember me" 체크박스 제외 | API 스펙에 대응 파라미터 없음 |
| 회원가입 | "성/이름" 2개 필드 → "닉네임" 1개 필드, 이메일 인증 단계 제거 | `member` 테이블에 실명 필드 없음. 이메일 인증은 가입 전엔 API 계약상 불가능 |
| 비밀번호 재설정 | 새 비밀번호/확인 필드 추가, 요청+재설정 화면 통합 | figma 와이어프레임에 새 비밀번호 입력란이 없었음(초안 누락으로 판단) |

## 트러블슈팅

**"요청에 실패했습니다" 같은 뭉뚱그려진 에러가 뜬다면:**
1. 백엔드가 `:8000`에 떠 있는지 확인 (`curl http://127.0.0.1:8000/api/v1/version`)
2. `vite.config.ts`의 proxy 설정이 살아있는지, dev 서버를 백엔드보다 먼저 켠 게 아닌지 확인(순서 상관은 없지만 dev 서버 재시작하면 확실함)
3. Network 탭에서 실패한 `/api/v1/...` 요청의 실제 응답(상태 코드, body)을 확인

**로그인은 되는데 새로고침하면 다시 로그아웃된다면:** refreshToken 쿠키가 안 내려온 것 — 백엔드 `COOKIE_SECURE` 설정이 `true`인 상태로 로컬 http에서 쓰고 있진 않은지 확인(로컬은 `false`여야 함).

**"인증코드가 일치하지 않습니다"만 계속 뜬다면:** Valkey에 저장된 코드를 직접 조회해서 실제 값과 비교 (`docker exec sesac-valkey valkey-cli GET "auth:email-verify:{이메일}"`) — 위 mailer 로그 미출력 이슈 때문에 화면의 "발송 완료" 문구만으로는 코드를 알 수 없음.
