import uuid

from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.repositories.user_repository import user_repository
from app.models.user_model import User, UserCreate, UserUpdate, UserPublic
from app.schemas.common import PaginatedResponse


class UserService:
    async def get_user_by_id(self, session: AsyncSession, user_id: uuid.UUID) -> User:
        user = await user_repository.get(session, entity_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_user_by_email(
        self, session: AsyncSession, email: EmailStr, include_deleted: bool = False
    ) -> User | None:
        return await user_repository.get_by_email(
            session=session, email=email, include_deleted=include_deleted
        )

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
        deleted = await user_repository.soft_delete(session, entity_id=user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return deleted

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
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> PaginatedResponse[UserPublic]:
        users = await user_repository.get_list(
            session, skip=skip, limit=limit, include_deleted=include_deleted
        )
        total = await user_service.count_users(session, include_deleted=include_deleted)

        return PaginatedResponse.create(
            items=[UserPublic.model_validate(user) for user in users],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def count_users(
        self, session: AsyncSession, include_deleted: bool = False
    ) -> int:
        return await user_repository.count(session, include_deleted)


user_service = UserService()
