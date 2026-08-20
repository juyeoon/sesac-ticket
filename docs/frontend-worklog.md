# 프론트 작업 로그

> 세션별로 무슨 일이 있었는지 시간순으로 남기는 기록용 문서. "지금 뭘 해야 하는지"는 [`frontend-handoff.md`](./frontend-handoff.md)를 보고, "왜 이렇게 됐는지"가 궁금할 때 여기를 본다. 새 세션 끝날 때마다 아래에 새 날짜 섹션을 추가한다 (기존 기록은 수정하지 않고 append만).

---

## 2026-08-20

### 프로젝트 파악
- `skeleton.md`, `notion/` 폴더(api-contract.md, api-파일-분담표.md, OWNERSHIP.md, claude-code-스켈레톤-지침.md, 전체 프로젝트 html export), `figma/` 와이어프레임, `ref.md`를 전부 확인.
- 구글 스프레드시트(`api 설계서`, `요구사항 정의서`, `서비스 스펙 및 사용 범위` 탭)를 직접 열어서 notion 문서보다 최신인 실제 API 스펙 확보.
- git 브랜치 전략 파악: `feature/ui`(프론트), `feature/backend-skeleton` 등 백엔드 브랜치들, 최종적으로 `main`에 merge.

### 디자인 시스템 + 스캐폴드
- Vite + React 19 + TypeScript + MUI(v9) + react-router-dom + MSW로 `web/frontend` 스캐폴드 생성.
- 참고 이미지(파스텔 블루/세이지그린/바닐라옐로 + 블랙 포인트, 미니멀 대시보드 톤) 기반으로 색상 팔레트 확정, `docs/design-system.md` 작성.
- Pretendard CDN 적용, MUI 테마(`src/theme/theme.ts`) 구성.

### Phase 0~3 구현 (전부 실제 브라우저로 검증 완료)
- **Phase 0**: 공통 레이아웃(RootLayout), 인증 Context, 로그인 유도 모달.
- **Phase 1**: 로그인/회원가입(이메일 인증 포함)/비밀번호 재설정. figma 대비 변경사항 다수 발견·반영(성명→닉네임, 새 비밀번호 필드 추가 등).
  - 버그: 로그인 실패 이슈 발생 → 원인은 새 npm 패키지 추가 후 dev 서버 미재시작(Vite 의존성 사전번들링 문제)이었음, 코드 버그 아님.
- **Phase 2**: 공연 목록/검색/카테고리 필터, 공연 상세(공유하기, 관심공연 하트), 회차 선택.
- **Phase 3**: 대기열(3초 폴링, 데모용 ~7초 고정 대기) → 좌석 선택(venue 좌표 + 실시간 상태 프론트 병합) → Hold+카운트다운 타이머 → 무통장입금 예매 생성/확인.
  - **버그 발견 및 수정**: Hold 만료 시 로컬 타이머가 0이 되는 시점과 서버가 실제로 좌석을 해제하는 시점 사이 레이스 컨디션 — 로컬 타이머 0 도달 시 서버에 즉시 재확인을 강제하고, 서버 확인 후에만 화면을 되돌리도록 수정 (`useHoldCountdown.ts`).
- 매 Phase마다 Playwright를 임시로 설치해 실제 클릭 흐름을 끝까지 재현하고, 검증 후 `npm uninstall playwright`로 제거하는 패턴 확립 (상시 테스트 프레임워크는 안 두기로 함).

### 버전/서버 정보 표시 (제출 필수조건)
- Footer에 `Front v{package.json 버전} · Server v{apiVersion} (instanceId · az) · X-Forwarded-For: ...` 노출.
- `/health/*`는 k8s probe 전용이라 이 용도에 안 맞는다는 걸 확인, 대신 `/api/v1/version`(API-SYS-003)에 서버 식별 필드를 얹는 방식을 백엔드에 제안.

