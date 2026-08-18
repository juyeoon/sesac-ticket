"""
[모듈] api/app/domains/admin/repository.py
[담당] A
[역할] admin_id/ID로 관리자 조회 + 관리자 refresh 토큰의 Valkey 읽기/쓰기.

[구현할 것]
- get_admin_by_admin_id(db, admin_id) -> Admin | None
- get_admin_by_id(db, id) -> Admin | None
- save_admin_refresh_token(admin_id, token, ttl_sec) -> None
- get_admin_refresh_token(admin_id) -> str | None
- delete_admin_refresh_token(admin_id) -> None

[의존]
- app.domains.admin.model (Admin)
- app.cache.client (master 전용)
- app.cache.keys (admin_refresh_token)

[호출자]
- app.domains.admin.service
- app.deps.auth

[주의]
- 관리자 refresh 토큰은 회원(`auth:refresh:{memberId}`)과 완전히 분리된 키
  (`admin:refresh:{adminId}`)를 쓴다. 반드시 master 전용.
"""

from sqlalchemy.orm import Session

from app.cache.client import get_master_client
from app.cache.keys import admin_refresh_token as admin_refresh_token_key
from app.domains.admin.model import Admin


def get_admin_by_admin_id(db: Session, admin_id: str) -> Admin | None:
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()


def get_admin_by_id(db: Session, id: int) -> Admin | None:
    return db.get(Admin, id)


def save_admin_refresh_token(admin_id: int, token: str, ttl_sec: int) -> None:
    client = get_master_client()
    client.set(admin_refresh_token_key(admin_id), token, ex=ttl_sec)


def get_admin_refresh_token(admin_id: int) -> str | None:
    client = get_master_client()
    return client.get(admin_refresh_token_key(admin_id))


def delete_admin_refresh_token(admin_id: int) -> None:
    client = get_master_client()
    client.delete(admin_refresh_token_key(admin_id))
