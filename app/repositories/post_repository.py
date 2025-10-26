from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlmodel import select, not_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Post, Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.post_schema import PostCreate, PostUpdate


class PostRepository(BaseRepository[Post, PostCreate, PostUpdate]):
    def __init__(self):
        super().__init__(Post)

    async def get_by_title(self, session: AsyncSession, title: str) -> Post | None:
        statement = select(self.model).where(self.model.title == title)
        filtered_statement = self._get_query_with_filter(statement)
        result = await session.exec(filtered_statement)
        return result.first()

    async def get_by_author(
        self,
        session: AsyncSession,
        author_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> list[Post]:
        statement = select(Post).where(Post.author_id == author_id)
        filtered_statement = self._get_query_with_filter(
            statement, include_deleted=include_deleted, only_deleted=only_deleted
        )
        filtered_statement = filtered_statement.offset(skip).limit(limit)
        result = await session.exec(filtered_statement)
        return list(result.all())

    async def count_by_author(
        self,
        session: AsyncSession,
        author_id: UUID,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(self.model)
            .where(Post.author_id == author_id)
        )
        filtered_statement = self._get_query_with_filter(
            statement, include_deleted=include_deleted, only_deleted=only_deleted
        )
        result = await session.exec(filtered_statement)
        return result.one()

    async def create_with_tags(
        self,
        session: AsyncSession,
        obj_in: PostCreate,
        author_id: UUID,
    ) -> Post:
        db_obj = Post.model_validate(obj_in, update={"author_id": author_id})

        if obj_in.tag_ids:
            statement = (
                select(Tag)
                .where(Tag.id.in_(obj_in.tag_ids))  # type: ignore[attr-defined]
                .where(not_(Tag.is_deleted))
            )
            result = await session.exec(statement)
            tags = list(result.all())
            db_obj.tags = tags

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_with_tags(
        self,
        session: AsyncSession,
        db_obj: Post,
        obj_in: PostUpdate | dict[str, Any],
    ) -> Post:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

        tag_ids = update_data.pop("tag_ids", None)

        db_obj.sqlmodel_update(update_data)

        if tag_ids is not None:
            statement = (
                select(Tag).where(Tag.id.in_(tag_ids)).where(not_(Tag.is_deleted))  # type: ignore[attr-defined]
            )
            result = await session.exec(statement)
            tags = list(result.all())
            db_obj.tags = tags

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


post_repository = PostRepository()