### 실제 배포 서버로 계약 검증
- 팀이 공유한 살아있는 백엔드 서버(`43.201.61.179:8000/docs`)의 실제 OpenAPI 스펙과 `feature/integration2`의 `api/.env.example`, `perf_seed.py`를 직접 확인.
- 발견한 불일치를 프론트 코드에 즉시 반영: `category`가 문자열이 아니라 `{id,name}` 객체, `venue`에 `address` 포함, `bankAccountInfo`는 객체가 아니라 문자열 하나, 공연 상세 응답엔 `status` 필드 자체가 없음(목록에만 있음) 등.
- gender/ageRange optional 필드 존재, Hold TTL(5분)/입금기한(24시간)/대기열 폴링(3초) 등 여러 assumption이 실제 값과 일치함을 확인.
- 이 과정에서 `docs/backend-decisions-needed.md`(1차, 이미 백엔드에 공유되어 `_answer.md`로 답변 받는 중)와 `docs/backend-decisions-followup-1.md`(2차, 실제 서버 확인 후 추가 발견분)로 문서를 나눔 — **1차 문서는 이미 공유된 것이라 이후 절대 직접 수정하지 않기로 함**, 새로 발견하는 내용은 항상 새 파일로.

### 로컬 폴더 구조 정리 (여러 번 시행착오)
- 처음엔 git worktree를 sibling 폴더에 만들고 junction으로 `sesac-ticket/api`에 연결하는 방식을 시도했으나, 사용자가 "연결 말고 진짜 파일을 그 자리에 두고 싶다"고 명확히 함.
- 시행착오: junction 제거 후 plain copy(스냅샷, 최신화 안 됨) → 그것도 아니고 "그 폴더에서 직접 git pull이 되어야 한다"는 요구 → `sesac-ticket/api`에 `feature/integration2`를 직접 clone 시도했으나 그 브랜치 자체의 루트에 이미 `api/`가 있어서 이중 중첩(`api/api/...`) 발생.
- **최종 결론**: `sesac-ticket/backend/`라는 이름으로 `feature/integration2`를 독립적으로 clone(자체 `.git` 보유, 완전히 별개 저장소). `backend/api/app/...`가 실제 코드 경로. `cd backend && git pull`로 최신화, `feature/ui` 쪽에는 `.gitignore`의 `/backend/`로 완전히 안 보이게 처리.

### 문서 정리
- `web/frontend/README.md`에 기술스택(버전 포함)/실행법/clone 시나리오 2가지(프론트만 vs 전체)/폴더구조/Mock 원리/테스트 계정/Phase 현황/화면별 테스트 시나리오/설계결정/figma 변경사항/트러블슈팅을 통합 — 기존 `docs/testing-guide.md`는 삭제(내용 흡수).
- `docs/frontend-handoff.md`(세션 간 인계용 "현재 상태" 요약), `docs/frontend-worklog.md`(지금 이 문서, 시간순 기록) 신설.
- 팀 채팅에서 얻은 프로젝트 배경(MySQL/Valkey 단일화, S3 미사용, 실제 시크릿 평문 공유 습관 등)은 개인 메모리에 저장.

### 커밋 상태
세션 종료 시점 기준 다수 변경사항이 **아직 커밋되지 않음** — `frontend-handoff.md`의 "가장 먼저 할 것" 섹션에 커밋 대상과 명령어 정리해둠.

---

## 2026-08-20 (2차 세션 — Phase 4 마이페이지)

### 커밋
- 이전 세션에서 안 올라갔던 변경사항(`fix: align frontend with real backend contract, ...`) 먼저 커밋·푸시 완료.

### Phase 4 구현 (마이페이지)
- `src/pages/mypage/`에 `MyPageLayout`(공통 서브내비 + 비로그인 시 안내 화면), `MyInfoPage`(조회), `MyInfoEditPage`(수정), `MyReservationsPage`, `MyFavoritesPage` 추가. `AppRoutes.tsx`에서 `/mypage`를 4개 자식 라우트를 가진 nested route로 교체.
- `userApi.ts`(PATCH), `reservationsApi.ts`(GET 목록) 신규 — `favoritesApi.ts`는 이전 세션에 이미 있던 것 재사용.
- **mock 핸들러 보정**: `PATCH /users/me`가 `verificationCode`를 아예 검증 안 하고 있던 걸 발견 — 회원가입과 동일하게 `db.pendingEmailCodes`로 실제 검증하도록 고침. 실 백엔드가 이 필드를 필수로 요구한다고 이미 확인된 상태라(`frontend-handoff.md`), mock만 느슨하면 나중에 실 서버 연동 시 폼이 갑자기 400 받는 걸 방지하려는 목적.
- 나이대(`ageRange`) 선택지는 스펙에 값 목록이 없어서 "10대~50대 이상" 5개로 임의 지정 — `README.md` 설계 결정 표에 flag 해둠.
- 관심 공연 목록은 `GET /users/me/favorites`가 ID 배열만 주기 때문에 `performanceApi.list()`와 프론트에서 교차 매칭.

