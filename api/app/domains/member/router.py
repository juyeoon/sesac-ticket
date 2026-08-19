"""
[모듈] api/app/domains/member/router.py
[담당] A
[역할] 내 정보 조회/수정, 회원 탈퇴(소프트 삭제), 관심 공연 목록/등록/삭제.
       api 설계서 AUTH-002, 008~012에 대응. 경로는 설계서 규격대로 /users/me.

[구현할 것]
- GET /users/me -> MemberResponse
- PATCH /users/me -> UpdateResponse (verificationCode로 본인인증 필요)
- DELETE /users/me -> WithdrawResponse (비밀번호 확인, 소프트 삭제)
- GET /users/me/favorites -> FavoriteListResponse
- POST /users/me/favorites/{performanceId} -> FavoritedResponse
- DELETE /users/me/favorites/{performanceId} -> FavoritedResponse

[의존]
- app.deps.auth (get_current_member)
- app.domains.member.service
- app.db.routing (get_db)

[호출자]
- app.api.v1

[주의]
- 설계서 경로는 /api/v1/users/me이지만 Python 패키지명은 기존대로 domains/member를
  유지한다 (URL 경로와 내부 모듈명이 같을 필요는 없음).
- 탈퇴는 설계서에 없는 비밀번호 재확인을 요구한다 (탈취된 access 토큰만으로
  탈퇴되는 것을 막기 위한 의도적인 보안 강화 — 이번 정합화에서도 유지하기로 결정).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.routing import get_db
from app.deps.auth import get_current_member
from app.domains.member import service as member_service
from app.domains.member.model import Member
from app.domains.member.schema import (
    FavoriteListResponse,
    FavoritedResponse,
    MemberResponse,
    MemberUpdateRequest,
    MemberWithdrawRequest,
    UpdateResponse,
    WithdrawResponse,
)

router = APIRouter(prefix="/users", tags=["member"])


@router.get("/me", response_model=MemberResponse)
def get_my_info(member: Member = Depends(get_current_member)) -> MemberResponse:
    return MemberResponse.model_validate(member)


@router.patch("/me", response_model=UpdateResponse)
def update_my_info(
    request: MemberUpdateRequest,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> UpdateResponse:
    member_service.update_my_info(
        db,
        member,
        nickname=request.nickname,
        gender=request.gender,
        age_range=request.age_range,
        verification_code=request.verification_code,
    )
    return UpdateResponse()


@router.delete("/me", response_model=WithdrawResponse)
def withdraw(
    request: MemberWithdrawRequest,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> WithdrawResponse:
    member_service.withdraw(db, member, password=request.password)
    return WithdrawResponse()


@router.get("/me/favorites", response_model=FavoriteListResponse)
def list_favorites(
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> FavoriteListResponse:
    items, total = member_service.list_favorites(db, member)
    return FavoriteListResponse(content=items, total_elements=total)


@router.post(
    "/me/favorites/{performance_id}", response_model=FavoritedResponse, status_code=201
)
def add_favorite(
    performance_id: int,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> FavoritedResponse:
    member_service.add_favorite(db, member, performance_id=performance_id)
    return FavoritedResponse(favorited=True)


@router.delete("/me/favorites/{performance_id}", response_model=FavoritedResponse)
def remove_favorite(
    performance_id: int,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> FavoritedResponse:
    member_service.remove_favorite(db, member, performance_id=performance_id)
    return FavoritedResponse(favorited=False)
