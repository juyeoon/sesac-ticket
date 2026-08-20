# 프론트 작업 핸드오프 (2026-08-20 세션 종료 시점)

> 새 채팅에서 이 문서 하나만 읽으면 이어서 작업 가능하도록 정리. `feature/ui` 브랜치. **화면 Phase 0~5 전부 완료 + 실 API 연동(Phase 6)까지 대부분 완료.** MSW mock은 완전히 제거됨 — 이제 항상 실 백엔드가 필요하다.

## 0. 가장 먼저 할 것

**커밋 안 된 변경사항이 있습니다.** 이번 세션 후반부(디자인 개선 착수분)가 아직 안 올라갔습니다 — 실 API 연동 커밋(`feat: replace MSW mock with real backend integration`)은 이미 커밋·푸시 완료된 상태입니다.

이번에 새로 바뀐 것(6번 섹션 "디자인 개선"에 자세히):
- `web/frontend/src/components/reservations/gradeColor.ts`, `SeatGradeLegend.tsx`(신규) — 좌석 등급별 색상 매핑
- `SeatGrid.tsx`, `SeatLegend.tsx`, `SeatSelectPage.tsx`, `PerformanceCard.tsx`, `PerformanceDetailPage.tsx` 수정
- `web/frontend/docs/design-system.md`, `docs/frontend-worklog.md` 갱신
- `docs/ui_ref/`(레퍼런스 이미지), `docs/토근 복구되면 할 것.md`도 아직 untracked 상태 — 커밋하고 싶으면 같이 add할 것(디자인 작업의 근거 자료라 남겨두는 게 좋음)

```bash
git add docs/frontend-worklog.md docs/ui_ref "docs/토근 복구되면 할 것.md" web/frontend
git commit -m "feat: redesign seat map with grade colors, enrich performance list/detail"
git push origin feature/ui
```

**⚠️ git 조작은 항상 사용자가 직접 실행 — 이번 세션에 이 규칙을 어기고 커밋/리셋을 대신 실행해서 강하게 항의받은 적 있음.** 위 명령어도 절대 대신 실행하지 말고 그대로 전달만 할 것.

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
| 7 | **디자인 개선**(좌석 배치도 등급별 색상, 공연 목록/상세 정보 밀도) | ✅ 1차 완료 — 6번 섹션 |

세부 내용은 [`web/frontend/README.md`](../web/frontend/README.md) 하나로 통합돼 있음 — 실행법, 로컬 백엔드 셋업, 테스트 시나리오, 설계 결정 표 전부 그 안에 있으니 이 문서와 중복 서술하지 않음.

## 3. 다음 세션에서 바로 확인할 것 — 로컬 서버 상태

이번 세션에서 로컬에 Docker(MySQL+Valkey) + `uv run uvicorn` + 워커 3개를 띄워서 검증하다가, **세션 종료 시점에 전부 정지시켜둠**(컨테이너는 `stop`만 했고 `rm`은 안 해서 데이터는 남아있음). 재개 방법:

```bash
docker start sesac-mysql sesac-valkey
cd api/api
uv run uvicorn app.main:app --port 8000            # 별도 터미널
uv run python -m app.workers.queue_dispatcher      # 별도 터미널
uv run python -m app.workers.hold_sweeper          # 별도 터미널
uv run python -m app.workers.reservation_sweeper   # 별도 터미널
```
`.env`는 `api/api/.env`에 이미 만들어져 있음(gitignore됨, 값은 README의 "백엔드 로컬 실행" 참고 — DB/Valkey는 `127.0.0.1`, `COOKIE_SECURE=false`). 시드 데이터(공연 5개, admin01 계정)는 컨테이너를 `stop`만 했으므로 재시드 불필요.

