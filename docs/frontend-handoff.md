# 프론트 작업 핸드오프 (2026-08-20 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. `feature/ui` 브랜치. **화면 Phase 0~5 전부 완료 + 실 API 연동(Phase 6)까지 대부분 완료.** MSW mock은 완전히 제거됨 — 이제 항상 실 백엔드가 필요하다.

## 0. 가장 먼저 할 것

**커밋 안 된 변경사항이 있습니다.** 좌석 배치도 등급색 개선(1차)과 메인/상세 히어로(2차)는 이미 커밋·푸시 완료됨. 이번엔 **세부 피드백 반영 + 범위 확장(로그인·좌석선택·마이페이지·고객센터)** 한 3차 디자인 패스가 아직 안 올라감(6번 섹션에 자세히):
- `PlaceholderImage.tsx` — 그러데이션 위 글자 오버레이 제거(어색하다는 피드백)
- `PerformanceListPage.tsx` — 히어로가 카테고리 필터와 무관하게 항상 보이도록 수정, 카테고리 버튼을 사각 타일 → 원형 아이콘 배지로 재설계(`ButtonBase` 기반, 접근성도 개선)
- `AuthCard.tsx` — 로그인/회원가입/비밀번호재설정 공통 레이아웃을 좌(브랜드 비주얼)/우(폼) 2단으로 전면 개편
- `SeatSelectPage.tsx` — 상단에 썸네일+제목+공연장 헤더 추가, 좌석 배치도를 카드로 감쌈
- `MyPageLayout.tsx` — 프로필 헤더(아바타+닉네임+이메일) + 밑줄 탭 네비 추가
- `SupportListPage.tsx`, `MyReservationsPage.tsx` — 카드 호버 그림자로 톤 통일
- `web/frontend/docs/design-system.md`, `docs/frontend-worklog.md` 갱신
- (4차, 추가) `SeatGrid.tsx` — x/y 절대좌표를 그리드 인덱스로 변환하는 버그 수정, 좌석 셀 크기 축소(가로 스크롤 제거)
- (5차, 추가) **그림자·radius 전면 폐지** — 호버 그림자/입체 효과, 좌석·범례의 inset 하이라이트를 전부 제거하고, `theme/tokens.ts`의 `radius` 스케일을 전부 `0`으로 바꿔 버튼/칩/카드/인풋/아바타/아이콘버튼까지 전부 각진 사각형으로 통일(6번 섹션 5차에 상세)

```bash
git add docs/frontend-worklog.md docs/frontend-handoff.md docs/backend-decisions-followup-2.md web/frontend
git commit -m "feat: refine home hero/category UX, extend design to auth/seat-select/mypage pages; fix seat grid layout bug; flatten shadows and radius to square corners"
git push origin feature/ui
```

**⚠️ git 조작은 항상 사용자가 직접 실행 — 이번 세션에 이 규칙을 어기고 커밋/리셋을 대신 실행해서 강하게 항의받은 적 있음.** 위 명령어도 절대 대신 실행하지 말고 그대로 전달만 할 것.

**참고**: 로컬 백엔드(Docker+uvicorn+워커 3개)는 이번 세션 마지막에도 **계속 띄워둔 상태로 끝남**. 다음 세션 시작할 때 `curl http://127.0.0.1:8000/api/v1/version`으로 살아있는지 먼저 확인하고, 죽어있으면 3번 섹션의 재기동 명령어 실행할 것.

