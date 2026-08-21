# B 핸드오프 문서

> A(회원/인증/대기열) 담당 작업을 `feature/integration` 브랜치로 통합 완료.
> B는 본인 작업을 이 브랜치에 merge하면 됩니다.

## 1. 브랜치

- **merge 대상: `feature/integration`** (feature/core + feature/auth + feature/db 전부 통합됨)
- `feature/performance-info`(공연/공연장 3개 커밋)는 **이미 여기 병합 완료**했습니다. B는 이제부터 `feature/integration`을 pull해서 이어서 작업하면 됩니다.
- 이후 추가 작업 push할 땐: `git fetch && git checkout feature/integration && git merge <B의-브랜치>`
- 충돌 예상 파일: `db/registry.py`, `api/v1.py` (구역별로 나뉘어 있어 자기 구역 줄만 추가하면 충돌 거의 없음)
- **참고:** B의 최초 "core infrastructure" 커밋은 A의 `feature/core`와 완전히 동일한 내용이었어서 병합 시 문제없었습니다. `api/v1.py`의 "B 구역"(performance/venue 라우터 등록)은 아직 비어있는 상태로 남겨뒀습니다 — B가 준비되면 채워주세요.

## 2. 환경변수 (.env) — 전체 목록

`api/.env.example`을 복사해서 `api/.env`로 채우면 됩니다 (git에는 안 올라감).

| 변수 | 기본값 | 설명 |
|---|---|---|
| `DB_WRITER_URL` | (필수) | writer(master) MySQL 접속 URL |
| `DB_READER_URL` | (필수) | reader(replica) MySQL 접속 URL. 개발 중엔 writer와 동일 주소 가능 |
| `DB_POOL_SIZE` | 5 | SQLAlchemy 커넥션 풀 크기 |
| `DB_POOL_RECYCLE` | 3600 | 커넥션 재활용 주기(초) |
| `VALKEY_MASTER_HOST` | (필수) | 쓰기/Lua 전용 |
| `VALKEY_MASTER_PORT` | 6379 | |
| `VALKEY_REPLICA_HOST` | (필수) | 읽기 전용. 개발 중엔 master와 동일 주소 가능 |
| `VALKEY_REPLICA_PORT` | 6379 | |
| `JWT_SECRET` | (필수) | 서명 시크릿 — **팀 전체가 같은 값을 써야** 서로 발급한 토큰을 검증 가능 |
| `JWT_ACCESS_EXPIRE_MIN` | 30 | access 토큰 만료(분) |
| `JWT_REFRESH_EXPIRE_DAYS` | 14 | refresh 토큰 만료(일) |
| `HOLD_TTL_SEC` | 300 | 좌석 선점 유지 시간(초) — B의 예매 도메인에서 사용 |
| `QUEUE_ENABLED` | true | **false면 entryTicket 검증 없이 통과** (우회 플래그, `deps/queue.py`가 참조) |
| `QUEUE_DISPATCH_BATCH_SIZE` | 50 | 대기열 방출 인원 |
| `QUEUE_POLL_INTERVAL_SEC` | 3 | 클라이언트 폴링 권장 주기(초) |
| `QUEUE_TOKEN_TTL_SEC` | 1800 | queueToken 유효시간(초) |
| `PASSWORD_RESET_TTL_SEC` | 900 | 비밀번호 재설정 토큰 유효시간 |
| `EMAIL_VERIFICATION_TTL_SEC` | 600 | 이메일 인증 코드 유효시간 |
| `EMAIL_VERIFICATION_COOLDOWN_SEC` | 60 | 이메일 인증 재요청 쿨다운 |
| `SMTP_HOST` | (비움) | **비워두면 실제 발송 없이 로그만 남김.** 로컬 개발 땐 비워두는 걸 권장 |
| `SMTP_PORT` | 587 | |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | (비움) | 실제 발송 테스트 필요하면 A에게 문의 (Gmail 앱 비밀번호 사용 중) |
| `SMTP_USE_TLS` | true | |
| `SMTP_FROM_EMAIL` / `SMTP_FROM_NAME` | | |
| `TRUSTED_PROXY_HOSTS` | * | ALB 2단 구성용. 운영에서는 nginx 내부 IP로 제한 |
| `COOKIE_SECURE` | true | refreshToken 쿠키 Secure 플래그. **로컬 http 개발 시 반드시 false로** (안 그러면 로그인해도 쿠키가 안 붙음) |
| `API_VERSION`, `APP_LATEST_VERSION`, `APP_MIN_REQUIRED_VERSION`, `APP_FORCE_UPDATE`, `APP_UPDATE_URL` | | `/version` API용 |
| `INSTANCE_ID` | api-local | 로그 구분용 (api-a / api-c) |

## 3. B가 특히 알아야 할 것

