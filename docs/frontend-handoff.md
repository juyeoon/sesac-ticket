# 프론트 작업 핸드오프 (2026-08-20 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. `feature/ui` 브랜치, 화면은 MSW mock으로 먼저 구현하는 중.

## 0. 가장 먼저 할 것

**커밋 안 된 변경사항이 있습니다.** 이번 세션에서 Phase 4(마이페이지)를 구현한 것이 아직 안 올라갔습니다.

```bash
git status   # 아래 파일들이 보일 것
```
- `web/frontend/src/pages/mypage/` 신규 파일들 (`MyPageLayout.tsx`, `MyInfoPage.tsx`, `MyInfoEditPage.tsx`, `MyReservationsPage.tsx`, `MyFavoritesPage.tsx`, `myInfoSchemas.ts`, `reservationsApi.ts`, `userApi.ts` — `favoritesApi.ts`는 이전 세션에 이미 있던 것)
- `web/frontend/src/routes/AppRoutes.tsx` 수정 (`/mypage`를 4개 자식 라우트를 가진 nested route로 교체)
- `web/frontend/src/mocks/handlers/auth.ts` 수정 (`PATCH /users/me`가 `verificationCode`를 검증하도록 보정 — 실 스펙 필수 필드인데 mock이 안 지키고 있었음)
- `web/frontend/README.md` 수정 (Phase 4 ✅, 마이페이지 테스트 시나리오·설계 결정 추가)
- `docs/frontend-worklog.md` 수정 (이번 세션 로그 추가)

`npm run build` / `npm run lint` 둘 다 이 세션 마지막에 통과 확인했고, Playwright로 로그인→마이페이지 조회/수정→실제 예매 생성→예매목록 반영→관심공연 등록/해제→비로그인 접근까지 전체 플로우를 브라우저로 재현해 콘솔 에러 0건 확인했습니다(검증 후 제거함). 커밋 메시지 예시:
```bash
git add docs/frontend-worklog.md web/frontend
git commit -m "feat: implement mypage (info view/edit, reservations, favorites)"
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

## 4. Phase 5 시작 전 확인할 것 (다음 화면 — 관리자 로그인, 고객센터)

- 관리자 로그인(`/admin/login`)은 일반 사용자 헤더/푸터를 안 쓰는 별도 영역 — `AppRoutes.tsx`에서 `RootLayout` 밖에 이미 분리돼 있음. 관리자 전용 인증/권한 체계가 필요한데 백엔드 스펙 확인 안 됨(일반 `AuthContext`/`useAuth`와 같은 걸 쓸지, 별도 Context가 필요할지부터 확인).
- 고객센터(`/support`)는 현재 `ComingSoonPage` 플레이스홀더 — 스펙 자체가 "플레이스홀더"로만 정의돼 있어서 실제 문의 접수/FAQ 기능 범위를 먼저 백엔드·기획 쪽에 확인 필요.
- 마이페이지(Phase 4)는 완료 — 다음 세션에서 참고할 패턴: `src/pages/mypage/MyPageLayout.tsx`(서브내비 + 비로그인 안내), `MyInfoEditPage.tsx`(react-hook-form + zod + `Controller`로 MUI Select 연동, `SendCodeButton` 재사용한 인증번호 발급/검증).

## 5. 아직 안 풀린 것 / 알고 있어야 할 갭

- **Refresh Token 미구현**: accessToken만 메모리 보관, 새로고침하면 로그아웃됨. 의도적 단순화 — 실제 연동 시점에 쿠키 기반으로 다시 작업 필요.
- **카테고리 불일치**: mock엔 콘서트/뮤지컬/연극/전시 4개, 실제 백엔드 시드엔 콘서트/뮤지컬 2개뿐. 실제 연동 시 정리 필요.
- **좌석 등급 라벨 불일치**: mock은 "R석/S석" 등, 실제는 "R"/"S"/"VIP" (접미사 없음).
- **좌석 선택 최대 4석 제한**: 프론트 임의 규칙, 백엔드 확인 안 됨.
- **회차→공연 역참조 API 없음**: 좌석 선택 페이지가 라우터 state에 의존 — 새로고침하면 "다시 선택해주세요" 뜸. 백엔드에 API 추가 요청 중.
- **나이대(`ageRange`) 선택지 임의 지정**: 스펙엔 값 목록이 없어서 프론트가 "10대/20대/30대/40대/50대 이상" 5개로 정함. 실제 연동 시 백엔드가 쓰는 값과 다르면 `MyInfoEditPage.tsx`의 `AGE_RANGE_OPTIONS` 배열만 바꾸면 됨.
- 자세한 배경/전체 목록은 [`backend-decisions-needed.md`](./backend-decisions-needed.md)(1차, 백엔드 공유 완료, 답변 대기 중)와 [`backend-decisions-followup-1.md`](./backend-decisions-followup-1.md)(2차, 실제 서버 확인 후 추가분) 참고.

## 6. 프로젝트 배경 (알아두면 좋음)

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨 — 나중에 관리자 이미지 업로드 화면 만들 때 재확인 필요.
- 백엔드는 `feature/integration2` 브랜치에서 실제 구현 활발히 진행 중 (예매/고객센터 도메인 머지됨). `backend/`에서 수시로 `git pull`해서 확인.
- **팀 채팅에 JWT_SECRET, SMTP 비밀번호, DB 비밀번호 같은 실제 시크릿이 평문으로 공유되는 습관 있음** — 어떤 파일/문서/메모리에도 절대 옮겨 적지 말 것 (이번 세션 내내 지킨 원칙).
- 테스트 계정: `test@example.com` / `passwd123` (mock DB, 새로고침하면 초기화됨).