**추가로 이번 세션에 발견/수정한 것 (4차 디자인 패스, 아직 커밋 안 됨)**:
- 대기열 통과 후 좌석 화면이 계속 로딩만 뜨던 버그 — `GET /schedules/{scheduleId}/seats`가 500을 내고 있었음. 원인은 ZPOPMIN과 동종의 redis-py/Valkey 환경 버그(다중 필드 `HSET` 실패) — 3번 섹션에 상세, 로컬 우회 적용해서 해결함.
- `SeatGrid.tsx`에 진짜 배치 버그가 있었던 것도 이번에 처음 발견함: 서버가 주는 좌석 `x`/`y`가 그리드 인덱스가 아니라 실제 배치 좌표(20px 단위)라서, 그대로 CSS grid-column/row에 쓰면 열 수백 개짜리 초대형 그리드가 만들어져 좌석이 듬성듬성 떨어져 보였음(좌석 상태 API가 계속 500이라 지금까지 실 데이터로 렌더링된 걸 본 적이 없어서 못 잡았던 버그). `SeatGrid.tsx`에서 실제 사용된 x/y 값들만 뽑아 순번을 매겨 촘촘한 인덱스로 바꾸는 방식으로 수정함.
- 좌석 셀 모양은 의자 아이콘(`EventSeatIcon`)으로 한 번 바꿔봤다가 사용자가 화면에서 직접 보고 "네모 모양으로 간단하게"로 되돌려달라고 해서 원래의 사각형 색상 셀로 복귀함(`SeatLegend.tsx`/`SeatGradeLegend.tsx`도 같이 되돌림). 등급별 색상 구분 자체는 유지.
- 이어서 "그림자/입체 효과 때문에 촌스럽다" + "좌석 배치도 가로 스크롤 생긴다, 셀 줄이자" 피드백 → `PerformanceCard`/`MyReservationsPage`/`SupportListPage`/`SeatGrid`/`SeatGradeLegend`/`SeatSelectPage`의 호버 그림자·inset 하이라이트를 전부 제거(호버는 `borderColor`/`outline` 변화만), `SeatGrid`의 셀 크기를 34px→18px로 줄이고 좌석선택 페이지 `Container`를 `md`→`lg`로 넓혀서 실제 45열 배치도가 가로 스크롤 없이 들어오게 함.
- 곧바로 "radius도 전부 삭제, 차라리 전부 사각형으로" 요청 → `theme/tokens.ts`의 `radius` 스케일을 전부 `0`으로 바꾸고, MUI 자체 기본이 원형인 `Avatar`/`IconButton`엔 `theme.ts`에 별도 오버라이드를 추가해서 강제로 각지게 만듦. 히어로 배너·정보카드·카테고리 배지·마이페이지 아바타 등 하드코딩돼 있던 `'20px'`/`'50%'`/`'999px'` 같은 문자열 radius도 전부 찾아서 제거.
- Playwright로 로그인 → 상세 → 회차선택 → 대기열 → 좌석선택 전체 플로우를 실제로 통과시켜서 스크린샷으로 확인, 이어서 그림자·radius 제거 후에도 홈/로그인/상세/마이페이지/좌석선택 전 화면을 다시 스크린샷으로 재확인 후 제거함.

## 1. 로컬 폴더 구조

```
sesac-ticket/
├── web/frontend/   ← 내 작업. feature/ui. git add/commit/push는 항상 여기
├── api/            ← feature/integration2를 별도로 clone해둔 완전히 독립된 저장소 (.gitignore 처리됨)
│   └── api/app/...     실제 백엔드 코드. cd api && git pull 로 최신화
└── docs/           ← 공용 문서
```
`feature/integration2`가 백엔드의 완성된 통합 브랜치 — 다른 feature 브랜치는 전부 여기 merge 완료. `main`은 아직 비어있음(초기 커밋뿐), 병합 안 됨.

## 2. Phase 진행 상황

| Phase | 내용 | 상태 |
|---|---|---|
| 0~5 | 전체 화면(로그인~관리자/고객센터) | ✅ |
| 6 | **실 API 연동** | ✅ 대부분 — 대기열 자동방출 구간만 로컬 환경 이슈로 미검증(4번 섹션) |
| 7 | **디자인 개선**(좌석 배치도 → 메인/상세 히어로 → 로그인/좌석선택/마이페이지) | 🔶 진행 중 — 3차까지 완료, 6번 섹션. 헤더/관리자/랭킹 섹션은 아직 범위 밖 |

세부 내용은 [`web/frontend/README.md`](../web/frontend/README.md) 하나로 통합돼 있음 — 실행법, 로컬 백엔드 셋업, 테스트 시나리오, 설계 결정 표 전부 그 안에 있으니 이 문서와 중복 서술하지 않음.

## 3. 다음 세션에서 바로 확인할 것 — 로컬 서버 상태

**이번 세션 종료 시점엔 로컬 백엔드가 켜져 있는 상태입니다** (Docker MySQL+Valkey, uvicorn, 워커 3개 전부 실행 중). 꺼져있으면 아래로 재기동:

