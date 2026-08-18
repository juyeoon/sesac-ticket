"""
[모듈] api/app/core/handlers.py
[담당] 공통
[역할] 예외를 JSON 응답으로 변환. FE가 받는 에러 응답 형태를 결정하는 유일한 지점.

[구현할 것]
- app_exception_handler(request, exc: AppException) -> JSONResponse
    { "errorCode": exc.error_code, "message": exc.message } 형태로 변환.
- validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse
    FastAPI 자체 검증 에러를 동일 규격으로 변환.
- register_exception_handlers(app: FastAPI) -> None
    위 두 핸들러를 app에 등록.

[의존]
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.main (create_app에서 등록)

[주의]
- 응답 규격은 이 파일에서만 결정한다. 두 벌의 에러 응답 형태가 생기면 FE가
  분기 처리를 해야 하므로 반드시 단일화.

[TODO] 구현 필요
"""

def app_exception_handler(request, exc):
    pass


def validation_exception_handler(request, exc):
    pass


def register_exception_handlers(app):
    pass
