"""
[모듈] api/app/db/routing.py
[담당] 공통
[역할] get_db(쓰기) / get_read_db(읽기) 두 개의 DB 세션 의존성 제공.

[구현할 것]
- get_db() -> Generator[Session, None, None]
    WriterSessionLocal 기반 세션 생성/정리. INSERT/UPDATE 및
    SELECT ... FOR UPDATE가 필요한 라우터에서 사용.
- get_read_db() -> Generator[Session, None, None]
    ReaderSessionLocal 기반 세션 생성/정리. 읽기 전용 라우터에서 사용.

[의존]
- app.db.session (WriterSessionLocal, ReaderSessionLocal)

[호출자]
- 전 도메인 router.py (Depends(get_db) 또는 Depends(get_read_db))

[주의]
- app.domains.reservation은 통째로 get_db(writer)만 사용해야 함. get_read_db는
  reader가 read_only=ON이라 SELECT FOR UPDATE 실행 시 즉시 에러.
- "내 예매 목록" 조회도 get_db(writer)를 써야 함. reader는 복제 지연 때문에
  방금 생성된 예매가 안 보일 수 있음.

[TODO] 구현 필요
"""

def get_db():
    pass


def get_read_db():
    pass