```bash
docker start sesac-mysql sesac-valkey
cd api/api
uv run uvicorn app.main:app --port 8000            # 별도 터미널
uv run python -m app.workers.queue_dispatcher      # 별도 터미널
uv run python -m app.workers.hold_sweeper          # 별도 터미널
uv run python -m app.workers.reservation_sweeper   # 별도 터미널
```
`.env`는 `api/api/.env`에 이미 만들어져 있음(gitignore됨, 값은 README의 "백엔드 로컬 실행" 참고 — DB/Valkey는 `127.0.0.1`, `COOKIE_SECURE=false`). 시드 데이터(공연 5개, admin01 계정)는 컨테이너를 `stop`만 했으므로 재시드 불필요.

**테스트 계정 관련**: `test@example.com`/`passwd123`으로 로그인이 안 되는 건 버그가 아니라 이 계정이 예전 mock DB에만 있던 계정이라 실 DB엔 없어서임. `POST /auth/signup`으로 직접 만들어둠(닉네임 "테스트유저") — 지금은 로그인 됨. **로컬 DB를 새로 만들면(볼륨 삭제 등) 이 계정도 사라지니, 그럴 땐 `/signup` 화면에서 다시 가입하거나 curl로 재생성할 것.**

**✅ 로컬 임시 우회 적용됨(2026-08-20)**: `api/api/app/workers/queue_dispatcher.py`의 `dispatch_once()`에서 `client.zpopmin(key, n)` 한 줄을 `client.zrange(key, 0, n-1, withscores=True)` + `client.zrem(key, *tokens)`로 교체 — 같은 효과를 내면서 ZPOPMIN을 피함. 실 API로 직접 검증함(`POST /queue/enter` → `GET /queue/{token}/status`가 몇 초 안에 `READY`로 전환, `entryTicket` 발급 확인). **이 패치는 `api/`(백엔드팀 저장소) 안의 로컬 전용 임시 코드고 커밋/푸시 안 했음** — 백엔드팀이 진짜 원인을 고쳐서 새 코드를 주면 이 부분은 지우고 최신 코드로 덮어쓸 것. 다음 세션에서 로컬 백엔드를 다시 클론/리셋하면 이 패치가 사라지니 그럴 땐 재적용 필요.

**✅ 같은 종류의 버그를 하나 더 찾아서 우회함(2026-08-20)**: `api/api/app/domains/reservation/service.py`의 `get_seat_status_list()`에서 `client.hset(key, mapping=mapping)`(다중 필드)도 `wrong number of arguments`로 동일하게 실패 — `client.hmset(key, mapping)`(레거시, 정상 동작 확인)으로 교체함. 이게 좌석 상태 API(`GET /schedules/{scheduleId}/seats`)가 500을 내던 원인이고, 그래서 대기열 통과 후 좌석 화면이 무한 로딩이었던 것. 마찬가지로 로컬 전용 임시 코드, 커밋/푸시 안 함, 클론/리셋하면 재적용 필요. 상세 재현/격리 내용은 [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md)에 ZPOPMIN 건과 같이 정리해둠(같은 원인일 가능성 있어 백엔드팀에 함께 확인 요청).

**원래 문제(백엔드팀 확인 필요, [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md)로 공유함)**: `redis-py==8.1.0`(백엔드 `uv.lock` 고정 버전)이 `protocol=2`(RESP2 강제) 조합에서 `ZPOPMIN` 명령을 보내면 Valkey 7.2가 `unknown command`로 거부함. `ZADD`/`ZRANGE`/`ZREM`/`GET`/`SET` 등 다른 명령은 전부 정상 — `ZPOPMIN`에 국한된 문제로 재현 확인함(`app/cache/client.py`의 `protocol=2` 핸드셰이크 우회 설정과 관련된 것으로 추정, 정확한 원인은 못 밝힘). 참고로:
1. 배포 서버(`43.201.61.179:8000`)가 살아있으면 이 우회 없이도 그쪽에서 정상 동작할 가능성 있음(다른 redis-py/Valkey 버전 조합이라 문제 없을 수 있음) — 여유 되면 확인.
2. 백엔드 팀이 진짜 원인을 알려주면 로컬 우회 코드는 지우고 정식 수정으로 교체.
3. **이제 로컬 우회로 대기열→좌석선택→Hold→예매 전체 플로우를 실제로 끝까지 테스트할 수 있음** — 다음 세션에서 제일 먼저 이 플로우를 검증할 것(지금까진 코드만 고쳐두고 실행 확인은 못 했던 부분).

