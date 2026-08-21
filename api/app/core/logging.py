"""
[모듈] api/app/core/logging.py
[담당] 공통
[역할] JSON 로그 포맷 설정. instance_ip 필드를 포함해 인스턴스별 로그 구분.

[구현할 것]
- setup_logging() -> None
- get_logger(name) -> Logger

[의존]
- 없음 (socket으로 직접 로컬 IP를 구함 — .env 설정값에 의존하지 않음)

[호출자]
- app.main (create_app에서 최초 1회 호출)
- app.core.lifespan
- 전 도메인 service (필요 시)

[주의]
- api 인스턴스가 여러 대(오토스케일링 포함) 운영되므로 구분 값 없이는 로그가
  어느 인스턴스에서 발생했는지 구분 불가. 장애 추적의 최소 조건.
- 예전엔 .env의 INSTANCE_ID(사람이 정해서 넣는 라벨)를 썼는데, 오토스케일링으로
  인스턴스가 자동으로 뜨고 죽는 환경에서는 그 값을 매번 부팅 스크립트로 채워줘야
  해서 번거로웠다. 대신 UDP 소켓으로 얻은 이 인스턴스의 실제 로컬 IP를 쓴다 —
  외부로 실제 패킷을 보내지 않고(connect()만 해서 라우팅만 결정) OS가 골라주는
  로컬 IP를 얻는 방식이라 별도 설정 없이 항상 정확하다.
"""

import json
import logging
import socket
import sys


def _get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "unknown"


_INSTANCE_IP = _get_local_ip()


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "instance_ip": _INSTANCE_IP,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
