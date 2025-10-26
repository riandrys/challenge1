from fastapi import APIRouter, status
from uuid import UUID

from fastapi.params import Depends

from app.api.deps import CurrentUser, SessionDep, get_current_user
from app.core.permissions import permission_checker
from app.repositories.comment_repository import comment_repository
from app.schemas.comment_schema import CommentCreate, CommentPublic, CommentUpdate
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
from app.services.comment_service import comment_service
from app.services.post_service import post_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/post/{post_id}",
    response_model=CommentPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_comment(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: UUID,
    comment_in: CommentCreate,
):
    await post_service.get_by_id(session, entity_id=post_id)
    comment = await comment_service.create_comment(
        session, comment_in, post_id, current_user.id
    )

    return comment


@router.get("/post/{post_id}", response_model=PaginatedResponse[CommentPublic])
async def read_comments_by_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: UUID,
    params: PaginationParams = Depends(),  # type: ignore[assignment]
    include_deleted: bool = False,
    only_deleted: bool = False,
):
    comments = await comment_service.get_by_post(
        session,
        post_id=post_id,
        params=params,
        include_deleted=include_deleted,
        only_deleted=only_deleted,
        current_user=current_user,
    )

    return comments


@router.get("/{comment_id}", response_model=CommentPublic)
async def read_comment(
    session: SessionDep,
    comment_id: UUID,
):
    comment = await comment_service.get_by_id(session, comment_id)

    return comment


@router.put("/{comment_id}", response_model=CommentPublic)
async def update_comment(
    session: SessionDep,
    current_user: CurrentUser,
    comment_id: UUID,
    comment_in: CommentUpdate,
):
    comment = await comment_service.get_by_id(session, comment_id)
    permission_checker.require_owner_or_superuser(current_user, comment)

    comment = await comment_repository.update(
        session, db_obj=comment, obj_in=comment_in
    )
    return comment


@router.delete("/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    session: SessionDep,
    current_user: CurrentUser,
    comment_id: UUID,
):
    comment = await comment_service.get_by_id(session, comment_id)
    permission_checker.require_owner_or_superuser(current_user, comment)

    await comment_service.delete(session, entity_id=comment_id)
    return MessageResponse(message="Comment deleted successfully")