**사용자가 직접 재현 확인함(2026-08-20)**: 대기열에서 "2번째"로 멈추고 예상 대기시간도 계속 같은 값(6초)에 머무는 증상을 직접 겪음 — 위 버그와 정확히 일치하는 증상이었음. 로컬 우회 적용 후 같은 방식으로 재현해서 `READY` 전환과 `entryTicket` 발급을 확인함(3번 섹션 상단).

## 4. 이번 세션에서 발견한 핵심 실 계약 불일치 (전부 코드에 반영 완료)

**회원가입 이메일 인증 흐름이 완전히 잘못 설계돼 있었음**: mock은 "이메일 인증 → 회원가입" 순서를 가정했지만, 실 백엔드의 `POST /auth/email/verify-request`는 **이미 가입된 회원에게만** 코드를 발급함(`member_repository.get_member_by_email`이 `None`이면 조용히 무시). 즉 가입 전에는 인증 코드를 받을 방법이 원천적으로 없음. `POST /auth/signup`도 이메일 인증을 요구하지 않고, `login`도 `email_verified`를 확인하지 않음 — 이메일 인증은 완전히 별개의 "본인확인" 기능(마이페이지 정보수정에서 실제로 이 용도로 쓰임)이었음. **`SignupPage.tsx`에서 인증 단계를 통째로 제거**하고 바로 `signup()`을 호출하도록 수정함. 이 버그를 실제로 Playwright로 회원가입을 시도하다가 발견함 — mock으로는 절대 못 잡는 종류의 문제였음. **이게 의도된 설계인지는 [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md)로 백엔드팀에 확인 요청해둠** — 답변 오면 반영할 것.

그 외 OpenAPI 스펙(`/openapi.json`)을 직접 떠서 확인한 불일치들 (전부 README "설계 결정" 표에도 정리):
- 관심 공연 목록이 ID 배열이 아니라 `{performanceId, title, thumbnailUrl}[]`
- 예매 상세의 좌석 항목에 `seatId`가 없고(`section/row/number/grade/price`만) `depositorName` 필드 자체가 응답에 없음
- 공유 링크 발급 API가 존재하지 않음
- 좌석 등급 목록 API(`GET /performances/{id}/schedules`)가 가격/등급 정보 없는 단순 상태값만 줌 — 공연 상세 응답에 이미 포함된 `schedules`를 대신 씀
- 좌석 `row`가 숫자가 아니라 문자열
- `MemberResponse`에 `preferredGenres` 없음(대신 `status`), 마이페이지 나이대 값 목록은 여전히 미정

## 5. 나중에 할 일 — `feature/integration3`

**프론트(`feature/ui`) 작업이 다 끝나면, `feature/integration3` 브랜치를 새로 만들어서 `feature/integration2`까지 진행된 백엔드와 merge한 뒤 통합 테스트하기로 함** (사용자 지침, 2026-08-20). 지금 당장 할 일 아님 — 실 API 연동(위 3번의 대기열 이슈 포함)까지 마무리된 뒤의 다음 단계. 착수 시 어느 브랜치가 베이스인지, `feature/ui` 코드를 어떻게 합칠지 다시 확인할 것.

## 6. 디자인 개선 (`docs/토근 복구되면 할 것.md` 반영)

### 1차 (좌석 배치도 중심) — 커밋·푸시 완료
- 컬러 팔레트/폰트는 이미 `theme/tokens.ts`에 정확히 일치해서 변경 없음.
- `SeatGrid.tsx` 대대적 개편 — 예매 가능 좌석을 등급별 색상으로 구분(`components/reservations/gradeColor.ts`가 가격 높은 순으로 액센트 컬러 배정), 좌석 셀을 쿠션처럼 보이는 모양으로, 무대를 곡선 SVG로, 좌우 행(row) 라벨, 등급·가격 범례(`SeatGradeLegend.tsx`) 추가.
- 공연 목록/상세에 카테고리 칩·아이콘 있는 정보 카드 추가(실제 데이터만).

