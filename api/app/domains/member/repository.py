"""
[모듈] api/app/domains/member/repository.py
[담당] A
[역할] 이메일/ID로 회원 조회, 생성, 정보 수정, 탈퇴(소프트 삭제).

[구현할 것]
- get_member_by_email(db, email) -> Member | None
- get_member_by_id(db, member_id) -> Member | None
- create_member(db, *, email, password_hash, nickname, gender, age_range) -> Member
- update_member(db, member, *, nickname, gender, age_range) -> Member
- withdraw_member(db, member) -> Member
    실제 row는 삭제하지 않고 status=WITHDRAWN, withdrawn_at만 기록한다.
- set_password_hash(db, member, password_hash) -> Member
- mark_email_verified(db, member) -> Member

[의존]
- app.domains.member.model (Member)

[호출자]
- app.domains.auth.service
- app.domains.member.service
- app.deps.auth
"""

from datetime import datetime

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


def update_member(
    db: Session,
    member: Member,
    *,
    nickname: str | None = None,
    gender: str | None = None,
    age_range: str | None = None,
) -> Member:
    if nickname is not None:
        member.nickname = nickname
    if gender is not None:
        member.gender = gender
    if age_range is not None:
        member.age_range = age_range

    db.commit()
    db.refresh(member)
    return member


def withdraw_member(db: Session, member: Member) -> Member:
    member.status = "WITHDRAWN"
    member.withdrawn_at = datetime.now()
    db.commit()
    db.refresh(member)
    return member


def set_password_hash(db: Session, member: Member, password_hash: str) -> Member:
    member.password_hash = password_hash
    db.commit()
    db.refresh(member)
    return member


def mark_email_verified(db: Session, member: Member) -> Member:
    member.email_verified = True
    db.commit()
    db.refresh(member)
    return member
