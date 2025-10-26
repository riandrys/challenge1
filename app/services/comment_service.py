from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Comment, User
from app.repositories.comment_repository import comment_repository
from app.schemas.comment_schema import CommentCreate, CommentUpdate, CommentPublic
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.base_service import BaseService


class CommentService(BaseService[Comment, CommentCreate, CommentUpdate, CommentPublic]):
    def __init__(self):
        super().__init__(repository=comment_repository, public_schema=CommentPublic)

    async def create_comment(
        self,
        session: AsyncSession,
        comment_in: CommentCreate,
        post_id: UUID,
        author_id: UUID,
    ) -> Comment:
        comment = await comment_repository.create_comment(
            session, comment_in, post_id, author_id
        )
        return comment

    async def get_by_post(
        self,
        session: AsyncSession,
        post_id: UUID,
        params: PaginationParams,
        current_user: User,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> PaginatedResponse[CommentPublic]:
        if (only_deleted or include_deleted) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deleted items",
            )

        skip = (params.page - 1) * params.page_size
        comments = await comment_repository.get_by_post(
            session,
            post_id=post_id,
            skip=skip,
            limit=params.page_size,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )
        total = await comment_repository.count_by_post(
            session,
            post_id=post_id,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )

        return PaginatedResponse.create(
            items=[CommentPublic.model_validate(comment) for comment in comments],
            total_items=total,
            params=params,
        )


comment_service = CommentService()
