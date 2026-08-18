"""
[모듈] api/app/db/session.py
[담당] 공통
[역할] writer_engine / reader_engine 2개와 그에 대응하는 세션 팩토리 생성.

[구현할 것]
- writer_engine, reader_engine
- WriterSessionLocal, ReaderSessionLocal

[의존]
- app.core.config (DB_WRITER_URL, DB_READER_URL, DB_POOL_SIZE, DB_POOL_RECYCLE)

[호출자]
- app.db.routing (get_db / get_read_db)
- app.core.lifespan (dispose)

[주의]
- 개발 중에는 writer/reader URL이 같은 주소를 가리켜도 무방하지만, 엔진 객체는
  반드시 분리 생성해야 나중에 실제 복제 구성으로 전환할 때 URL만 바꿔 끼울 수 있음.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

_settings = get_settings()

writer_engine = create_engine(
    _settings.db_writer_url,
    pool_size=_settings.db_pool_size,
    pool_recycle=_settings.db_pool_recycle,
    pool_pre_ping=True,
)
reader_engine = create_engine(
    _settings.db_reader_url,
    pool_size=_settings.db_pool_size,
    pool_recycle=_settings.db_pool_recycle,
    pool_pre_ping=True,
)

WriterSessionLocal = sessionmaker(bind=writer_engine, autoflush=False, autocommit=False)
ReaderSessionLocal = sessionmaker(bind=reader_engine, autoflush=False, autocommit=False)
