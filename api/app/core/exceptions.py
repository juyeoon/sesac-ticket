"""
[모듈] api/app/core/exceptions.py
[담당] 공통
[역할] AppException 베이스 + ErrorCode enum. 에러 코드는 이 파일에서만 정의.

[구현할 것]
- class ErrorCode(str, Enum): AUTH_*, PERF_*, RESV_*, QUEUE_*, COMMON_* 접두사
- class AppException(Exception): error_code / message / status_code 보관

[의존]
- 없음

[호출자]
- 전 도메인 service/router, app.core.handlers

[주의]
- 접두사 규칙: AUTH_*, PERF_*, RESV_*, QUEUE_*, COMMON_*. 새 에러 코드는
  반드시 이 파일 한 곳에서만 추가한다. 각자 만들면 코드값이 겹침.
"""

from enum import Enum


class ErrorCode(str, Enum):
    # AUTH_*
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_EMAIL_ALREADY_EXISTS = "AUTH_EMAIL_ALREADY_EXISTS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"

    # PERF_*
    PERF_NOT_FOUND = "PERF_NOT_FOUND"
    PERF_SCHEDULE_NOT_FOUND = "PERF_SCHEDULE_NOT_FOUND"

    # RESV_*
    RESV_SEAT_ALREADY_HELD = "RESV_SEAT_ALREADY_HELD"
    RESV_SEAT_ALREADY_RESERVED = "RESV_SEAT_ALREADY_RESERVED"
    RESV_HOLD_NOT_FOUND = "RESV_HOLD_NOT_FOUND"
    RESV_HOLD_EXPIRED = "RESV_HOLD_EXPIRED"
    RESV_HOLD_OWNER_MISMATCH = "RESV_HOLD_OWNER_MISMATCH"

    # QUEUE_*
    QUEUE_ENTRY_TICKET_MISSING = "QUEUE_ENTRY_TICKET_MISSING"
    QUEUE_ENTRY_TICKET_INVALID = "QUEUE_ENTRY_TICKET_INVALID"
    QUEUE_NOT_ENTERED = "QUEUE_NOT_ENTERED"

    # COMMON_*
    COMMON_VALIDATION_FAILED = "COMMON_VALIDATION_FAILED"
    COMMON_INTERNAL_ERROR = "COMMON_INTERNAL_ERROR"


_DEFAULT_STATUS_CODE: dict[ErrorCode, int] = {
    ErrorCode.AUTH_INVALID_CREDENTIALS: 401,
    ErrorCode.AUTH_EMAIL_ALREADY_EXISTS: 409,
    ErrorCode.AUTH_TOKEN_EXPIRED: 401,
    ErrorCode.AUTH_TOKEN_INVALID: 401,
    ErrorCode.PERF_NOT_FOUND: 404,
    ErrorCode.PERF_SCHEDULE_NOT_FOUND: 404,
    ErrorCode.RESV_SEAT_ALREADY_HELD: 409,
    ErrorCode.RESV_SEAT_ALREADY_RESERVED: 409,
    ErrorCode.RESV_HOLD_NOT_FOUND: 404,
    ErrorCode.RESV_HOLD_EXPIRED: 410,
    ErrorCode.RESV_HOLD_OWNER_MISMATCH: 403,
    ErrorCode.QUEUE_ENTRY_TICKET_MISSING: 403,
    ErrorCode.QUEUE_ENTRY_TICKET_INVALID: 403,
    ErrorCode.QUEUE_NOT_ENTERED: 404,
    ErrorCode.COMMON_VALIDATION_FAILED: 422,
    ErrorCode.COMMON_INTERNAL_ERROR: 500,
}


class AppException(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message or error_code.value
        self.status_code = status_code or _DEFAULT_STATUS_CODE.get(error_code, 500)
        super().__init__(self.message)
