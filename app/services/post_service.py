from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.permissions import permission_checker
from app.repositories.post_repository import post_repository
from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.post_schema import PostCreate, PostUpdate, PostPublic
from app.models import User, Post
from app.services.base_service import BaseService


class PostService(BaseService[Post, PostCreate, PostUpdate, PostPublic]):
    def __init__(self):
        super().__init__(repository=post_repository, public_schema=PostPublic)

    async def create_post(
        self, session: AsyncSession, post_in: PostCreate, author_id: UUID
    ) -> Post:
        post = await post_repository.create_with_tags(
            session, obj_in=post_in, author_id=author_id
        )
        return post

    async def get_posts_by_author(
        self,
        session: AsyncSession,
        current_user: User,
        author_id: UUID,
        params: PaginationParams,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> PaginatedResponse[PostPublic]:
        if (only_deleted or include_deleted) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deleted items",
            )

        skip = (params.page - 1) * params.page_size
        posts = await post_repository.get_by_author(
            session,
            author_id=author_id,
            skip=skip,
            limit=params.page_size,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )
        total = await post_repository.count_by_author(
            session,
            author_id=author_id,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )

        return PaginatedResponse.create(
            items=[PostPublic.model_validate(post) for post in posts],
            total_items=total,
            params=params,
        )

    async def update_post(
        self,
        session: AsyncSession,
        current_user: User,
        post_id: UUID,
        post_in: PostUpdate,
    ) -> Post:
        post = await self.get_by_id(session, post_id)
        permission_checker.require_owner_or_superuser(current_user, post)

        updated = await post_repository.update_with_tags(
            session, db_obj=post, obj_in=post_in
        )
        return updated

    async def delete_post(
        self, session: AsyncSession, post_id: UUID, current_user: User
    ) -> bool:
        post = await self.get_by_id(session, post_id)

        permission_checker.require_owner_or_superuser(current_user, post)

        # TODO before delete the post i need delete the associated comments
        return await self.delete(session, post_id)


post_service = PostService()
