"""
[모듈] api/scripts/seed.py
[담당] A
[역할] 개발/테스트용 초기 데이터 생성. 공연장 1개, 좌석 격자(3구역×10행×15열=450석),
       공연 3개, 회차 각 3개(총 9회차), 회차별 좌석 상태(schedule_seat) 4,050건 생성.

[구현할 것]
- build_venue_seats(venue_id) -> list[dict]: 좌석 격자 좌표 생성
- seed(engine) -> None: 전체 시드 실행
    (category -> venue -> venue_seat -> performance -> performance_seat_grade ->
     schedule -> schedule_seat 순서로 삽입, 전부 하나의 트랜잭션)
- main() -> None: CLI 진입점 (`python -m scripts.seed`)

[의존]
- sqlalchemy Core (text) — B의 venue/performance ORM 모델을 기다리지 않기 위해
  ORM이 아니라 Core로 직접 테이블에 INSERT한다.
- app.db.session (writer_engine)

[호출자]
- 수동 실행: `cd api && python -m scripts.seed`

[주의]
- api/scripts/sql/sesac_ticket_dummy_data_1.sql과는 별개의 데이터셋이다. 그쪽은
  좌석 3석짜리 예매 흐름(선점→예매→결제) 시나리오 테스트용이고, 이 스크립트는
  B가 목록/상세/회차/좌석배치도 API를 개발할 때 쓸 규모 있는 기본 데이터다.
  같은 DB에 동시에 넣으면 category/venue id가 1로 겹쳐 PK 충돌이 나므로
  둘 중 하나만 선택해서 사용할 것.
- venue/performance/schedule 테이블은 아직 SQLAlchemy 모델이 없으므로(B 담당,
  미착수) ORM이 아니라 SQLAlchemy Core의 text()로 직접 INSERT한다. B가 모델을
  만들고 나면 이 스크립트를 ORM 기반으로 바꿀 수 있다.
- 실행 전 api/scripts/sql/sesac_ticket_init.sql로 스키마가 먼저 구축되어 있어야 한다.
- 이미 데이터가 있는 DB에 재실행하면 안 된다 (idempotent 아님). seed() 시작 시
  venue 테이블이 비어있는지 확인해서 아니면 중단한다.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.session import writer_engine

_SECTIONS = [
    {"name": "A", "grade": "VIP"},
    {"name": "B", "grade": "R"},
    {"name": "C", "grade": "S"},
]
_ROWS_PER_SECTION = 10
_SEATS_PER_ROW = 15
_SEAT_SPACING = 20

_GRADE_PRICE = {"VIP": 150000, "R": 100000, "S": 70000}

_PERFORMANCES = [
    {
        "title": "새싹 콘서트 2026",
        "description": "2026 새싹티켓 시드 공연 1",
        "running_time_min": 120,
        "age_limit": "12세 이상",
    },
    {
        "title": "새싹 뮤지컬 나이트",
        "description": "2026 새싹티켓 시드 공연 2",
        "running_time_min": 150,
        "age_limit": "전체 관람가",
    },
    {
        "title": "새싹 재즈 페스티벌",
        "description": "2026 새싹티켓 시드 공연 3",
        "running_time_min": 100,
        "age_limit": "전체 관람가",
    },
]

_SCHEDULES_PER_PERFORMANCE = 3


def build_venue_seats(venue_id: int) -> list[dict]:
    seats = []
    for section in _SECTIONS:
        for row_no in range(1, _ROWS_PER_SECTION + 1):
            for seat_no in range(1, _SEATS_PER_ROW + 1):
                seats.append(
                    {
                        "venue_id": venue_id,
                        "section": section["name"],
                        "row_no": str(row_no),
                        "seat_no": seat_no,
                        "x": seat_no * _SEAT_SPACING,
                        "y": row_no * _SEAT_SPACING,
                        "grade": section["grade"],
                    }
                )
    return seats


def seed(engine: Engine) -> None:
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM venue")).scalar_one()
        if existing:
            raise RuntimeError(
                "venue 테이블에 이미 데이터가 있습니다. seed.py는 빈 DB에서만 실행하세요."
            )

        category_id = conn.execute(
            text(
                "INSERT INTO category (name, sort_order, created_at) "
                "VALUES (:name, :sort_order, :created_at)"
            ),
            {"name": "콘서트", "sort_order": 1, "created_at": datetime.now()},
        ).lastrowid

        venue_id = conn.execute(
            text("INSERT INTO venue (name, address) VALUES (:name, :address)"),
            {"name": "새싹 아레나", "address": "서울시 강남구 새싹로 123"},
        ).lastrowid

        venue_seats = build_venue_seats(venue_id)
        conn.execute(
            text(
                "INSERT INTO venue_seat "
                "(venue_id, section, row_no, seat_no, x, y, grade) "
                "VALUES (:venue_id, :section, :row_no, :seat_no, :x, :y, :grade)"
            ),
            venue_seats,
        )
        venue_seat_ids = conn.execute(
            text("SELECT id, grade FROM venue_seat WHERE venue_id = :venue_id"),
            {"venue_id": venue_id},
        ).all()

        now = datetime.now()
        for performance_def in _PERFORMANCES:
            performance_id = conn.execute(
                text(
                    "INSERT INTO performance "
                    "(title, category_id, description, venue_id, ticket_open_at, "
                    "ticket_close_at, running_time_min, age_limit, status, created_at) "
                    "VALUES (:title, :category_id, :description, :venue_id, "
                    ":ticket_open_at, :ticket_close_at, :running_time_min, "
                    ":age_limit, :status, :created_at)"
                ),
                {
                    "title": performance_def["title"],
                    "category_id": category_id,
                    "description": performance_def["description"],
                    "venue_id": venue_id,
                    "ticket_open_at": now,
                    "ticket_close_at": now + timedelta(days=30),
                    "running_time_min": performance_def["running_time_min"],
                    "age_limit": performance_def["age_limit"],
                    "status": "ACTIVE",
                    "created_at": now,
                },
            ).lastrowid

            conn.execute(
                text(
                    "INSERT INTO performance_seat_grade (performance_id, grade, price) "
                    "VALUES (:performance_id, :grade, :price)"
                ),
                [
                    {"performance_id": performance_id, "grade": grade, "price": price}
                    for grade, price in _GRADE_PRICE.items()
                ],
            )

            for i in range(_SCHEDULES_PER_PERFORMANCE):
                perf_date = date.today() + timedelta(days=7 * (i + 1))
                schedule_id = conn.execute(
                    text(
                        "INSERT INTO schedule "
                        "(performance_id, perf_date, perf_time, status, created_at) "
                        "VALUES (:performance_id, :perf_date, :perf_time, :status, :created_at)"
                    ),
                    {
                        "performance_id": performance_id,
                        "perf_date": perf_date,
                        "perf_time": "19:00:00",
                        "status": "OPEN",
                        "created_at": now,
                    },
                ).lastrowid

                conn.execute(
                    text(
                        "INSERT INTO schedule_seat "
                        "(schedule_id, venue_seat_id, grade, price, status) "
                        "VALUES (:schedule_id, :venue_seat_id, :grade, :price, :status)"
                    ),
                    [
                        {
                            "schedule_id": schedule_id,
                            "venue_seat_id": row.id,
                            "grade": row.grade,
                            "price": _GRADE_PRICE[row.grade],
                            "status": "AVAILABLE",
                        }
                        for row in venue_seat_ids
                    ],
                )


def main() -> None:
    seed(writer_engine)
    print("seed complete: 1 venue, 450 seats, 3 performances, 9 schedules, 4050 schedule_seat rows")


if __name__ == "__main__":
    main()
