from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User
from app.models.tag_model import Tag
from app.schemas.tag_schema import TagCreate, TagUpdate, TagPublic
from app.repositories.tag_repository import tag_repository
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.base_service import BaseService


class TagService(BaseService[Tag, TagCreate, TagUpdate, TagPublic]):
    def __init__(self):
        super().__init__(tag_repository, TagPublic)

    async def get_tag_by_id(self, session: AsyncSession, tag_id: UUID) -> Tag:
        return await self.get_by_id(session, tag_id)

    async def get_tags(
        self,
        session: AsyncSession,
        current_user: User,
        params: PaginationParams,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> PaginatedResponse[TagPublic]:
        return await self.get_list_paginated(
            session,
            current_user,
            params=params,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )

    async def create_tag(self, session: AsyncSession, tag_in: TagCreate) -> Tag:
        existing_tag = await tag_repository.get_by_name(session, tag_in.name)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tag with this name already exists",
            )
        return await self.create(session, tag_in)

    async def update_tag(
        self, session: AsyncSession, tag_id: UUID, tag_in: TagUpdate
    ) -> Tag:
        tag = await self.get_by_id(session, tag_id)
        if tag_in.name and tag_in.name != tag.name:
            existing_tag = await tag_repository.get_by_name(session, tag_in.name)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tag with this name already exists",
                )
        return await tag_repository.update(session, tag, tag_in)

    async def delete_tag(self, session: AsyncSession, tag_id: UUID) -> bool:
        # TODO check if tag is associated with any posts before deleting
        return await self.delete(session, tag_id)

    async def restore_tag(self, session: AsyncSession, tag_id: UUID) -> Tag:
        return await self.restore(session, tag_id)


tag_service = TagService()