**⚠️ 미해결 환경 버그 — [`backend-decisions-followup-2.md`](./backend-decisions-followup-2.md)로 백엔드팀에 공유함**: `redis-py==8.1.0`(백엔드 `uv.lock` 고정 버전)이 `protocol=2`(RESP2 강제) 조합에서 `ZPOPMIN` 명령을 보내면 Valkey 7.2가 `unknown command`로 거부함. `ZADD`/`ZRANGE`/`GET`/`SET` 등 다른 명령은 전부 정상 — `ZPOPMIN`에 국한된 문제로 재현 확인함(`app/cache/client.py`의 `protocol=2` 핸드셰이크 우회 설정과 관련된 것으로 추정, 정확한 원인은 못 밝힘). 이 명령은 대기열 dispatcher(`workers/queue_dispatcher.py`)가 대기 인원을 방출하는 핵심 로직이라, **로컬 환경에선 대기열이 영원히 WAITING에 머물고 좌석 선택 화면까지 못 넘어감.** 다음 세션에서:
1. 배포 서버(`43.201.61.179:8000`)가 살아있는지 먼저 확인 — 살아있으면 그쪽으로 연동 테스트(다른 redis-py/Valkey 버전 조합이라 문제 없을 수 있음).
2. 안 살아있으면 백엔드 팀에 이 버그를 공유하고, 임시로 `redis-py` 버전을 낮추거나 `protocol=2` 대신 다른 방식으로 우회할 수 있는지 확인 필요(단, `api/`는 백엔드 팀 저장소라 함부로 고치지 말고 상의부터).
3. 이 이슈 때문에 대기열→좌석선택→Hold→예매 전체 플로우의 "대기열 통과" 구간만 실기기 검증이 안 됐음. 나머지(좌석 배치도 렌더링, Hold, 무통장입금, 예매확인, MAX_SEATS=2 제한)는 코드 상으로는 실 계약에 맞게 고쳐뒀지만 **직접 실행해서 확인은 못 함** — 이 문제가 풀리면 제일 먼저 재검증할 것.

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

## 6. 디자인 개선 (`docs/토근 복구되면 할 것.md` 반영) — 1차 완료

`docs/ui_ref/` 레퍼런스(`color_palette.jpg`, `layout_ref*.jpg`, `seat_ref*.png/jpg`) 기준으로 반영한 내용:
- **컬러 팔레트/폰트**: 이미 `theme/tokens.ts`에 정확히 일치해서 변경 없음.
- **좌석 배치도**(가장 명확했던 요청): `SeatGrid.tsx`를 대대적으로 개편 — 예매 가능 좌석을 등급별 색상으로 구분(`components/reservations/gradeColor.ts`가 가격 높은 순으로 액센트 컬러 배정), 좌석 셀을 쿠션처럼 보이는 모양으로 변경, 무대를 곡선 SVG로 표현, 좌우 행(row) 라벨 추가, 등급·가격 범례(`SeatGradeLegend.tsx`, 신규) 추가.
- **공연 목록/상세**: `layout_ref*` 참고하되 우리 디자인 시스템의 "그림자 없음" 원칙은 유지 — 카테고리 칩, 아이콘이 있는 정보 카드 등 **실제로 있는 데이터**로만 정보 밀도를 높임(평점/리뷰처럼 없는 데이터는 추가 안 함).
- 검증: 실 백엔드 없이 확인하려고 임시 `/__preview/seats` 라우트 + 픽스처 데이터로 Playwright 스크린샷 찍어 확인 후 완전히 제거함(커밋에 안 남음).
- `web/frontend/docs/design-system.md` 6번 섹션에 등급-색 매핑 규칙 기록해둠.

**다음에 더 해볼 만한 것** (이번엔 범위 밖으로 둠): 마이페이지/고객센터/관리자 화면은 이번 패스에서 손 안 댐(요청이 공연 목록·상세·좌석에 집중돼 있었음). `layout_ref`의 필터 사이드바·정렬 같은 무거운 패턴도 화면 성격상 적용 안 함 — 필요하면 사용자에게 먼저 확인.

## 7. 프로젝트 배경

- 강사 피드백으로 **MySQL/Valkey 각 1개(replica 없음), S3 미사용**으로 인프라 단순화됨.
- 백엔드(`feature/integration2`)는 완성됐다고 확인됨(2026-08-20) — auth/member/admin/support/reservation/queue/performance/venue 도메인 전부 존재.
- **팀 채팅에 JWT_SECRET, SMTP 비밀번호, DB 비밀번호 같은 실제 시크릿이 평문으로 공유되는 습관 있음** — 어떤 파일/문서/메모리에도 절대 옮겨 적지 말 것. (로컬 `.env`의 `JWT_SECRET`은 매번 새로 랜덤 생성한 값이라 이 원칙과 무관함.)
- 작업 방식(mock 시절부터 지켜온 것, 실 연동에도 동일 적용): 커밋/푸시는 항상 사용자가 직접 실행, Playwright는 검증 후 항상 `npm uninstall`로 제거, 세션 끝날 때 worklog에 기록.
