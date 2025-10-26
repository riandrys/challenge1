from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tag_model import Tag, PostTagLink
from app.repositories.base_repository import BaseRepository
from app.schemas.tag_schema import TagCreate, TagUpdate


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    def __init__(self):
        super().__init__(Tag)

    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Tag]:
        statement = select(self.model).where(self.model.name == name)
        result = await session.exec(statement)
        return result.first()

    async def count_posts_by_tag(self, session: AsyncSession, tag_id: UUID) -> int:
        statement = select(func.count(PostTagLink.post_id)).where(  # type: ignore [arg-type]
            PostTagLink.tag_id == tag_id
        )
        result = await session.exec(statement)
        return result.one()


tag_repository = TagRepository()
