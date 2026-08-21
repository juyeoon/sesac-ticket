api/app/
├── main.py # create_app(), ProxyHeaders 미들웨어 ★
│
├── core/
│ ├── config.py # DB writer/reader URL, Valkey master/replica 분리 ★
│ ├── security.py
│ ├── exceptions.py
│ ├── handlers.py
│ ├── logging.py # instance_id를 로그에 포함 ★ (2대 구분용)
│ └── lifespan.py # 풀 2세트 생성 + Lua SCRIPT LOAD(master) ★
│
├── db/
│ ├── base.py
│ ├── session.py # ★ writer_engine / reader_engine 2개
│ ├── registry.py
│ └── routing.py # ★ get_db(쓰기) / get_read_db(읽기) 의존성
│
├── cache/
│ ├── client.py # ★ master 클라이언트 / replica 클라이언트
│ ├── keys.py
│ └── scripts/
│ ├── hold_seats.lua # master 전용
│ └── release_seats.lua
│
├── deps/
│ ├── auth.py
│ └── queue.py # entryTicket 검증
│
├── domains/
│ ├── auth/ router, schema, service, repository
│ ├── member/ + model.py
│ ├── admin/
│ ├── venue/ model: venue, venue_seat
│ ├── performance/ model: performance, category, performance_image,
│ │ performance_seat_grade, schedule
│ ├── reservation/ ★ 핵심 — 전부 writer + Valkey master
│ │ ├── model.py reservation, reservation_seat, schedule_seat, seat_hold_log
│ │ ├── repository.py
│ │ ├── hold_service.py
│ │ ├── service.py
│ │ ├── schema.py
│ │ └── router.py
│ ├── payment/ bank_transfer_payment
│ ├── queue/ 대기열 Sorted Set (master 전용)
│ └── system/
│ ├── router.py # /health/live, /health/ready ★
│ └── service.py # DB·Valkey 각각 1초 타임아웃 체크
│
├── workers/
│ ├── base.py # ★ Valkey 분산 락 기반 리더 선출
│ ├── hold_sweeper.py
│ └── queue_dispatcher.py
│
└── api/v1.py
