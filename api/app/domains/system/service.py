"""
[모듈] api/app/domains/system/service.py
[담당] A
[역할] DB·Valkey 각각 1초 타임아웃 체크.

[구현할 것]
- check_db() -> bool: writer/reader에 SELECT 1
- check_cache() -> bool: master/replica에 PING

[의존]
- app.db.session (writer_engine, reader_engine)
- app.core.config

[호출자]
- app.domains.system.router
"""

import logging

import redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import reader_engine, writer_engine

logger = logging.getLogger(__name__)

_HEALTH_TIMEOUT_SEC = 1


def check_db() -> bool:
    try:
        with writer_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        with reader_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("db health check failed")
        return False


def check_cache() -> bool:
    settings = get_settings()
    try:
        master = redis.Redis(
            host=settings.valkey_master_host,
            port=settings.valkey_master_port,
            socket_connect_timeout=_HEALTH_TIMEOUT_SEC,
            socket_timeout=_HEALTH_TIMEOUT_SEC,
        )
        replica = redis.Redis(
            host=settings.valkey_replica_host,
            port=settings.valkey_replica_port,
            socket_connect_timeout=_HEALTH_TIMEOUT_SEC,
            socket_timeout=_HEALTH_TIMEOUT_SEC,
        )
        return bool(master.ping()) and bool(replica.ping())
    except Exception:
        logger.exception("cache health check failed")
        return False
