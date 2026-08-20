# 프론트 작업 핸드오프 (2026-08-20 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. `feature/ui` 브랜치, 화면은 MSW mock으로 먼저 구현하는 중.

## 0. 가장 먼저 할 것

**Phase 4(마이페이지) 커밋은 완료됨.** 그 직후 세션에서 `docs/backend-decisions-followup-1_ANSWER.md`(백엔드 답변)를 반영한 수정사항이 아직 안 올라갔습니다.

```bash
git status   # 아래 파일들이 보일 것
```
- 좌석 상태 `SOLD` → `RESERVED`로 전면 정정 (`seatApi.ts`, `mocks/data/store.ts`, `mocks/seatStatus.ts`, `mocks/handlers/reservations.ts`, `theme/tokens.ts`의 `seat.soldBg/soldText` → `reservedBg/reservedText`, `SeatGrid.tsx`, `SeatLegend.tsx`) — 실제 백엔드엔 `SOLD` 상태 자체가 없고 `AVAILABLE → HELD → RESERVED`만 존재한다고 확인됨.
- 예매 상태에 `CANCELLED` 추가 (`reservationApi.ts`, `mypage/reservationsApi.ts`, `ReservationConfirmPage.tsx`/`MyReservationsPage.tsx`의 `STATUS_LABEL`) — 실제 `reservation.status`엔 `PENDING_PAYMENT`/`CONFIRMED`/`CANCELLED`/`EXPIRED` 4가지가 있다고 확인됨(취소 기능 자체는 아직 화면에 없음, 타입만 대응).
- `entryTicketStorage.ts`의 세션스토리지 캐시 TTL을 9분 → 4분으로 정정 — 실제 entryTicket TTL이 5분(`_ENTRY_TICKET_TTL_SEC=300`, 하드코딩값)으로 확인됨. **9분으로 뒀으면 캐시가 아직 유효하다고 착각한 채로 만료된 entryTicket을 좌석 선점에 써서 403이 났을 것** — 실제 버그가 될 뻔한 부분.
- `/api/v1/version`의 `clientIp` 필드명이 프론트 가정 그대로 확정됨 — 코드 변경 없음, 관련 주석만 "확인 필요"에서 "확정됨"으로 정리.
- `docs/frontend-worklog.md`, `web/frontend/README.md`(설계 결정 표) 갱신.

`npm run build` / `npm run lint` 통과 확인 필요 (이 수정 이후 아직 안 돌려봄 — 다음 세션에서 제일 먼저 할 것). 커밋 메시지 예시:
```bash
git add docs/frontend-worklog.md web/frontend
git commit -m "fix: align seat/reservation status enums with confirmed backend contract"
git push origin feature/ui
```

## 1. 로컬 폴더 구조 (중요 — 실수로 헷갈리지 말 것)

```
sesac-ticket/
├── web/frontend/   ← 내 작업. feature/ui. git add/commit/push는 항상 여기
├── backend/        ← feature/integration2를 별도로 clone해둔 완전히 독립된 저장소
│   └── api/app/...     실제 백엔드 코드. cd backend && git pull 로 최신화
└── docs/           ← 공용 문서 (백엔드 팀과 공유하는 것들)
```
`backend/`는 `.gitignore`에 있어서 `feature/ui`엔 절대 안 잡힙니다. **새 채팅에서 다시 만들 필요 없음 — 이미 있음.**

## 2. Phase 진행 상황

| Phase | 내용 | 상태 |
|---|---|---|
| 0 | 공통 레이아웃, 인증 Context, 로그인 유도 모달 | ✅ |
| 1 | 로그인 / 회원가입(이메일 인증) / 비밀번호 재설정 | ✅ |
| 2 | 공연 목록·검색·카테고리 필터, 공연 상세(공유·관심공연), 회차 선택 | ✅ |
| 3 | 대기열, 좌석 선택+Hold+타이머, 무통장입금 예매 생성/확인 | ✅ |
| 4 | 마이페이지 (내정보 조회/수정, 내 예매 목록, 관심 공연 목록) | ✅ |
| **5** | **관리자 로그인, 고객센터(플레이스홀더)** | **⬜ 다음 작업** |