### 2차 (메인화면부터 전체적으로) — 커밋·푸시 완료
1차가 "카드 안에 아이콘 몇 개 추가" 수준이라 부족하다는 피드백("지금은 너무 데모 사이트라는 게 눈에 보일 정도") — 훨씬 과감하게 반영:
- **`PlaceholderImage.tsx` 완전 재작성**: 모든 카드가 똑같은 회색 박스였던 게 데모 티의 가장 큰 원인이라고 판단해서, 시드(공연 id)로 매번 같은 파스텔 그러데이션 "포스터 아트"를 생성하도록 바꿈. 단순 다항해시는 한 자리 숫자 id끼리 색이 거의 안 갈렸어서 FNV-1a로 교체. **새 컴포넌트를 쓸 땐 반드시 카드별로 다른 `seed`(id 등)를 넘길 것** — 같은 시드를 재사용하면 원래 문제(전부 같은 색)가 재발함.
- **`PerformanceListPage.tsx`(메인 화면)**: 상위 2개 공연을 히어로 배너로(어두운 그러데이션 오버레이 + 흰 타이틀), 카테고리를 칩 대신 아이콘+개수 타일로, 카드 호버 시 그림자+살짝 뜨는 효과.
- **`PerformanceDetailPage.tsx`**: 전체 폭 히어로 배너 + 좌(정보카드+설명)/우(가격·등급별 가격·예매 CTA가 있는 sticky 카드) 2단 레이아웃 — 전형적인 이커머스 상품 상세 구조 참고.
- 디자인 시스템의 "그림자 없음" 원칙을 "기본 상태는 보더만, 호버 등 상호작용 피드백엔 허용"으로 조정(`design-system.md` 1·4·5번 섹션).
- 검증: Playwright로 실 백엔드 붙여서 홈/상세 페이지 스크린샷 찍어 직접 확인 후 스크립트 제거.

### 3차 (세부 피드백 + 범위 확장) — 아직 커밋 안 됨, 이번 문서 0번 참고
2차 스크린샷을 보고 받은 구체적 피드백을 반영, 범위도 사용자가 직접 지정한 화면까지 확장:
- 카테고리 필터 버튼을 사각 타일 → 야놀자/인터파크 티켓 스타일 원형 아이콘 배지로 재설계(`ButtonBase` + `aria-label`로 접근성도 개선 — 원래 `Stack onClick`이라 키보드 접근이 아예 안 됐음).
- 히어로 배너가 카테고리 필터를 바꿔도 사라지지 않도록 수정("위에 고정되어있어야 하는 영역이 사라져서 엉성해 보인다"는 지적 반영).
- `PlaceholderImage`의 글자 오버레이 제거 — 그러데이션만 남김.
- **범위 확장**: 로그인/회원가입/비밀번호재설정(`AuthCard.tsx` 2단 레이아웃), 좌석선택 페이지 전체(헤더+카드 래핑), 마이페이지(프로필 헤더+탭 네비)까지 적용. **고객센터는 리스트 카드 호버 그림자 정도만 톤 맞춤** — 텍스트 위주 콘텐츠라 히어로 같은 큰 구조 변경은 안 함. 관리자 화면은 사용자가 우선순위 낮다고 해서 이번엔 손 안 댐.
- Playwright로 홈(전체/필터 상태)·로그인·마이페이지 스크린샷 재확인 후 제거.

**여전히 범위 밖인 것**: 헤더/네비게이션(RootLayout) 자체 디자인, 관리자 화면, "인기순/랭킹" 같은 섹션(`layout_ref4.jpg` 참고 여지 있으나 실제 인기 데이터가 없어서 의도적으로 안 만듦 — 필요하면 먼저 확인). `layout_ref3.jpg`(부동산 리스팅 스타일 필터 사이드바)도 아직 미반영.

### 4차 (좌석 화면 버그 수정 + 좌석 셀 모양 원복) — 아직 커밋 안 됨
- 대기열 통과 후 좌석 화면 무한 로딩 버그 수정(원인은 백엔드 HSET 이슈, 0번/3번 섹션 참고) — 이번이 실 데이터로 좌석 배치도가 처음 정상 렌더링된 시점.
- 그 과정에서 `SeatGrid.tsx`의 실제 배치 버그 발견·수정: 좌석 `x`/`y`가 그리드 인덱스가 아니라 절대 좌표였던 문제(0번 섹션 참고).
- `seat_ref` 이미지를 참고해 좌석 셀을 의자 아이콘(`EventSeatIcon`)으로 바꿔봤으나, 실제 렌더링 화면을 보여드리자 "네모 모양으로 간단하게" 해달라는 피드백을 받아 원래의 사각형 색상 셀로 되돌림. 등급별 색상 구분(`gradeColor.ts`)은 그대로 유지 — 아이콘 모양이 아니라 사각형 색상으로 구분하는 편이 이 프로젝트엔 더 맞는다는 걸 확인함.

