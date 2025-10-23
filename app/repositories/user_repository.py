from typing import Any

from pydantic import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.security import get_password_hash, verify_password
from app.models.user_model import User, UserCreate, UserUpdate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self) -> None:
        super().__init__(User)

    async def create(self, session: AsyncSession, obj_in: UserCreate) -> User:
        db_obj = User.model_validate(
            obj_in, update={"hashed_password": get_password_hash(obj_in.password)}
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> Any:
        if isinstance(obj_in, dict):
            user_data = obj_in
        else:
            user_data = obj_in.model_dump(exclude_unset=True)
        if "password" in user_data and user_data["password"]:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            user_data["hashed_password"] = hashed_password
        return await super().update(session, db_obj=db_obj, obj_in=user_data)

    @staticmethod
    async def get_by_email(
        session: AsyncSession, email: EmailStr, include_deleted: bool = False
    ) -> User | None:
        statement = select(User).where(User.email == email)
        if not include_deleted:
            statement = statement.where(User.is_deleted == False)  # noqa: E712)
        result = await session.exec(statement)
        return result.first()

    async def authenticate(
        self, session: AsyncSession, email: EmailStr, password: str
    ) -> User | None:
        db_user = await self.get_by_email(
            session=session, email=email, include_deleted=True
        )
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user


user_repository = UserRepository()
