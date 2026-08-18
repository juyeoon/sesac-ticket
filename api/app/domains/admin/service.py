"""
[모듈] api/app/domains/admin/service.py
[담당] A
[역할] 관리자 인증 로직.

[구현할 것]
- admin_login(db, *, admin_id, password) -> Admin

[의존]
- app.core.security (verify_password)
- app.domains.admin.repository
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.domains.admin.router

[주의]
- 무통장 입금 확인 처리는 이번 범위에서 제외(여유 시 추가).
"""

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.core.security import verify_password
from app.domains.admin import repository as admin_repository
from app.domains.admin.model import Admin


def admin_login(db: Session, *, admin_id: str, password: str) -> Admin:
    admin = admin_repository.get_admin_by_admin_id(db, admin_id)
    if admin is None or not verify_password(password, admin.password_hash):
        raise AppException(ErrorCode.AUTH_INVALID_CREDENTIALS)
    return admin
