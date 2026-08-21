"""
[모듈] api/app/domains/system/router.py
[담당] A
[역할] /health/live(Liveness), /health/ready(Readiness), /version(앱/API 버전 조회).
       api 설계서 SYS-001/002/003에 대응.

[구현할 것]
- GET /health/live -> { status: "UP" }
- GET /health/ready -> DB·Valkey 중 하나만 죽어도 503, { status, checks: { db, valkey } }
- GET /version?platform= -> VersionResponse (clientIp/webIp/apiIp 포함)

[의존]
- app.domains.system.service

[호출자]
- app.api.v1

[주의]
- clientIp는 X-Forwarded-For 헤더값 + 마지막으로 직접 접속한 순수 IP를 합친 전체
  체인(로컬PC~alb-int)이다. request.client.host는 못 쓴다 — TRUSTED_PROXY_HOSTS가
  체인의 모든 hop을 신뢰하도록 넓게 잡혀 있으면 ProxyHeadersMiddleware가 이 값을
  "원래 클라이언트"까지 거슬러 올라간 값으로 덮어써버려서(원래 클라이언트 IP가
  중복으로 찍히는 버그가 났었음), 대신 main.py의 _CaptureDirectPeerMiddleware가
  덮어쓰기 전에 미리 보존해둔 request.state.direct_peer_ip를 쓴다.
- webIp는 X-Forwarded-For 헤더의 마지막 항목이다. nginx(web)가 /api/*를
  alb-int로 프록시할 때 자기 자신의 IP를 그 헤더 맨 끝에 append하므로
  (proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for), 그게 곧
  web 인스턴스의 IP다.
- apiIp는 request.scope["server"](이 커넥션을 받은 로컬 소켓의 (host, port))다.
  --host 0.0.0.0으로 띄워도 실제로 접속을 받은 인터페이스의 진짜 IP가 그대로
  들어온다. 예전 INSTANCE_ID/INSTANCE_AZ처럼 .env에 사람이 정해서 넣는 라벨이
  아니라 OS 소켓에서 매 요청마다 직접 얻는 실측값이라, 오토스케일링으로
  인스턴스가 늘거나 바뀌어도 별도 설정 없이 항상 맞다.
"""

from fastapi import APIRouter, HTTPException, Request

from app.domains.system import service as system_service
from app.domains.system.schema import VersionResponse

router = APIRouter(tags=["system"])


@router.get("/health/live")
def health_live() -> dict:
    return {"status": "UP"}


@router.get("/health/ready")
def health_ready() -> dict:
    db_ok = system_service.check_db()
    cache_ok = system_service.check_cache()
    checks = {"db": "UP" if db_ok else "DOWN", "valkey": "UP" if cache_ok else "DOWN"}

    if not (db_ok and cache_ok):
        raise HTTPException(status_code=503, detail={"status": "DOWN", "checks": checks})
    return {"status": "UP", "checks": checks}


@router.get("/version", response_model=VersionResponse)
def get_version(request: Request, platform: str | None = None) -> VersionResponse:
    direct_peer = getattr(request.state, "direct_peer_ip", None)
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for and direct_peer:
        client_ip = f"{forwarded_for}, {direct_peer}"
    else:
        client_ip = forwarded_for or direct_peer

    web_ip = forwarded_for.split(",")[-1].strip() if forwarded_for else None

    server_addr = request.scope.get("server")
    api_ip = server_addr[0] if server_addr else None

    info = system_service.get_version_info(platform, client_ip, web_ip, api_ip)
    return VersionResponse(**info)