세부 스택/실행법/테스트 시나리오는 [`web/frontend/README.md`](../web/frontend/README.md) 하나로 통합됐음(`testing-guide.md`는 삭제, 내용은 README로 흡수), 디자인 규칙은 [`web/frontend/docs/design-system.md`](../web/frontend/docs/design-system.md) 참고.

## 3. 다음 세션 작업 방식 (지금까지 해온 패턴)

1. 화면 구현 (mock API 핸들러 + 페이지 컴포넌트)
2. `npm run build && npm run lint` 통과 확인
3. Playwright를 **임시로 설치**해서 실제 클릭 흐름 검증 (로그인 → 화면 이동 → 액션까지 끝까지) → 검증 끝나면 `npm uninstall playwright`로 다시 제거 (이 프로젝트엔 테스트 프레임워크를 상시로 안 두기로 함)
4. `web/frontend/README.md`의 Phase 체크리스트/테스트 시나리오 갱신
5. 커밋 메시지만 제안 — **커밋/푸시는 항상 사용자가 직접 실행** (이번 세션 내내 지킨 규칙)
6. figma/스펙과 다르게 만든 부분은 반드시 이유와 함께 flag
7. **세션 끝날 때(또는 큰 마일스톤마다) [`frontend-worklog.md`](./frontend-worklog.md)에 로그 한 단락 추가** — 날짜, 한 일, 발견한 이슈 위주로 짧게. 이 핸드오프 문서는 "현재 상태 요약"이고, worklog는 "시간순 기록"이라 역할이 다름 — 둘 다 유지할 것.

## 4. 진행 방향 합의 (2026-08-20, 사용자 확인)

**"화면 다 만들고 나서 API 연동할지" 질문에 → Phase 5 mock까지 마무리한 뒤, 리프레시 토큰/CORS 같은 인프라 작업을 한 번에 처리하면서 전체 도메인을 Swagger 기준 실 API로 전환하는 순서로 확정.** 순서: (1) Phase 5(관리자 로그인, 고객센터) mock 구현 → (2) 화면 전체 완성 후 별도 세션(들)에서 실 API 연동 착수.

`backend/`를 pull해서 실 API 연동 착수 시 참고할 것들을 미리 확인해둠:
- **member/admin 인증 둘 다 refresh token이 HttpOnly 쿠키로 실제 구현돼 있음** (`api/app/domains/auth/router.py`, `api/app/domains/admin/router.py`) — `POST /auth/refresh`(쿠키명 `refreshToken`, path `/api/v1/auth`), `POST /admin/auth/refresh`(쿠키명 `adminRefreshToken`, path `/api/v1/admin/auth`), 둘 다 completely 분리됨. 지금 프론트의 "accessToken 메모리만 보관, refresh 없음" 단순화를 실 연동 시점에 걷어내야 함 — fetch client에 401 시 자동 재발급 인터셉터 추가 필요.
- **크로스오리진 쿠키 이슈 주의**: 로컬 프론트(5173) ↔ 배포된 백엔드(8000) 간에 refresh 쿠키를 주고받으려면 `fetch`에 `credentials: 'include'`, 백엔드 CORS에 `allow_credentials=True` + 와일드카드 아닌 명시적 origin이 필요. 실 연동 착수 전에 백엔드 CORS 설정부터 확인.
- **관리자 로그인 실제 스펙 확인됨**: `POST /admin/auth/login`(`{admin_id, password}` → access token + refresh 쿠키), `POST /admin/auth/refresh`. 일반 회원과 별개의 인증 체계(별도 쿠키명·경로)로 구현돼 있어서, 프론트도 `AuthContext`를 공유하지 말고 관리자 전용 Context를 새로 만드는 게 맞아 보임.
- **고객센터 실제 스펙 확인됨**: `GET /support/posts`(목록, `page`/`size`/`category` 쿼리, 인증 불필요), `GET /support/posts/{id}`(상세, 인증 불필요) — **읽기 전용 게시글 목록/상세**이지 문의 접수(글쓰기) 기능이 아님. Phase 5 화면은 이 범위로 설계하면 됨(문의 작성 폼은 스펙에 없음).
- 마이페이지(Phase 4)는 완료 — 참고할 패턴: `src/pages/mypage/MyPageLayout.tsx`(서브내비 + 비로그인 안내), `MyInfoEditPage.tsx`(react-hook-form + zod + `Controller`로 MUI Select 연동, `SendCodeButton` 재사용한 인증번호 발급/검증).

