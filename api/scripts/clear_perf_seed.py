from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.session import writer_engine

_TABLES_IN_DELETE_ORDER = [
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
