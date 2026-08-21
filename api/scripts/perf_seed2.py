"""
[모듈] api/scripts/perf_seed2.py
[역할] perf_seed.py가 이미 만들어둔 공연 5개(1~5)에 이어서 공연 5개(6~10)를
       추가로 시딩한다. 새 venue/venue_seat을 또 만들지 않고, perf_seed.py가
       만든 기존 venue를 그대로 재사용한다(공연장은 하나뿐인 시드 설계).

[전제]
- perf_seed.py가 먼저 실행되어 venue/venue_seat이 이미 존재해야 한다.
  (venue 테이블이 비어있으면 이 스크립트는 실행을 거부한다.)

[구현할 것]
- 새 카테고리(무용/오페라) 추가 — 이미 있으면 건너뜀
- 공연 6~10 추가: performance/performance_seat_grade/performance_image/
  schedule/schedule_seat, 기존 venue_seat_id를 재사용
- force_status: 예매 기간과 무관하게 관리자가 강제로 상태를 지정한 경우
  (예: 비공개 처리)를 재현하기 위한 필드. 있으면 날짜 계산을 무시한다.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.session import writer_engine

_GRADE_PRICE = {"VIP": 150000, "R": 100000, "S": 70000}

_NEW_CATEGORIES = [
    {"name": "무용", "sort_order": 3},
    {"name": "오페라", "sort_order": 4},
]

_PERFORMANCES = [
    {
        "title": "새싹 댄스 나이트",
        "category": "무용",
        "description": "2026 새싹티켓 시드 공연 6 (예매중)",
        "running_time_min": 90,
        "age_limit": "전체 관람가",
        "ticket_open_days": -5,
        "ticket_close_days": 25,
        "poster_file": "06_dance.png",
    },
    {
        "title": "새싹 오케스트라 갈라",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 7 (예매 오픈 전)",
        "running_time_min": 130,
        "age_limit": "전체 관람가",
        "ticket_open_days": 15,
        "ticket_close_days": 45,
        "poster_file": "07_orchestra.png",
    },
    {
        "title": "새싹 인디 나이트",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 8 (예매중)",
        "running_time_min": 100,
        "age_limit": "전체 관람가",
        "ticket_open_days": -1,
        "ticket_close_days": 20,
        "poster_file": "08_indie.png",
    },
    {
        "title": "새싹 오페라의 밤",
        "category": "오페라",
        "description": "2026 새싹티켓 시드 공연 9 (예매 종료)",
        "running_time_min": 160,
        "age_limit": "12세 이상",
        "ticket_open_days": -50,
        "ticket_close_days": -15,
        "poster_file": "09_opera.png",
    },
    {
        "title": "새싹 K-POP 슈퍼콘서트",
        "category": "콘서트",
        "description": "2026 새싹티켓 시드 공연 10 (비공개 처리됨)",
        "running_time_min": 150,
        "age_limit": "전체 관람가",
        "ticket_open_days": -10,
        "ticket_close_days": 20,
        "force_status": "HIDDEN",  # 예매 기간상 ACTIVE여야 하지만 관리자가 비공개 처리한 케이스
        "poster_file": "10_kpop.png",
    },
]

# perf_seed.py의 _POSTER_URL_PREFIX와 동일한 규칙 — S3 전환 시 파일명만 남기고
# STORAGE_BASE_URL을 설정하면 코드 변경 없이 전환된다.
_POSTER_URL_PREFIX = "/poster"

_SCHEDULES_PER_PERFORMANCE = 3


def seed(engine: Engine) -> None:
    with engine.begin() as conn:
        venue_row = conn.execute(text("SELECT id FROM venue LIMIT 1")).first()
        if venue_row is None:
            raise RuntimeError(
                "venue 테이블이 비어있습니다. perf_seed2.py는 perf_seed.py를 먼저 "
                "실행해 만든 venue를 재사용합니다."
            )
        venue_id = venue_row.id

        now = datetime.now()

        category_ids = {
            row.name: row.id
            for row in conn.execute(text("SELECT id, name FROM category")).all()
        }
        for cat in _NEW_CATEGORIES:
            if cat["name"] in category_ids:
                continue
            category_ids[cat["name"]] = conn.execute(
                text(
                    "INSERT INTO category (name, sort_order, created_at) "
                    "VALUES (:name, :sort_order, :created_at)"
                ),
                {"name": cat["name"], "sort_order": cat["sort_order"], "created_at": now},
            ).lastrowid

        venue_seat_ids = conn.execute(
            text("SELECT id, grade FROM venue_seat WHERE venue_id = :venue_id"),
            {"venue_id": venue_id},
        ).all()

        for performance_def in _PERFORMANCES:
            ticket_open_at = now + timedelta(days=performance_def["ticket_open_days"])
            ticket_close_at = now + timedelta(days=performance_def["ticket_close_days"])
            if "force_status" in performance_def:
                status = performance_def["force_status"]
            elif ticket_close_at < now:
                status = "ENDED"
            elif ticket_open_at > now:
                status = "UPCOMING"
            else:
                status = "ACTIVE"

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
                    "ticket_open_at": ticket_open_at,
                    "ticket_close_at": ticket_close_at,
                    "running_time_min": performance_def["running_time_min"],
                    "age_limit": performance_def["age_limit"],
                    "status": status,
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
    n = len(_PERFORMANCES)
    print(
        f"seed2 complete: {len(_NEW_CATEGORIES)} new categories, {n} performances, "
        f"{n * _SCHEDULES_PER_PERFORMANCE} schedules, "
        f"{n * _SCHEDULES_PER_PERFORMANCE * 450} schedule_seat rows"
    )


if __name__ == "__main__":
    main()
