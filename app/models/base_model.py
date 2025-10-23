import uuid
from datetime import datetime, UTC

from sqlalchemy import func
from sqlmodel import SQLModel, Field
import sqlalchemy as sa


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class SoftDeleteMixin(SQLModel):
    is_deleted: bool = Field(default=False, nullable=False, index=True)
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(TimestampMixin, SoftDeleteMixin, SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
