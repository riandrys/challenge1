from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tag_model import Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.tag_schema import TagCreate, TagUpdate


class TagRepository(BaseRepository[Tag, TagCreate, TagUpdate]):
    def __init__(self):
        super().__init__(Tag)

    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Tag]:
        statement = select(self.model).where(self.model.name == name)
        result = await session.exec(statement)
        return result.first()


tag_repository = TagRepository()
