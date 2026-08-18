"""
[모듈] api/app/domains/admin/repository.py
[담당] A
[역할] admin_id/ID로 관리자 조회.

[구현할 것]
- get_admin_by_admin_id(db, admin_id) -> Admin | None
- get_admin_by_id(db, id) -> Admin | None

[의존]
- app.domains.admin.model (Admin)

[호출자]
- app.domains.admin.service
- app.deps.auth
"""

from sqlalchemy.orm import Session

from app.domains.admin.model import Admin


def get_admin_by_admin_id(db: Session, admin_id: str) -> Admin | None:
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()


def get_admin_by_id(db: Session, id: int) -> Admin | None:
    return db.get(Admin, id)
