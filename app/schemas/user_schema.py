from typing import Annotated
from uuid import UUID
from datetime import datetime

from pydantic import EmailStr, AfterValidator
from sqlmodel import SQLModel, Field

from app.core.security import validate_password_strength

StrongPasswordStr = Annotated[
    str, Field(min_length=8, max_length=40), AfterValidator(validate_password_strength)
]


def validate_optional_password(v: str | None) -> str | None:
    if v is None:
        return None  # Permite que el valor sea nulo
    return validate_password_strength(v)


OptionalStrongPasswordStr = Annotated[
    str | None,
    Field(default=None, min_length=8, max_length=40),
    AfterValidator(validate_optional_password),
]


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: StrongPasswordStr


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: StrongPasswordStr
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: OptionalStrongPasswordStr


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: StrongPasswordStr


class UserPublic(UserBase):
    id: UUID
    created_at: datetime
    is_deleted: bool
