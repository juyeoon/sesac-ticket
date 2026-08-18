"""
[모듈] api/app/main.py
[담당] 공통
[역할] FastAPI 앱 팩토리. 미들웨어·예외 핸들러 부착, 라우터 등록, lifespan 연결.

[구현할 것]
- create_app() -> FastAPI

[의존]
- app.core.config
- app.core.lifespan
- app.core.handlers
- app.core.logging
- app.api.v1

[호출자]
- gunicorn.conf.py / ASGI 엔트리포인트 (gunicorn -k uvicorn.workers.UvicornWorker app.main:app)

[주의]
- ALB가 alb-pub → nginx → alb-int → gunicorn 순으로 2단 구성됨.
  X-Forwarded-* 헤더가 두 단계를 거치므로 ProxyHeadersMiddleware의
  trusted_hosts 범위를 nginx 쪽 내부 IP로 한정할 것 (settings.trusted_proxy_hosts).
"""

from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(title="sesac-ticket-api", lifespan=lifespan)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=settings.trusted_proxy_hosts)
    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
