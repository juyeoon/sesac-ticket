"""
[모듈] api/app/main.py
[담당] 공통
[역할] FastAPI 앱 팩토리. 미들웨어·예외 핸들러 부착, 라우터 등록, lifespan 연결.

[구현할 것]
- create_app() -> FastAPI
    FastAPI 인스턴스 생성. ProxyHeadersMiddleware 등록(ALB 2단 구성이라 필수).
    app.core.lifespan.lifespan을 lifespan 인자로 연결.
    app.api.v1.router를 prefix="/api/v1"로 include.
    app.core.handlers.register_exception_handlers(app) 호출.
    app.core.logging.setup_logging() 호출.

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
  trusted_hosts 범위를 nginx 쪽 내부 IP로 한정할 것.

[TODO] 구현 필요
"""

def create_app():
    pass