### 5차 (그림자·radius 전면 폐지) — 아직 커밋 안 됨
- **그림자 제거**: 실 화면을 보여드리자 "그림자, 입체 효과 때문에 촌스럽다"는 피드백 → `PerformanceCard` 호버 그림자+뜨는 효과, `SeatGradeLegend`/`SeatGrid`의 inset 하이라이트, `MyReservationsPage`/`SupportListPage` 리스트 카드 호버 그림자, `SeatSelectPage` 하단바 그림자를 전부 제거. 호버는 `borderColor`(카드)나 `outline`(좌석 셀) 변화만 남김.
- **좌석 배치도 셀 축소**: 같은 화면에서 "`/schedules/1/seats`에서 좌석 가로가 너무 커서 가로 스크롤 생긴다" 지적도 같이 받음. curl로 실 데이터를 까보니 VIP/R/S 3구역이 좌표를 공유해서 **한 행에 45열**(구역당 15열)이나 되는 게 원인이었음 — `SeatGrid.tsx`의 셀 크기(34px→18px)·간격(6px→2px)·행 라벨 폭(28px→18px)을 줄이고 `SeatSelectPage`의 `Container`도 `md`→`lg`로 넓혀서, 45열이 1280px 뷰포트 안에 가로 스크롤 없이 전부 들어오게 함. 셀이 작아지면서 안에 찍던 좌석 번호는 지저분해 보여서 빼고 `title` 툴팁으로만 남김.
- **radius 전면 폐지**: 그림자를 걷어내자마자 바로 "radius도 전부 삭제, 차라리 전부 사각형으로 가자"는 요청을 받음 → `theme/tokens.ts`의 `radius` 스케일(`sm/md/lg/xl/pill`)을 전부 `0`으로 바꿔서 `theme.ts`가 참조하는 버튼/칩/카드/Paper/인풋을 한 번에 각지게 만듦. MUI 자체가 원형으로 그리는 `Avatar`/`IconButton`은 토큰이 안 먹혀서 `theme.ts`에 별도 컴포넌트 오버라이드(`MuiAvatar`/`MuiIconButton` → `borderRadius: 0`)를 추가. 컴포넌트별로 하드코딩돼 있던 `'20px'`(히어로 배너/정보카드/좌석선택 래퍼), `'50%'`(카테고리 아이콘 배지/마이페이지 아바타), `'999px'`(관심공연 하트 아이콘), `'3px'`/`'4px'`(좌석 셀/범례 스와치)도 전부 찾아서 제거.
- `docs/design-system.md` 1·4·5·6번 섹션을 "그림자·radius 둘 다 원칙적으로 안 쓴다"로 다시 정리 — 앞으로 새 컴포넌트에서 이 둘을 다시 넣지 않도록 명시해둠.
- Playwright로 로그인/홈/상세/마이페이지/좌석선택 화면을 다시 스크린샷으로 재확인(버튼·칩·검색창·히어로·카테고리 배지·아바타·좌석 셀까지 전부 각진 사각형으로 나오는 것, 좌석 화면에 가로 스크롤이 없는 것) 후 스크립트/브라우저 제거.

## 7. 프로젝트 배경

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨.
- 백엔드(`feature/integration2`)는 완성됐다고 확인됨(2026-08-20) — auth/member/admin/support/reservation/queue/performance/venue 도메인 전부 존재.
- **팀 채팅에 JWT_SECRET, SMTP 비밀번호, DB 비밀번호 같은 실제 시크릿이 평문으로 공유되는 습관 있음** — 어떤 파일/문서/메모리에도 절대 옮겨 적지 말 것. (로컬 `.env`의 `JWT_SECRET`은 매번 새로 랜덤 생성한 값이라 이 원칙과 무관함.)
- 작업 방식(mock 시절부터 지켜온 것, 실 연동에도 동일 적용): 커밋/푸시는 항상 사용자가 직접 실행, Playwright는 검증 후 항상 `npm uninstall`로 제거, 세션 끝날 때 worklog에 기록.