### Playwright로 전체 플로우 검증 (완료 후 제거)
- 로그인 → 마이페이지 조회 → 정보수정(인증번호 발급/검증 포함) → **실제 예매 생성 전체 플로우**(공연상세→회차선택→대기열→좌석선점→무통장입금) → 내 예매 목록에 반영 확인 → 관심공연 등록/해제 → 비로그인 상태에서 `/mypage` 직접 접근 시 안내 화면까지 전부 브라우저로 재현, 콘솔 에러 0건.
- 테스트 스크립트 작성 중 한 번 "즐겨찾기가 목록에 안 보임"으로 실패했었는데, 원인은 코드 버그가 아니라 테스트가 `page.goto()`로 하드 네비게이션을 해서 세션(accessToken, 메모리 보관)이 날아간 것 — 오히려 "새로고침하면 로그아웃됨" 설계가 의도대로 동작함을 확인해준 케이스. 이후 클릭 기반 네비게이션으로 수정.
- 검증 끝나고 `npm uninstall playwright` + 임시 스크립트 삭제로 원복.

### 문서 갱신
- `README.md`: Phase 4 ✅로 변경(Phase 5가 다음 작업), 마이페이지 테스트 시나리오 추가, 설계 결정 표에 나이대 선택지·PATCH verificationCode mock 보정 사유 추가.
- `frontend-handoff.md`를 Phase 5(관리자 로그인·고객센터) 기준으로 갱신 예정.

### 진행 방향 확정 + `backend-decisions-followup-1_ANSWER.md` 반영
- 사용자에게 "화면 다 만들고 API 연동할지" 물어봄 → **Phase 5(관리자 로그인, 고객센터) mock까지 마무리 후 전체 API 연동**으로 확정.
- 그 과정에서 `backend/`를 pull해서 확인해보니 `feature/integration2`에 **admin(관리자 로그인)·support(고객센터) 도메인이 이미 실제로 구현·merge돼 있음**을 발견. 특히 member/admin 인증 둘 다 refresh token이 HttpOnly 쿠키로 구현됨(`auth/router.py`, `admin/router.py`) — 지금 프론트가 "의도적으로 단순화"해둔 부분이 실제로는 이미 풀려있던 셈. Phase 5 화면 범위도 실제 라우터 코드로 확인: 고객센터는 게시글 목록/상세 조회만 있고(문의 접수 기능 없음), 관리자 인증은 일반 회원과 완전히 분리된 쿠키 체계.
- 사용자가 공유해준 `docs/backend-decisions-followup-1_ANSWER.md`(2차 질문 3개 답변) 반영:
  - `/api/v1/version`의 `clientIp` 필드 — 프론트가 이미 그 이름으로 가정해뒀던 게 그대로 확정됨. 코드 변경 없음.
  - **좌석 상태에 `SOLD`가 실제로 없음** — `AVAILABLE → HELD → RESERVED`만 존재. mock 전체(타입, 시드 로직, 핸들러, 디자인 토큰, 컴포넌트, 문서)에서 `SOLD`를 `RESERVED`로 정정. 범례 라벨도 "판매 완료"→"예매 완료"로 바꿈(RESERVED가 결제 완료가 아니라 예매 생성 시점 상태라서).
  - **예매 상태에 `CANCELLED` 존재** — `PENDING_PAYMENT`/`CONFIRMED`/`CANCELLED`/`EXPIRED` 4가지로 타입과 라벨 맵에 추가(취소 기능 자체는 아직 화면 없음).
  - **entryTicket 실제 TTL이 5분**(하드코딩값, `.env`엔 없음) — 프론트가 "10분일 것"이라 추측해 9분으로 캐시하고 있던 게 실제보다 길어서, 만료된 티켓으로 좌석 선점 시도해 403 나는 실제 버그가 될 뻔했음. 4분으로 정정.
- Playwright로 좌석 선택 화면 스모트 테스트(RESERVED 좌석 렌더링/클릭 비활성화/선점 흐름) 재검증 후 제거. `npm run build`/`lint` 통과.
