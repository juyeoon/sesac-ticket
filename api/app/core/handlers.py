"""
[모듈] api/app/core/handlers.py
[담당] 공통
[역할] 예외를 JSON 응답으로 변환. FE가 받는 에러 응답 형태를 결정하는 유일한 지점.

[구현할 것]
- app_exception_handler(request, exc) -> JSONResponse
- validation_exception_handler(request, exc) -> JSONResponse
- register_exception_handlers(app) -> None

[의존]
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.main (create_app에서 등록)

[주의]
- 응답 규격은 이 파일에서만 결정한다. 두 벌의 에러 응답 형태가 생기면 FE가
  분기 처리를 해야 하므로 반드시 단일화.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException, ErrorCode


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"errorCode": exc.error_code.value, "message": exc.message},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "errorCode": ErrorCode.COMMON_VALIDATION_FAILED.value,
            "message": str(exc.errors()),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
