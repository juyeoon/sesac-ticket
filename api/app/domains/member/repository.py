"""
[모듈] api/app/domains/member/repository.py
[담당] A
[역할] 이메일/ID로 회원 조회, 생성.

[구현할 것]
- get_member_by_email(db, email) -> Member | None
- get_member_by_id(db, member_id) -> Member | None
- create_member(db, *, email, password_hash, nickname, gender, age_range) -> Member

[의존]
- app.domains.member.model (Member)

[호출자]
- app.domains.auth.service
- app.deps.auth
"""

from sqlalchemy.orm import Session

from app.domains.member.model import Member


def get_member_by_email(db: Session, email: str) -> Member | None:
    return db.query(Member).filter(Member.email == email).first()


def get_member_by_id(db: Session, member_id: int) -> Member | None:
    return db.get(Member, member_id)


def create_member(
    db: Session,
    *,
    email: str,
    password_hash: str,
    nickname: str,
    gender: str | None = None,
    age_range: str | None = None,
) -> Member:
    member = Member(
        email=email,
        password_hash=password_hash,
        nickname=nickname,
        gender=gender,
        age_range=age_range,
        status="ACTIVE",
        email_verified=False,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
