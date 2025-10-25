from typing import List
from sqlmodel import Relationship

from app.models.base_model import BaseModel
from app.schemas.user_schema import UserBase


# Database model, database table inferred from class name
class User(BaseModel, UserBase, table=True):
    hashed_password: str
    posts: List["Post"] = Relationship(back_populates="author", cascade_delete=True)  # type: ignore # noqa: F821
    comments: List["Comment"] = Relationship(  # type: ignore # noqa: F821
        back_populates="author", cascade_delete=True
    )
