"""baseline schema (created via api/scripts/sql/sesac_ticket_init.sql)

Revision ID: 0001_baseline
Revises:
Create Date: 2026-08-18

"""

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """이 리비전은 실제 스키마 변경을 수행하지 않는다 (raw SQL 우선 방식).

    스키마는 api/scripts/sql/sesac_ticket_init.sql을 직접 실행해서 만든다.
    신규 환경 셋업 순서:
      1) mysql -uroot -p < api/scripts/sql/sesac_ticket_init.sql
      2) (선택) mysql -uroot -p sesac_ticket < api/scripts/sql/sesac_ticket_dummy_data_1.sql
      3) cd api && alembic stamp 0001_baseline

    이후 스키마 변경은 SQLAlchemy 모델을 고치고
    `alembic revision --autogenerate`로 diff를 생성해 이 리비전 위에 쌓는다.
    """


def downgrade() -> None:
    pass
