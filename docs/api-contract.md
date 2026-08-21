# API Contract

> Must API의 요청/응답 JSON을 실제 값으로 고정하는 문서.
> 통합 전 반드시 채워야 함 — 없으면 FE/BE 통합 시 전부 다시 맞춰야 한다.
> 새 API를 구현하기 전에 이 문서를 먼저 갱신한다 (FE가 mock으로 병행 개발 중).

## 목차

1. [공통 규격](#공통-규격)
2. [인증 (A)](#인증-a)
3. [회원 (A)](#회원-a)
4. [관리자 (A)](#관리자-a)
5. [대기열 (A)](#대기열-a)
6. [공연장 (B)](#공연장-b)
7. [공연정보 (B)](#공연정보-b)
8. [예매 (B)](#예매-b)
9. [결제 (B)](#결제-b)
10. [시스템 (공통)](#시스템-공통)

---

## 공통 규격

- [x] 에러 응답 포맷: `{ errorCode, message }` (`core/exceptions.py`, `core/handlers.py`)
- [x] 인증 헤더 규격: `Authorization: Bearer <accessToken>`
- [x] refreshToken은 응답 바디에 넣지 않고 **HttpOnly + SameSite=Lax 쿠키**로만 발급
      (쿠키명 `refreshToken`, path `/api/v1/auth`, 운영에서는 `Secure`, 로컬 http는
      `COOKIE_SECURE=false`로 완화)
- [x] 응답 바디 필드는 **camelCase** (api 설계서 규격). 요청 바디는 camelCase/snake_case
      둘 다 허용 (pydantic `alias_generator=to_camel` + `populate_by_name=True`)
- [ ] 성공 응답 포맷 (도메인별로 상이 — 목록 페이징 등 B 쪽 확정 필요)
- [ ] 페이징 파라미터/응답 규격 (B 담당 도메인에서 확정)
- [ ] entryTicket 헤더 규격 (`X-Entry-Ticket`, B의 Hold API 연결 시 확정)

## 인증 (A)

- [x] `POST /api/v1/auth/signup` — req `{ email, password, nickname, gender?, ageRange? }` →
      `201 { userId }`
- [x] `POST /api/v1/auth/login` — req `{ email, password }` →
      `200 { accessToken, tokenType: "Bearer", expiresIn }` (+ `refreshToken` 쿠키 발급)
- [x] `POST /api/v1/auth/refresh` — req 없음(쿠키만) →
      `200 { accessToken, tokenType, expiresIn }` / `401 AUTH_TOKEN_INVALID`
- [x] `POST /api/v1/auth/logout` — 인증 필요(access 토큰) →
      `200 { loggedOut: true }` (+ 쿠키 삭제)
- [x] `POST /api/v1/auth/password/reset-request` — req `{ email }` → `200 { sent: true }`
      (가입 여부 무관 항상 200 — 사용자 열거 공격 방지)
- [x] `POST /api/v1/auth/password/reset` — req `{ resetToken, newPassword }` →
      `200 { reset: true }` / `400 AUTH_PASSWORD_RESET_TOKEN_INVALID`
- [x] `POST /api/v1/auth/email/verify-request` — req `{ email }` → `200 { sent: true }`
      / `429 AUTH_EMAIL_VERIFICATION_TOO_MANY_REQUESTS` (쿨다운 중 재요청)
- [x] `POST /api/v1/auth/email/verify` — req `{ email, code }` → `200 { verified: true }`
      / `400 AUTH_EMAIL_VERIFICATION_CODE_INVALID`

> 이메일은 `core/mailer.py`가 실제 SMTP로 발송한다 (`SMTP_HOST` 등 `.env` 설정).
> `SMTP_HOST`가 비어있으면(로컬/테스트 기본값) 실제 발송 없이 로그로만 남기는
> 스텁 경로를 탄다 — 테스트 환경은 항상 이 경로를 사용한다.
> 재설정 토큰/인증 코드를 테스트에서 직접 확인하려면 `app.domains.auth.repository`
> 조회 함수를 쓴다 (`tests/test_password_reset.py`, `tests/test_email_verification.py` 참고).

## 회원 (A)

경로는 설계서 규격대로 `/api/v1/users/me` (Python 패키지명은 `domains/member` 유지).

- [x] `GET /api/v1/users/me` → `200 { id, email, nickname, gender, ageRange, status, emailVerified }`
- [x] `PATCH /api/v1/users/me` — req `{ nickname?, gender?, ageRange?, verificationCode }` →
      `200 { updated: true }` / `400 AUTH_EMAIL_VERIFICATION_CODE_INVALID`
      (본인인증 필요 — 먼저 `POST /auth/email/verify-request`로 코드를 받아야 함, 1회용)
- [x] `DELETE /api/v1/users/me` — req `{ password }` →
      `200 { deleted: true }` (소프트 삭제: `status=WITHDRAWN`, row 삭제 아님)
      / `401 AUTH_INVALID_CREDENTIALS`
- [x] `GET /api/v1/users/me/favorites?page=&size=` →
      `200 { content: [{ performanceId, title, thumbnailUrl }], totalElements }`
- [x] `POST /api/v1/users/me/favorites/{performanceId}` →
      `201 { favorited: true }` / `404 PERF_NOT_FOUND` / `409 MEMBER_FAVORITE_ALREADY_EXISTS`
- [x] `DELETE /api/v1/users/me/favorites/{performanceId}` →
      `200 { favorited: false }` / `404 MEMBER_FAVORITE_NOT_FOUND`

> **설계서와의 의도적인 차이:** 회원탈퇴에 `password` 확인을 요구한다 (설계서엔 body 없음).
> 탈취된 access 토큰만으로 탈퇴되는 걸 막기 위한 보안 강화이며, 논의 후 유지하기로 결정함.
>
> **아직 미구현:** `preferredGenres`(선호 장르) — `member` 테이블에 컬럼이 없어 스키마
> 변경(B와 공유 중인 `init.sql` 수정)이 필요해서 보류함.
>
> `performance`/`performance_image`는 B의 ORM 모델이 없어 관심 공연 조회는
> `domains/member/favorite_repository.py`에서 raw SQL로 직접 조회한다.

## 관리자 (A)

- [x] `POST /api/v1/admin/auth/login` — req `{ adminId, password }` →
      `200 { accessToken, tokenType: "Bearer", expiresIn }` (+ `adminRefreshToken` 쿠키 발급)
      / `401 AUTH_INVALID_CREDENTIALS`
- [x] `POST /api/v1/admin/auth/refresh` — req 없음(쿠키만) →
      `200 { accessToken, tokenType, expiresIn }` / `401 AUTH_TOKEN_INVALID`

> `adminRefreshToken`은 회원용 `refreshToken` 쿠키와 이름이 다른 별도 쿠키로 완전히
> 분리된다 (`admin:refresh:{adminId}` Valkey 키도 회원(`auth:refresh:{memberId}`)과 분리).

## 대기열 (A)

- [x] `POST /api/v1/queue/enter` — 인증 필요, req `{ performanceId, scheduleId }` →
      `200 { queueToken, position, estimatedWaitSeconds }`
- [x] `GET /api/v1/queue/{queueToken}/status` — **인증 불필요** (queueToken 자체가 자격증명) →
      `200 { status: "WAITING"|"READY", position, estimatedWaitSeconds, entryTicket }` /
      `404 QUEUE_NOT_ENTERED` (토큰 없음/만료)

> 상세 상태 전이는 `docs/queue-flow.md` 참고. queueToken(순번 조회용)과 entryTicket(Hold API
> 게이트 통과용)은 서로 다른 토큰이다.

## 공연장 (B)

- [ ] GET 좌석 배치도

## 공연정보 (B)

- [ ] GET 공연 목록 (페이징 + 카테고리 필터)
- [ ] GET 공연 상세
- [ ] GET 회차 목록

## 예매 (B)

- [ ] GET 좌석 상태 조회
- [ ] POST 좌석 Hold 생성
- [ ] DELETE Hold 해제
- [ ] GET Hold 조회
- [ ] POST 예매 생성 (무통장)
- [ ] GET 내 예매 목록

## 결제 (B)

- [ ] (예매 생성 응답에 포함되는 입금 정보 규격)

## 시스템 (공통)

- [x] `GET /api/v1/health/live` → `200 { status: "UP" }`
- [x] `GET /api/v1/health/ready` → `200 { status: "UP", checks: { db: "UP", valkey: "UP" } }` /
      `503 { status: "DOWN", checks: {...} }` (DB·Valkey 중 하나만 죽어도 503)
- [x] `GET /api/v1/version?platform=` (`ios|android|web`, 선택) →
      `200 { apiVersion, app: { latestVersion, minRequiredVersion, forceUpdate, updateUrl } }` /
      `400` (잘못된 platform 값)

> `app_version`은 분담표에서 DB 테이블로는 범위 밖이라 했던 항목이라, **테이블 없이
> `.env` 설정값 기반**으로 간단히 구현했다 (`core/config.py`의 `API_VERSION`,
> `APP_LATEST_VERSION` 등). 플랫폼별로 다른 값을 주는 기능은 없음(전부 동일 값 반환).
