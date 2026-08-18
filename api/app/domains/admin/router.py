"""
[모듈] api/app/domains/admin/router.py
[담당] A
[역할] 관리자 로그인.

[구현할 것]
- POST /admin/login -> AdminTokenResponse

[의존]
- app.domains.admin.service
- app.domains.admin.schema
- app.db.routing (get_db)

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.routing import get_db
from app.domains.admin import service as admin_service
from app.domains.admin.schema import AdminLoginRequest, AdminTokenResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=AdminTokenResponse)
def login(request: AdminLoginRequest, db: Session = Depends(get_db)) -> AdminTokenResponse:
    admin = admin_service.admin_login(db, admin_id=request.admin_id, password=request.password)
    access_token = create_access_token(admin.id)
    return AdminTokenResponse(access_token=access_token)
