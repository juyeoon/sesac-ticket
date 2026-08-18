"""
[모듈] api/app/db/session.py
[담당] 공통
[역할] writer_engine / reader_engine 2개와 그에 대응하는 세션 팩토리 생성.

[구현할 것]
- writer_engine
    create_engine(settings.DB_WRITER_URL, pool_size=..., pool_recycle=3600)
- reader_engine
    create_engine(settings.DB_READER_URL, pool_size=..., pool_recycle=3600)
- WriterSessionLocal
    sessionmaker(bind=writer_engine)
- ReaderSessionLocal
    sessionmaker(bind=reader_engine)

[의존]
- app.core.config (DB_WRITER_URL, DB_READER_URL, DB_POOL_SIZE, DB_POOL_RECYCLE)

[호출자]
- app.db.routing (get_db / get_read_db)
- app.core.lifespan (초기화 트리거)

[주의]
- 개발 중에는 writer/reader URL이 같은 주소를 가리켜도 무방하지만, 엔진 객체는
  반드시 분리 생성해야 나중에 실제 복제 구성으로 전환할 때 URL만 바꿔 끼울 수 있음.

[TODO] 구현 필요
"""

writer_engine = None
reader_engine = None


def get_writer_session_local():
    pass


def get_reader_session_local():
    pass
