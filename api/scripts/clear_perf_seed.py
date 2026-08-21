"""
[모듈] api/scripts/clear_perf_seed.py
[역할] perf_seed.py로 넣은 공연 관련 데이터를 삭제. reservation 도메인이 merge된
       뒤로 schedule_seat을 참조하는 예약/선점/결제 테이블이 생겨서, 그 자식
       테이블들부터 먼저 지워야 FK 제약을 안 건드린다 (회원/예약 자체를 정리하려는
       게 아니라, 공연 데이터를 지우려면 어차피 같이 지워야 하는 것들).

[주의]
- member_favorite/reservation 계열은 이 시드가 만든 공연을 참조하는 한도 내에서만
  같이 지워지는 게 맞지만, 이 스크립트는 애초에 로컬 테스트용 전체 초기화 도구라
  범위를 안 나누고 전부 지운다.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.session import writer_engine

_TABLES_IN_DELETE_ORDER = [
    "bank_transfer_payment",
    "member_favorite",
    "reservation_seat",
    "reservation",
    "seat_hold_log",
    "schedule_seat",
    "schedule",
    "performance_seat_grade",
    "performance_image",
    "performance",
    "venue_seat",
    "venue",
    "category",
]


def clear(engine: Engine) -> None:
    with engine.begin() as conn:
        for table in _TABLES_IN_DELETE_ORDER:
            conn.execute(text(f"DELETE FROM `{table}`"))
            conn.execute(text(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1"))


def main() -> None:
    clear(writer_engine)
    print("cleared: " + ", ".join(_TABLES_IN_DELETE_ORDER))


if __name__ == "__main__":
    main()
