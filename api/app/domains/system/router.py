"""
[모듈] api/app/domains/system/router.py
[담당] A
[역할] /health/live(Liveness), /health/ready(Readiness), /version(앱/API 버전 조회).
       api 설계서 SYS-001/002/003에 대응.

[구현할 것]
- GET /health/live -> { status: "UP" }
- GET /health/ready -> DB·Valkey 중 하나만 죽어도 503, { status, checks: { db, valkey } }
- GET /version?platform= -> VersionResponse (server/clientIp 포함)

[의존]
- app.domains.system.service

[호출자]
- app.api.v1

[주의]
- clientIp는 X-Forwarded-For 헤더값 + 마지막으로 직접 접속한 순수 IP를 합친 전체
  체인이다. X-Forwarded-For는 각 hop이 "나한테 연결한 놈이 누구였는지"만 계속
  append하는 방식이라, 이 API에 마지막으로 직접 TCP 연결한 놈(=alb-int) 자신의
  IP는 헤더에 안 남는다. request.client.host는 못 쓴다 — TRUSTED_PROXY_HOSTS가
  체인의 모든 hop을 신뢰하도록 넓게 잡혀 있으면 ProxyHeadersMiddleware가 이 값을
  "원래 클라이언트"까지 거슬러 올라간 값으로 덮어써버려서(원래 클라이언트 IP가
  중복으로 찍히는 버그가 났었음), 대신 main.py의 _CaptureDirectPeerMiddleware가
  덮어쓰기 전에 미리 보존해둔 request.state.direct_peer_ip를 쓴다.
- 헤더가 없으면(프록시 없이 직접 접속) direct_peer_ip 하나만 남는다.
- 체인 맨 끝에 이 API 인스턴스 자신의 실제 IP도 이어붙인다. request.scope["server"]는
  이 커넥션을 받은 로컬 소켓의 (host, port)라, --host 0.0.0.0으로 띄워도 실제로
  접속을 받은 인터페이스의 진짜 IP가 그대로 들어온다 (INSTANCE_ID처럼 .env로
  사람이 정해둔 라벨이 아니라, OS 소켓에서 직접 얻은 실측값). X-Forwarded-For는
  원래 "나에게 도달하기 전" 경로만 남기고 자기 자신은 안 남기는 게 표준이지만,
  여기선 화면에 전체 경로(로컬 PC~API 인스턴스)를 한 줄로 다 보여주는 게
  목적이라 의도적으로 예외를 둔다.
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

    server_addr = request.scope.get("server")
    instance_ip = server_addr[0] if server_addr else None

    info = system_service.get_version_info(platform, client_ip)
    if client_ip and instance_ip:
        info["client_ip"] = f"{client_ip}, {instance_ip}"
    else:
        info["client_ip"] = client_ip or instance_ip
    return VersionResponse(**info)
