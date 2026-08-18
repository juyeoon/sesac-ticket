"""
[모듈] api/app/core/logging.py
[담당] 공통
[역할] JSON 로그 포맷 설정. instance_id 필드를 포함해 인스턴스별 로그 구분.

[구현할 것]
- setup_logging() -> None
- get_logger(name) -> Logger

[의존]
- app.core.config (INSTANCE_ID)

[호출자]
- app.main (create_app에서 최초 1회 호출)
- app.core.lifespan
- 전 도메인 service (필요 시)

[주의]
- api 인스턴스가 2대(api-a / api-c) 운영되므로 instance_id 없이는 로그가
  어느 인스턴스에서 발생했는지 구분 불가. 장애 추적의 최소 조건.
"""

import json
import logging
import sys

from app.core.config import get_settings


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        settings = get_settings()
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "instance_id": settings.instance_id,
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
