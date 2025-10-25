import uuid

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel
from app.models.user_model import User
from app.models.post_model import Post
from app.schemas.comment_schema import CommentBase


class Comment(BaseModel, CommentBase, table=True):
    post_id: uuid.UUID = Field(
        foreign_key="post.id", nullable=False, ondelete="CASCADE"
    )
    author_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    post: Post = Relationship(
        back_populates="comments", sa_relationship_kwargs={"lazy": "selectin"}
    )
    author: User = Relationship(
        back_populates="comments", sa_relationship_kwargs={"lazy": "selectin"}
    )
