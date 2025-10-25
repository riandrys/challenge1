import uuid

from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.repositories.user_repository import user_repository
from app.models.user_model import User
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services.base_service import BaseService
from app.schemas.user_schema import UserCreate, UserUpdate, UserPublic


class UserService(BaseService[User, UserCreate, UserUpdate, UserPublic]):
    def __init__(self):
        super().__init__(user_repository, UserPublic)

    async def get_user_by_id(self, session: AsyncSession, user_id: uuid.UUID) -> User:
        return await self.get_by_id(session, entity_id=user_id)

    async def get_user_by_email(
        self, session: AsyncSession, email: EmailStr, include_deleted: bool = False
    ) -> User:
        user = await user_repository.get_by_email(
            session=session, email=email, include_deleted=include_deleted
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def create_user(self, session: AsyncSession, user_in: UserCreate) -> User:
        existing_user = await user_repository.get_by_email(
            session=session, email=user_in.email
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        return await user_repository.create(session, obj_in=user_in)

    async def update_user(
        self, session: AsyncSession, current_user: User, user_in: UserUpdate
    ) -> User:
        if user_in.email and user_in.email != current_user.email:
            existing_user = await user_repository.get_by_email(
                session, email=user_in.email
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        return await user_repository.update(
            session, db_obj=current_user, obj_in=user_in
        )

    async def delete_user(self, session: AsyncSession, user_id: uuid.UUID) -> bool:
        return await self.delete(session, entity_id=user_id)

    async def authenticate(
        self, session: AsyncSession, email: EmailStr, password: str
    ) -> User:
        user = await user_repository.authenticate(
            session, email=email, password=password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
            )
        return user

    async def get_users(
        self,
        session: AsyncSession,
        current_user: User,
        params: PaginationParams,
        include_deleted: bool = False,
        only_deleted: bool = False,
    ) -> PaginatedResponse[UserPublic]:
        return await self.get_list_paginated(
            session, current_user, params, include_deleted, only_deleted
        )

    async def restore_user(self, session: AsyncSession, user_id: uuid.UUID) -> User:
        return await self.restore(session, user_id)


user_service = UserService()