## 5. 아직 안 풀린 것 / 알고 있어야 할 갭

- **Refresh Token 미구현(mock)**: accessToken만 메모리 보관, 새로고침하면 로그아웃됨. 의도적 단순화 — 실제 백엔드엔 이미 쿠키 기반으로 구현돼 있음을 확인함(4번 항목 참고), 실 API 연동 시점에 프론트도 맞춰야 함.
- **카테고리 불일치**: mock엔 콘서트/뮤지컬/연극/전시 4개, 실제 백엔드 시드엔 콘서트/뮤지컬 2개뿐. 실제 연동 시 정리 필요.
- **좌석 등급 라벨 불일치**: mock은 "R석/S석" 등, 실제는 "R"/"S"/"VIP" (접미사 없음).
- **좌석 선택 최대 4석 제한**: 프론트 임의 규칙, 백엔드 확인 안 됨.
- **회차→공연 역참조 API 없음**: 좌석 선택 페이지가 라우터 state에 의존 — 새로고침하면 "다시 선택해주세요" 뜸. 백엔드에 API 추가 요청 중.
- **나이대(`ageRange`) 선택지 임의 지정**: 스펙엔 값 목록이 없어서 프론트가 "10대/20대/30대/40대/50대 이상" 5개로 정함. 실제 연동 시 백엔드가 쓰는 값과 다르면 `MyInfoEditPage.tsx`의 `AGE_RANGE_OPTIONS` 배열만 바꾸면 됨.
- ~~좌석 상태 `SOLD`~~ → **`RESERVED`로 확인·수정 완료**(0번 항목), ~~entryTicket 캐시 TTL 9분~~ → **4분으로 수정 완료**, ~~`/version`의 `clientIp` 필드명~~ → **프론트 가정 그대로 확정**. 전부 `backend-decisions-followup-1_ANSWER.md`에서 답변받음.
- 자세한 배경/전체 목록은 [`backend-decisions-needed.md`](./backend-decisions-needed.md)(1차, 답변 완료 `_answer.md`)와 [`backend-decisions-followup-1.md`](./backend-decisions-followup-1.md) + [`backend-decisions-followup-1_ANSWER.md`](./backend-decisions-followup-1_ANSWER.md)(2차, 답변 완료) 참고.

## 6. 프로젝트 배경 (알아두면 좋음)

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨 — 나중에 관리자 이미지 업로드 화면 만들 때 재확인 필요.
- 백엔드는 `feature/integration2` 브랜치에서 실제 구현 활발히 진행 중 (예매/고객센터 도메인 머지됨). `backend/`에서 수시로 `git pull`해서 확인.
- **팀 채팅에 JWT_SECRET, SMTP 비밀번호, DB 비밀번호 같은 실제 시크릿이 평문으로 공유되는 습관 있음** — 어떤 파일/문서/메모리에도 절대 옮겨 적지 말 것 (이번 세션 내내 지킨 원칙).
- 테스트 계정: `test@example.com` / `passwd123` (mock DB, 새로고침하면 초기화됨).
