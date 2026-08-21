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
- TRUSTED_PROXY_HOSTS가 체인의 모든 hop(web, alb-int, alb-pub 서브넷)을 다
  신뢰하도록 넓게 잡혀 있으면, ProxyHeadersMiddleware가 request.client.host를
  "원래 클라이언트"까지 거슬러 올라간 값으로 덮어써버려서 마지막 hop(alb-int)
  자신의 순수 접속 IP가 사라진다. _CaptureDirectPeerMiddleware를
  ProxyHeadersMiddleware보다 바깥쪽(나중에 add_middleware)에 붙여서, 덮어쓰기
  전의 순수 TCP 접속 IP를 request.state.direct_peer_ip에 미리 보존해둔다
  (system/router.py의 /version clientIp가 이걸 사용).
"""

from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging


class _CaptureDirectPeerMiddleware:
    """ProxyHeadersMiddleware가 scope['client']를 덮어쓰기 전의 순수 TCP 접속 IP를
    request.state.direct_peer_ip에 보존한다."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            client = scope.get("client")
            scope.setdefault("state", {})
            scope["state"]["direct_peer_ip"] = client[0] if client else None
        await self.app(scope, receive, send)


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(title="sesac-ticket-api", lifespan=lifespan)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=settings.trusted_proxy_hosts)
    app.add_middleware(_CaptureDirectPeerMiddleware)
    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
