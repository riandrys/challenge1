import uuid
from typing import Any, Generic, TypeVar
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        entity_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> ModelType | None:
        statement = select(self.model).where(self.model.id == entity_id)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)  # noqa: E712

        result = await session.exec(statement)
        return result.first()

    async def get_list(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ModelType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)  # noqa: E712

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def count(
        self,
        session: AsyncSession,
        include_deleted: bool = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)  # noqa: E712

        result = await session.exec(statement)
        return result.one()

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)  # type: ignore[attr-defined]
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def soft_delete(
        self,
        session: AsyncSession,
        entity_id: uuid.UUID,
    ) -> bool:
        db_obj = await self.get(session, entity_id=entity_id)
        if not db_obj:
            return False

        db_obj.soft_delete()
        session.add(db_obj)
        await session.commit()
        return True

    async def restore(
        self,
        session: AsyncSession,
        entity_id: uuid.UUID,
    ) -> ModelType | None:
        db_obj = await self.get(session, entity_id=entity_id, include_deleted=True)
        if not db_obj or not db_obj.is_deleted:
            return None

        db_obj.restore()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        entity_id: uuid.UUID,
    ) -> bool:
        db_obj = await self.get(session, entity_id=entity_id, include_deleted=True)
        if not db_obj:
            return False

        await session.delete(db_obj)
        await session.commit()
        return True