### 3-1. `db/base.py` — bigint 자동 매핑
`Base`에 `type_annotation_map = {int: BigInteger}`가 등록되어 있어서, B가 만들 `domains/performance/model.py` 등에서 `id: Mapped[int]`라고만 써도 자동으로 `BIGINT`가 됩니다. `api/scripts/sql/sesac_ticket_init.sql`의 모든 PK/FK가 bigint라서 별도 설정 없이 일치합니다.

### 3-2. `workers/base.py` — 임시 구현, 검토/교체 필요
원래 B 담당 파일인데, B 착수 전이라 A가 대기열 개발을 막지 않으려고 **최소 구현으로 임시로 만들어둠** (Valkey 분산 락 기반 리더 선출). B가 `hold_sweeper.py`를 만들 때 이 파일을 검토하고, 필요하면 그대로 재사용하거나 교체해주세요. `queue_dispatcher.py`도 이 모듈을 그대로 쓰고 있어서, 교체하면 A도 영향 받습니다 — 바꾸기 전에 한마디 해주시면 좋습니다.

### 3-3. `workers/queue_dispatcher.py` — 활성 회차 목록 연동 필요
`_dispatch_all_schedules()`가 지금은 자리표시자입니다. B의 `performance`/`schedule` 도메인이 준비되면, 활성 (performanceId, scheduleId) 목록을 조회해서 `dispatch_once(performance_id, schedule_id)`를 각각 호출하도록 이 함수를 채워주세요.

### 3-4. `deps/queue.py` — Hold API에 게이트 부착 필요
B의 예매 Hold 생성 엔드포인트(`POST /seats/hold` 등)에 `Depends(verify_entry_ticket)`을 한 줄 붙여야 대기열 게이트가 동작합니다. `QUEUE_ENABLED=false`면 검증 없이 통과하는 우회 플래그가 있으니, 대기열이 불안정해도 예매 데모는 살릴 수 있습니다.

### 3-5. `member_favorite` — B의 ORM 모델로 전환 완료
관심 공연(`domains/member/favorite_repository.py`)은 처음엔 raw SQL이었는데, B의 `domains/performance/model.py`(`Performance`, `PerformanceImage`)가 merge된 뒤 **정식 ORM 쿼리로 교체**했습니다. `member_favorite` 테이블 자체도 `domains/member/model.py`에 `MemberFavorite` ORM 모델로 새로 추가했고(`performance.id` FK), `db/registry.py`의 A 구역에 등록해뒀습니다.
- **B가 알아야 할 것**: `db/registry.py`의 **B 구역**(venue/performance import)이 아직 주석 처리라, Alembic `autogenerate`를 돌리면 `MemberFavorite`이 참조하는 `performance` 테이블 FK를 못 찾을 수 있습니다. B가 본인 구역 주석을 해제할 때 같이 해결됩니다.
- 테스트(`tests/conftest.py`)는 `domains.venue.model`을 명시적으로 import해서 `Performance.venue` 관계(문자열 참조)가 매퍼 설정 시점에 풀리게 해뒀습니다.

### 3-6. `cache/keys.py` — 공유 파일, 새 키 추가 시 상대에게 알릴 것
B가 쓸 키(`seat_status`, `hold`)는 이미 자리가 있습니다. 새 키가 필요하면 이 파일에 추가하고 A에게 알려주세요.

### 3-7. 스키마 정본은 `api/scripts/sql/sesac_ticket_init.sql`
Alembic으로 스키마를 처음부터 만들지 않습니다 (raw SQL 우선 정책). 새 DB 셋업 순서:
```
mysql -uroot -p < api/scripts/sql/sesac_ticket_init.sql
cd api && alembic stamp 0001_baseline
```
이후 스키마 변경(B가 테이블 추가/수정할 때)부터는 `alembic revision --autogenerate`로 diff를 쌓으면 됩니다.

### 3-8. `scripts/seed.py`
공연장 1개, 좌석 450석, 공연 3개, 회차 9개, `schedule_seat` 4,050건을 만들어둡니다 (raw SQL Core 기반, B의 ORM 모델 없이도 실행 가능). `cd api && python -m scripts.seed`로 실행. **빈 DB에서만 실행 가능** (재실행 시 에러).

### 3-9. 인증 관련 재사용 가능한 것들
- `deps/auth.py`의 `get_current_member`, `get_current_admin` — B의 예매/관리자 API에서 `Depends`로 바로 가져다 쓰면 됩니다.
- 에러 응답은 전부 `{errorCode, message}` 형식이고, 새 에러 코드는 `core/exceptions.py`의 `ErrorCode`에 접두사(`RESV_*` 등)로 추가하면 됩니다.
- 응답 바디는 camelCase입니다 (`pydantic`의 `alias_generator=to_camel` 패턴을 그대로 따라주세요 — 기존 도메인 스키마 파일 참고).

## 4. 테스트

`cd api && pip install -e ".[dev]" && pytest tests/` — 현재 38개 전부 PASSED. B의 테스트도 이 안에 같이 넣어주시면 됩니다.
