# 프론트 작업 핸드오프 (2026-08-21 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. **오늘부로 `feature/ui`가 아니라 `feature/integration3` 브랜치를 씀** — 백엔드팀이 프론트(`feature/ui`)+백엔드(`feature/integration2`)를 통합해서 새로 만든 브랜치. 화면 Phase 0~5 + 실 API 연동 + 디자인 개선(1~5차)까지는 이 브랜치에 전부 이미 들어가 있는 상태로 시작함.

## 0. 가장 먼저 할 것

**커밋 안 된 변경사항**:
- `web/frontend/src/pages/performances/PerformanceListPage.tsx` — **진짜 버그 수정, 커밋해야 함.** 메인 화면 히어로 배너(`HeroBanner`)가 실제 포스터 이미지 대신 계속 그러데이션만 보이던 버그. 원인: 팀원이 `PlaceholderImage`에 실제 이미지(`src`) 연동을 추가하면서 `PerformanceCard`/`PerformanceDetailPage`엔 `src`를 넘기도록 고쳤는데 `HeroBanner`만 빠뜨림. `src={performance.thumbnailUrl}` 추가로 수정.
- `api/app/domains/reservation/service.py`, `api/app/workers/queue_dispatcher.py` — **로컬 전용 임시 우회 패치, 절대 커밋하지 말 것.** 아래 3번 섹션 참고.

```bash
git add web/frontend/src/pages/performances/PerformanceListPage.tsx
git commit -m "fix: wire real thumbnail image into home hero banner"
git push origin feature/integration3
```

**⚠️ git 조작은 항상 사용자가 직접 실행할 것.** 위 명령어도 절대 대신 실행하지 말고 그대로 전달만 할 것 (과거 세션에 이 규칙을 어겨서 강하게 항의받은 적 있음).

**⚠️ `api/app/...` 두 파일은 절대 `git add`하지 말 것.** 로컬 redis-py 환경 버그를 피하기 위한 개인 워크어라운드일 뿐, 실제 수정이 아님(3번 섹션). `git add web/frontend`처럼 경로를 좁혀서 add하는 지금 방식이면 자동으로 안전함.

## 1. 로컬 폴더 구조 (오늘 변경됨 — 별도 clone 폐지)

```
sesac-ticket/          ← 이 저장소 하나. feature/integration3. git add/commit/push 전부 여기서
├── web/frontend/      ← 프론트
├── api/               ← 백엔드 (이제 같은 저장소 안에 있음, 별도 clone 아님!)
└── docs/              ← 공용 문서
```

**오늘 있었던 일**: 원래 `api/`는 완전히 별도의 clone(자체 `.git`, `feature/integration2` 체크아웃)이었음 — `feature/ui`가 `api/`를 전혀 추적하지 않던 시절엔 문제 없었지만, `feature/integration3`가 프론트 저장소 쪽에도 `api/`를 새로 추적하기 시작하면서 **그 별도 clone이 있던 바로 그 자리에 메인 저장소가 자기 파일을 체크아웃하려다 충돌**이 남(`git status`에 `api/api/`, `api/docs/`, `api/web/` 같은 이상한 중첩 폴더가 untracked로 나타남). 원인 파악 후 별도 clone은 완전히 폐지하고(더 이상 필요 없음 — 이제 프론트/백엔드가 한 브랜치, 한 저장소에 있으므로) `sesac-ticket/api/`를 메인 저장소가 체크아웃한 것 하나로 정리함. **혹시 다음 세션에서 `sesac-ticket/api/` 안에 `.git`이 또 있거나 이상한 중첩이 보이면 같은 문제이니, 메인 저장소 checkout만 남기고 별도 clone 흔적은 지울 것.**

## 2. Phase 진행 상황

| Phase | 내용 | 상태 |
|---|---|---|
| 0~5 | 전체 화면(로그인~관리자/고객센터) | ✅ |
| 6 | 실 API 연동 | ✅ |
| 7 | 디자인 개선(좌석 배치도 → 메인/상세 히어로 → 로그인/좌석선택/마이페이지 → 그림자·radius 폐지) | ✅ 5차까지 완료 |
| 8 | `feature/integration3` 통합(백엔드팀이 완료) | ✅ — 대기열/좌석 관련 버그가 로컬 환경(redis-py 버전 조합) 문제였을 뿐, 클라우드 배포 환경은 정상 동작한다고 확인됨 |

