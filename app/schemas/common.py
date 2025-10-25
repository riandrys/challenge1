from math import ceil
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(Query(default=1, ge=1, description="Current page number"))
    page_size: int = Field(
        Query(default=100, ge=1, le=100, description="Number of items per page")
    )


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(description="Current page number", examples=[1])
    page_size: int = Field(description="Number of items per page", examples=[10])

    total_pages: int = Field(description="Total pages", examples=[5])
    total_items: int = Field(description="Total items", examples=[48])

    @classmethod
    def create(
        cls, items: list[T], total_items: int, params: PaginationParams
    ) -> "PaginatedResponse[T]":
        total_pages = ceil(total_items / params.page_size) if total_items else 0
        return cls(
            items=items,
            total_items=total_items,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )


class MessageResponse(BaseModel):
    message: str
