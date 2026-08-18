"""
[모듈] api/app/core/lifespan.py
[담당] 공통
[역할] 앱 시작 시 DB 엔진·Valkey 풀 생성 및 Lua SCRIPT LOAD. 종료 시 자원 정리.

[구현할 것]
- lifespan(app: FastAPI) -> AsyncIterator[None]
    시작: app.db.session의 writer_engine/reader_engine 초기화,
    app.cache.client의 master/replica 클라이언트 생성,
    hold_seats.lua / release_seats.lua를 master에 SCRIPT LOAD하여 SHA 캐싱.
    종료: 엔진 dispose, Valkey 커넥션 종료.

[의존]
- app.db.session
- app.cache.client

[호출자]
- app.main (create_app에서 FastAPI(lifespan=lifespan)로 연결)

[주의]
- Lua 스크립트는 master에만 로드한다. replica는 read_only라 SCRIPT LOAD가
  거부되거나 무의미함.
- SCRIPT LOAD로 얻은 SHA는 app.cache.client의 EVALSHA 폴백 헬퍼가 참조.

[TODO] 구현 필요
"""

def lifespan(app):
    pass