세부 내용은 [`web/frontend/README.md`](../web/frontend/README.md) 참고.

## 3. 다음 세션에서 바로 확인할 것 — 로컬 서버 상태

**이번 세션 종료 시점엔 로컬 백엔드가 꺼져 있습니다** (Docker 컨테이너, uvicorn, 워커 전부 미실행 상태로 끝남 — 위 1번 섹션의 clone 정리 작업 때문에 재기동을 다음 세션으로 미룸). 처음부터 새로 띄워야 함:

```bash
docker start sesac-mysql sesac-valkey   # 없으면 README의 "백엔드 로컬 실행" 참고해서 새로 생성
cd api
uv sync
uv run uvicorn app.main:app --port 8000            # 별도 터미널
uv run python -m app.workers.queue_dispatcher      # 별도 터미널
uv run python -m app.workers.hold_sweeper          # 별도 터미널
uv run python -m app.workers.reservation_sweeper   # 별도 터미널
```

**경로가 바뀌었음에 주의**: 예전엔 별도 clone이라 `cd api/api`였는데, 이제 `sesac-ticket/api/`가 바로 프로젝트 루트라서 `cd api` 한 번이면 됨.

**`.env` 위치도 바뀜**: `sesac-ticket/api/.env` (예전 `api/api/.env` 아님). 이번 세션엔 시간이 급해서 **팀 채팅에 공유된 실제 시크릿 값을 그대로 `.env`에 사용함**(사용자 본인 판단, "프로덕션에서는 바꿀 것"이라고 명시함) — 평소 원칙(JWT_SECRET 등은 매번 랜덤 생성)과 다른 예외적 처리이니, **다음 세션에서 로컬 개발에 지장 없으면 랜덤 값으로 되돌리는 걸 권장**. `.env`는 gitignore돼 있어 커밋될 일은 없음.

**✅ 로컬 임시 우회 재적용 완료(2026-08-21)**: `feature/integration3`로 넘어오면서 파일이 클린 상태로 새로 체크아웃됐길래, 아래 두 패치를 다시 적용해둠 — 다음 세션에서 로컬 백엔드를 다시 클론/리셋하면 또 사라지니 그때마다 재적용 필요.
1. `api/app/workers/queue_dispatcher.py`의 `dispatch_once()` — `client.zpopmin(key, n)`을 `client.zrange(key, 0, n-1, withscores=True)` + `client.zrem(key, *tokens)`로 교체.
2. `api/app/domains/reservation/service.py`의 `get_seat_status_list()` — `client.hset(key, mapping=mapping)`(다중 필드)을 `client.hmset(key, mapping)`(레거시)으로 교체.

두 군데 다 코드에 "원래 코드로 되돌릴 것" 주석과 정확한 원복 방법을 남겨뒀음. **오늘 사용자가 배포팀에 확인해본 결과, 이 두 버그는 클라우드 배포 환경에서는 재현되지 않는다고 확인됨** — 즉 로컬 Docker Valkey + redis-py 8.1.0 조합에서만 나는 환경 문제로 보임(원인 분석은 [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md) 참고). 배포에 영향 없는 로컬 전용 이슈이므로 백엔드팀 우선순위는 낮아도 됨 — 다만 로컬 개발을 계속하려면 이 두 패치는 계속 필요함.

**테스트 계정**: `test@example.com`/`passwd123` — DB를 새로 만들면 사라지니 그럴 땐 `/signup`에서 재가입하거나 curl로 재생성.

## 4. 이번 세션에서 새로 들어온 것 (백엔드팀이 `feature/integration3`에 병합, 프론트가 만든 게 아님)

