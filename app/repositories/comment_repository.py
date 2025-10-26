from uuid import UUID

from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import Comment
from app.repositories.base_repository import BaseRepository
from app.schemas.comment_schema import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self):
        super().__init__(Comment)

    async def create_comment(
        self,
        session: AsyncSession,
        comment_in: CommentCreate,
        post_id: UUID,
        author_id: UUID,
    ) -> Comment:
        db_obj = Comment.model_validate(
            comment_in, update={"author_id": author_id, "post_id": post_id}
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_by_post(
        self,
        session: AsyncSession,
        post_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> list[Comment]:
        statement = select(Comment).where(Comment.post_id == post_id)
        filtered_statement = self._get_query_with_filter(
            statement, include_deleted=include_deleted, only_deleted=only_deleted
        )
        filtered_statement = filtered_statement.offset(skip).limit(limit)
        result = await session.exec(filtered_statement)
        return list(result.all())

    async def count_by_post(
        self,
        session: AsyncSession,
        post_id: UUID,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> int:
        statement = (
            select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        )
        filtered_statement = self._get_query_with_filter(
            statement, include_deleted=include_deleted, only_deleted=only_deleted
        )
        result = await session.exec(filtered_statement)
        return result.one()


comment_repository = CommentRepository()
