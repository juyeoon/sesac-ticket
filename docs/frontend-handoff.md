# 프론트 작업 핸드오프 (2026-08-20 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. `feature/ui` 브랜치, 화면은 MSW mock으로 먼저 구현하는 중.

## 0. 가장 먼저 할 것

**커밋 안 된 변경사항이 있습니다.** 이번 세션에서 실제 배포 서버(OpenAPI 스펙)를 확인하고 mock을 고친 것 + 새 문서들이 아직 안 올라갔습니다.

```bash
git status   # 아래 파일들이 보일 것
```
- `web/frontend/src/**` 여러 개 수정 (category 객체화, bankAccountInfo 문자열화, status 조건부 렌더링 등 — 실제 API와 맞춘 것)
- `web/frontend/.env.production` (신규)
- `web/frontend/README.md` 전면 개편 (기술스택 버전, clone 시나리오 2가지, 테스트 가이드 전부 흡수)
- `web/frontend/docs/testing-guide.md` 삭제 (README로 통합)
- `.gitignore` 수정 (`/backend/` 추가)
- `docs/backend-decisions-followup-1.md`, `docs/api-tree.md`, `docs/project-tree.md`, `docs/backend-decisions-needed_answer.md`, `docs/frontend-handoff.md`, `docs/frontend-worklog.md` (신규)

`npm run build` / `npm run lint` 둘 다 이 세션 마지막에 통과 확인했습니다. 커밋 메시지 예시:
```bash
git add .gitignore docs web/frontend
git commit -m "fix: align frontend with real backend contract, add version/X-Forwarded-For display"
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
| **4** | **마이페이지 (내정보 조회/수정, 내 예매 목록, 관심 공연 목록)** | **⬜ 다음 작업** |
| 5 | 관리자 로그인, 고객센터(플레이스홀더) | ⬜ |

세부 스택/실행법/테스트 시나리오는 [`web/frontend/README.md`](../web/frontend/README.md) 하나로 통합됐음(`testing-guide.md`는 삭제, 내용은 README로 흡수), 디자인 규칙은 [`web/frontend/docs/design-system.md`](../web/frontend/docs/design-system.md) 참고.

## 3. 다음 세션 작업 방식 (지금까지 해온 패턴)

1. 화면 구현 (mock API 핸들러 + 페이지 컴포넌트)
2. `npm run build && npm run lint` 통과 확인
3. Playwright를 **임시로 설치**해서 실제 클릭 흐름 검증 (로그인 → 화면 이동 → 액션까지 끝까지) → 검증 끝나면 `npm uninstall playwright`로 다시 제거 (이 프로젝트엔 테스트 프레임워크를 상시로 안 두기로 함)
4. `web/frontend/README.md`의 Phase 체크리스트/테스트 시나리오 갱신
5. 커밋 메시지만 제안 — **커밋/푸시는 항상 사용자가 직접 실행** (이번 세션 내내 지킨 규칙)
6. figma/스펙과 다르게 만든 부분은 반드시 이유와 함께 flag
7. **세션 끝날 때(또는 큰 마일스톤마다) [`frontend-worklog.md`](./frontend-worklog.md)에 로그 한 단락 추가** — 날짜, 한 일, 발견한 이슈 위주로 짧게. 이 핸드오프 문서는 "현재 상태 요약"이고, worklog는 "시간순 기록"이라 역할이 다름 — 둘 다 유지할 것.

## 4. Phase 4 시작 전 확인할 것 (다음 화면)

- `GET /users/me`, `PATCH /users/me` (닉네임/성별/나이대 수정, `verificationCode` 필요 — 실제 스펙에도 필수 필드로 확인됨)
- `GET /users/me/reservations` (mock 핸들러 이미 만들어둠, 페이지만 없음)
- `GET/POST/DELETE /users/me/favorites` (마찬가지로 mock 핸들러 있음, 페이지만 없음)
- 로그인 필요 라우트라 `useRequireAuth` 패턴 그대로 적용

## 5. 아직 안 풀린 것 / 알고 있어야 할 갭

- **Refresh Token 미구현**: accessToken만 메모리 보관, 새로고침하면 로그아웃됨. 의도적 단순화 — 실제 연동 시점에 쿠키 기반으로 다시 작업 필요.
- **카테고리 불일치**: mock엔 콘서트/뮤지컬/연극/전시 4개, 실제 백엔드 시드엔 콘서트/뮤지컬 2개뿐. 실제 연동 시 정리 필요.
- **좌석 등급 라벨 불일치**: mock은 "R석/S석" 등, 실제는 "R"/"S"/"VIP" (접미사 없음).
- **좌석 선택 최대 4석 제한**: 프론트 임의 규칙, 백엔드 확인 안 됨.
- **회차→공연 역참조 API 없음**: 좌석 선택 페이지가 라우터 state에 의존 — 새로고침하면 "다시 선택해주세요" 뜸. 백엔드에 API 추가 요청 중.
- 자세한 배경/전체 목록은 [`backend-decisions-needed.md`](./backend-decisions-needed.md)(1차, 백엔드 공유 완료, 답변 대기 중)와 [`backend-decisions-followup-1.md`](./backend-decisions-followup-1.md)(2차, 실제 서버 확인 후 추가분) 참고.

## 6. 프로젝트 배경 (알아두면 좋음)

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨 — 나중에 관리자 이미지 업로드 화면 만들 때 재확인 필요.
- 백엔드는 `feature/integration2` 브랜치에서 실제 구현 활발히 진행 중 (예매/고객센터 도메인 머지됨). `backend/`에서 수시로 `git pull`해서 확인.
- **팀 채팅에 JWT_SECRET, SMTP 비밀번호, DB 비밀번호 같은 실제 시크릿이 평문으로 공유되는 습관 있음** — 어떤 파일/문서/메모리에도 절대 옮겨 적지 말 것 (이번 세션 내내 지킨 원칙).
- 테스트 계정: `test@example.com` / `passwd123` (mock DB, 새로고침하면 초기화됨).
