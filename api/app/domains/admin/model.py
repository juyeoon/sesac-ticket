"""
[모듈] api/app/domains/admin/model.py
[담당] A
[역할] admin 테이블 매핑.

[구현할 것]
- class Admin(Base, TimestampMixin)
    id, admin_id, password_hash, name, role, created_at

[의존]
- app.db.base (Base, TimestampMixin)

[호출자]
- app.domains.admin.repository, service
- app.deps.auth (get_current_admin)
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Admin(Base, TimestampMixin):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
