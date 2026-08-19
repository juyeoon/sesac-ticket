"""
[모듈] api/app/domains/member/service.py
[담당] A
[역할] 내 정보 수정(본인인증 필요), 회원 탈퇴(소프트 삭제), 관심 공연 관리.

[구현할 것]
- update_my_info(db, member, *, nickname, gender, age_range, verification_code) -> None
    verification_code가 해당 회원 이메일로 발급된 인증 코드와 일치해야 한다
    (api 설계서 AUTH-009: "이메일 제외 회원 정보 수정 (본인 인증 필요)").
    일치하면 코드는 즉시 소모(삭제)한다.
- withdraw(db, member, *, password) -> None
    비밀번호 재확인 후 status=WITHDRAWN, withdrawn_at 기록. 실제 row는 삭제하지 않는다.
- list_favorites(db, member, *, page, size) -> tuple[list[dict], int]
- add_favorite(db, member, *, performance_id) -> None
- remove_favorite(db, member, *, performance_id) -> None

[의존]
- app.core.security (verify_password)
- app.domains.member.repository
- app.domains.member.favorite_repository
- app.domains.auth.repository (이메일 인증 코드 조회 — verification_code 검증용)
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.domains.member.router

[주의]
- 탈퇴는 비밀번호 재확인을 반드시 거친다 (탈취된 access 토큰만으로 탈퇴되는 것을 방지).
  api 설계서엔 없는 보안 강화이며, 의도적으로 유지하기로 결정함.
- 정보 수정은 verification_code 없이는 항상 실패한다. 클라이언트는 먼저
  POST /auth/email/verify-request로 코드를 받아야 한다.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.core.security import verify_password
from app.domains.auth import repository as auth_repository
from app.domains.member import favorite_repository
from app.domains.member import repository as member_repository
from app.domains.member.model import Member


def update_my_info(
    db: Session,
    member: Member,
    *,
    nickname: str | None,
    gender: str | None,
    age_range: str | None,
    verification_code: str,
) -> None:
    stored_code = auth_repository.get_email_verification_code(member.email)
    if stored_code is None or stored_code != verification_code:
        raise AppException(ErrorCode.AUTH_EMAIL_VERIFICATION_CODE_INVALID)

    member_repository.update_member(
        db, member, nickname=nickname, gender=gender, age_range=age_range
    )
    auth_repository.delete_email_verification_code(member.email)


def withdraw(db: Session, member: Member, *, password: str) -> None:
    if not verify_password(password, member.password_hash):
        raise AppException(ErrorCode.AUTH_INVALID_CREDENTIALS)

    member_repository.withdraw_member(db, member)


def list_favorites(
    db: Session, member: Member, *, page: int, size: int
) -> tuple[list[dict], int]:
    return favorite_repository.list_favorites(db, member.id, page=page, size=size)


def add_favorite(db: Session, member: Member, *, performance_id: int) -> None:
    if not favorite_repository.performance_exists(db, performance_id):
        raise AppException(ErrorCode.PERF_NOT_FOUND)
    if favorite_repository.is_favorited(db, member.id, performance_id):
        raise AppException(ErrorCode.MEMBER_FAVORITE_ALREADY_EXISTS)
    favorite_repository.add_favorite(db, member.id, performance_id)


def remove_favorite(db: Session, member: Member, *, performance_id: int) -> None:
    removed = favorite_repository.remove_favorite(db, member.id, performance_id)
    if not removed:
        raise AppException(ErrorCode.MEMBER_FAVORITE_NOT_FOUND)
