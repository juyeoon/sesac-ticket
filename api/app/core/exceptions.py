"""
[모듈] api/app/core/exceptions.py
[담당] 공통
[역할] AppException 베이스 + ErrorCode enum. 에러 코드는 이 파일에서만 정의.

[구현할 것]
- class AppException(Exception)
    error_code: ErrorCode, message: str, status_code: int 보관.
- class ErrorCode(str, Enum)
    후보 (실제 값 없이 이름만, 접두사 규칙 준수):
    # AUTH_*
    - AUTH_INVALID_CREDENTIALS
    - AUTH_EMAIL_ALREADY_EXISTS
    - AUTH_TOKEN_EXPIRED
    - AUTH_TOKEN_INVALID
    # PERF_*
    - PERF_NOT_FOUND
    - PERF_SCHEDULE_NOT_FOUND
    # RESV_*
    - RESV_SEAT_ALREADY_HELD
    - RESV_SEAT_ALREADY_RESERVED
    - RESV_HOLD_NOT_FOUND
    - RESV_HOLD_EXPIRED
    - RESV_HOLD_OWNER_MISMATCH
    # QUEUE_*
    - QUEUE_ENTRY_TICKET_MISSING
    - QUEUE_ENTRY_TICKET_INVALID
    # COMMON_*
    - COMMON_VALIDATION_FAILED
    - COMMON_INTERNAL_ERROR

[의존]
- 없음

[호출자]
- 전 도메인 service/router, app.core.handlers

[주의]
- 접두사 규칙: AUTH_*, PERF_*, RESV_*, QUEUE_*, COMMON_*. 새 에러 코드는
  반드시 이 파일 한 곳에서만 추가한다. 각자 만들면 코드값이 겹침.

[TODO] 구현 필요
"""

class AppException(Exception):
    pass


class ErrorCode:
    pass
