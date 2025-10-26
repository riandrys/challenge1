from uuid import UUID
from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User
from app.models.base_model import BaseModel
from app.repositories.base_repository import BaseRepository
from app.schemas.common import PaginatedResponse, PaginationParams

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
PublicSchemaType = TypeVar("PublicSchemaType")


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, PublicSchemaType]
):
    def __init__(
        self,
        repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType],
        public_schema: type[PublicSchemaType],
    ):
        self.repository = repository
        self.public_schema = public_schema

    async def get_list_paginated(
        self,
        session: AsyncSession,
        current_user: User,
        params: PaginationParams,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> PaginatedResponse[PublicSchemaType]:
        if (only_deleted or include_deleted) and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deleted items",
            )
        skip = (params.page - 1) * params.page_size
        items = await self.repository.get_list(
            session,
            skip=skip,
            limit=params.page_size,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )
        total = await self.repository.count(
            session, include_deleted=include_deleted, only_deleted=only_deleted
        )
        return PaginatedResponse.create(
            items=[self.public_schema.model_validate(item) for item in items],  # type: ignore[attr-defined]
            total_items=total,
            params=params,
        )

    async def get_by_id(
        self,
        session: AsyncSession,
        entity_id: UUID,
        current_user: User | None = None,
        include_deleted: bool = False,
    ) -> ModelType:
        if include_deleted and current_user and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deleted items",
            )
        item = await self.repository.get(
            session, entity_id=entity_id, include_deleted=include_deleted
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repository.model.__name__} not found",
            )
        return item

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        return await self.repository.create(session, obj_in=obj_in)

    async def update(
        self,
        session: AsyncSession,
        entity_id: UUID,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        db_obj = await self.repository.get(session, entity_id=entity_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repository.model.__name__} not found",
            )

        return await self.repository.update(session, db_obj=db_obj, obj_in=obj_in)

    async def delete(
        self,
        session: AsyncSession,
        entity_id: UUID,
    ) -> bool:
        deleted = await self.repository.soft_delete(session, entity_id=entity_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repository.model.__name__} not found",
            )
        return deleted

    async def restore(
        self,
        session: AsyncSession,
        entity_id: UUID,
    ) -> ModelType:
        item = await self.repository.restore(session, entity_id=entity_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repository.model.__name__} not found",
            )
        return item

    async def count(
        self,
        session: AsyncSession,
        include_deleted: bool = False,
    ) -> int:
        return await self.repository.count(session, include_deleted=include_deleted)
