"""
[모듈] api/app/core/lifespan.py
[담당] 공통
[역할] 앱 시작 시 DB 엔진·Valkey 풀 생성 및 Lua SCRIPT LOAD. 종료 시 자원 정리.

[구현할 것]
- lifespan(app) -> AsyncIterator[None]
    시작: app.db.session의 writer_engine/reader_engine은 모듈 import 시점에
    이미 생성됨. Valkey master 클라이언트를 얻고, cache/scripts/*.lua가
    존재하면 SCRIPT LOAD하여 SHA를 app.state.script_shas에 보관.
    종료: 엔진 dispose, Valkey 커넥션 종료.

[의존]
- app.db.session
- app.cache.client

[호출자]
- app.main (create_app에서 FastAPI(lifespan=lifespan)로 연결)

[주의]
- Lua 스크립트는 master에만 로드한다. replica는 read_only라 SCRIPT LOAD가
  거부되거나 무의미함.
- hold_seats.lua / release_seats.lua는 B 담당(예매 도메인)이 아직 작성 중일
  수 있음. 파일이 없으면 경고 로그만 남기고 넘어간다 — 병렬 작업 중 앱이
  기동 자체를 못 하면 안 되기 때문.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI

from app.cache.client import get_master_client
from app.db.session import reader_engine, writer_engine

logger = logging.getLogger(__name__)

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "cache" / "scripts"
_LUA_SCRIPTS = ["hold_seats.lua", "release_seats.lua"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    master = get_master_client()

    script_shas: dict[str, str] = {}
    for filename in _LUA_SCRIPTS:
        path = _SCRIPTS_DIR / filename
        if path.exists():
            script_shas[filename] = master.script_load(path.read_text(encoding="utf-8"))
        else:
            logger.warning("lua script not ready yet, skipping SCRIPT LOAD: %s", filename)
    app.state.script_shas = script_shas

    try:
        yield
    finally:
        writer_engine.dispose()
        reader_engine.dispose()
        master.close()