- **실제 포스터 이미지 연동**: `PlaceholderImage`에 `src` prop 추가 — 있으면 실제 이미지, 없거나 로드 실패하면 기존 그러데이션 폴백. `PerformanceCard`(`thumbnailUrl`)·`PerformanceDetailPage`(`images[0].imageUrl`)에 연동됨. **`PerformanceListPage.tsx`의 `HeroBanner`엔 빠져있던 걸 이번 세션에 발견해서 수정함**(0번 섹션).
- **`PENDING_PAYMENT` 좌석 상태 신설**: 예매 생성 시 바로 `RESERVED`가 아니라 `HELD → PENDING_PAYMENT(입금대기중) → RESERVED(관리자 확정 후)` 3단계로 분리됨. `SeatStatus` 타입, `SeatGrid`/`SeatLegend`의 색상·라벨, `tokens.ts`의 `pendingPayment*` 토큰에 반영됨.
- **관리자 홈 — 무통장입금 확정 기능**: 예매번호 입력해서 확정하는 화면이 생김(`AdminHomePage.tsx`, `adminApi.confirmBankTransfer`). 회원 전용 예매 상세 조회 API를 관리자 토큰으론 못 쓰기 때문에 예매번호를 직접 입력받는 방식.
- **선점 실패 시 UX 수정**: 좌석 선점(`holdMutation`) 실패 시 선택 상태를 비우고 좌석 현황을 다시 받아오도록 수정(`SeatSelectPage.tsx`) — 이전엔 실패해도 화면에 stale `AVAILABLE` 표시가 남아서 다른 좌석 선택이 막혀 보이는 문제가 있었음.
- **푸터를 화면 하단 고정으로 변경**(`RootLayout.tsx`).
- **서버 식별 방식을 `.env` 라벨 대신 실측 IP 기반으로 전환** — `SystemInfoBadge.tsx`/`systemApi.ts` 관련.

## 5. 이전 세션들에서 발견한 핵심 실 계약 불일치 (전부 코드에 반영 완료)

- 회원가입 이메일 인증 흐름 — 가입 전 인증 불가능한 설계라 `SignupPage.tsx`에서 인증 단계 제거함.
- 관심 공연 목록 `{performanceId, title, thumbnailUrl}[]`, 예매 상세 좌석 항목에 `seatId` 없음, 공유 링크 API 없음, 좌석 등급 목록 API 대신 공연 상세의 `schedules` 사용, 좌석 `row`는 문자열, `MemberResponse`에 `preferredGenres` 없음(`status`로 대체).

상세 근거는 [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md)와 `web/frontend/README.md`의 설계 결정 표 참고.

## 6. 디자인 개선 이력 (1~5차 전부 완료, `feature/integration3`에 이미 포함됨)

세부 내용이 길어서 [`frontend-worklog.md`](./frontend-worklog.md)의 2026-08-20/2026-08-21 항목에 각 차수별로 상세히 남겨뒀음. 요약:
1. 좌석 배치도 등급색 + 무대 곡선 SVG
2. 메인/상세 히어로 배너 + 그러데이션 포스터 아트(`PlaceholderImage`)
3. 카테고리 원형 배지, 로그인/좌석선택/마이페이지 레이아웃 개편
4. 좌석 화면 무한 로딩 버그 수정(HSET) + `SeatGrid`의 x/y 좌표→그리드 인덱스 변환 버그 수정
5. **그림자·radius 전면 폐지** — 전부 각진 사각형, 그림자 없음(`theme/tokens.ts`의 `radius`가 전부 `0`)

**여전히 범위 밖인 것**: 헤더/네비게이션(RootLayout) 자체 디자인, "인기순/랭킹" 섹션(실제 인기 데이터 없어서 의도적으로 안 만듦).

## 7. 프로젝트 배경

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨.
- **팀 채팅에 실제 시크릿이 평문으로 공유되는 습관 있음** — 원칙적으로 파일/메모리에 옮기지 않음. (3번 섹션에 적었듯 이번 세션엔 사용자가 시간 압박으로 예외적으로 로컬 `.env`에 실제 값을 씀 — 프로덕션 전엔 교체 예정이라고 확인함.)
- 작업 방식: 커밋/푸시는 항상 사용자가 직접 실행, Playwright는 검증 후 항상 `npm uninstall`로 제거, 세션 끝날 때 worklog에 기록, 백엔드 확인 요청은 매번 새 문서로.
