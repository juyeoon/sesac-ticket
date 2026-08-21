from datetime import date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.session import writer_engine

_SECTIONS = [
    {"name": "A", "grade": "VIP", "x_offset": 0},
    {"name": "B", "grade": "R", "x_offset": 400},
    {"name": "C", "grade": "S", "x_offset": 800},
]
_ROWS_PER_SECTION = 10
_SEATS_PER_ROW = 15
_SEAT_SPACING = 20

_GRADE_PRICE = {"VIP": 150000, "R": 100000, "S": 70000}

_CATEGORIES = [
    {"name": "콘서트", "sort_order": 1},
    {"name": "뮤지컬", "sort_order": 2},
]

_PERFORMANCES = [
    {
        "title": "새싹 콘서트 2026",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 1 (예매중)",
        "running_time_min": 120,
        "age_limit": "12세 이상",
        "ticket_open_days": -7,  # 7일 전 오픈
        "ticket_close_days": 23,  # 23일 후 마감
        "poster_file": "01_concert.png",
    },
    {
        "title": "새싹 뮤지컬 나이트",
        "category": "뮤지컬",
        "description": "2026 새싹티켓 시드 공연 2 (예매 종료)",
        "running_time_min": 150,
        "age_limit": "전체 관람가",
        "ticket_open_days": -40,
        "ticket_close_days": -10,  # 10일 전 마감됨
        "poster_file": "02_musical.png",
    },
    {
        "title": "새싹 재즈 페스티벌",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 3 (예매 오픈 전)",
        "running_time_min": 100,
        "age_limit": "전체 관람가",
        "ticket_open_days": 10,  # 10일 후 오픈
        "ticket_close_days": 40,
        "poster_file": "03_jassfestival.png",
    },
    {
        "title": "새싹 발라드 콘서트",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 4 (예매중)",
        "running_time_min": 110,
        "age_limit": "12세 이상",
        "ticket_open_days": -3,
        "ticket_close_days": 27,
        "poster_file": "04_ballad.png",
    },
    {
        "title": "새싹 클래식 뮤지컬",
        "category": "뮤지컬",
        "description": "2026 새싹티켓 시드 공연 5 (예매 종료)",
        "running_time_min": 140,
        "age_limit": "전체 관람가",
        "ticket_open_days": -60,
        "ticket_close_days": -20,
        "poster_file": "05_classic.png",
    },
]

# performance_image.file_key에 들어갈 값. STORAGE_BASE_URL이 비어있으면(로컬 개발 기본값)
# build_image_url()이 이 값을 그대로 반환하므로, "/poster/..." 루트 상대경로로 넣어두면
# web/frontend/public/poster/에 있는 파일이 프론트 자체 정적 서빙으로 바로 열린다.
# 나중에 S3로 옮기면: file_key를 파일명만(예: "01_concert.png")으로 바꾸고
# STORAGE_BASE_URL=https://<bucket>.s3.amazonaws.com/poster 처럼 설정하면 코드 변경 없이 전환된다.
_POSTER_URL_PREFIX = "/poster"

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
                        "x": section["x_offset"] + seat_no * _SEAT_SPACING,
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

        now = datetime.now()

        category_ids = {}
        for cat in _CATEGORIES:
            category_ids[cat["name"]] = conn.execute(
                text(
                    "INSERT INTO category (name, sort_order, created_at) "
                    "VALUES (:name, :sort_order, :created_at)"
                ),
                {"name": cat["name"], "sort_order": cat["sort_order"], "created_at": now},
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

        for performance_def in _PERFORMANCES:
            ticket_close_at = now + timedelta(days=performance_def["ticket_close_days"])
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
                    "category_id": category_ids[performance_def["category"]],
                    "description": performance_def["description"],
                    "venue_id": venue_id,
                    "ticket_open_at": now + timedelta(days=performance_def["ticket_open_days"]),
                    "ticket_close_at": ticket_close_at,
                    "running_time_min": performance_def["running_time_min"],
                    "age_limit": performance_def["age_limit"],
                    "status": "ENDED" if ticket_close_at < now else "ACTIVE",
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

            conn.execute(
                text(
                    "INSERT INTO performance_image (performance_id, file_key, sort_order) "
                    "VALUES (:performance_id, :file_key, :sort_order)"
                ),
                {
                    "performance_id": performance_id,
                    "file_key": f"{_POSTER_URL_PREFIX}/{performance_def['poster_file']}",
                    "sort_order": 0,
                },
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
    print(
        "seed complete: 1 venue, 450 seats, 2 categories, 5 performances, "
        "15 schedules, 6750 schedule_seat rows"
    )


if __name__ == "__main__":
    main()
