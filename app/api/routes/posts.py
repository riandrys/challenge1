from fastapi import APIRouter, status, Depends
from uuid import UUID

from app.api.deps import CurrentUser, SessionDep
from app.services.post_service import post_service
from app.schemas.post_schema import (
    PostCreate,
    PostPublic,
    PostUpdate,
    PostPublicWithRelations,
    PostReadWithAuthor,
)
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/", response_model=PostPublicWithRelations, status_code=status.HTTP_201_CREATED
)
async def create_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_in: PostCreate,
):
    post = await post_service.create_post(
        session,
        post_in=post_in,
        author_id=current_user.id,
    )
    return post


@router.get("/", response_model=PaginatedResponse[PostPublic])
async def read_posts(
    session: SessionDep,
    current_user: CurrentUser,
    params: PaginationParams = Depends(),
    include_deleted: bool = False,
    only_deleted: bool = False,
):
    posts = await post_service.get_list_paginated(
        session, current_user, params, include_deleted, only_deleted
    )

    return posts


@router.get("/{post_id}", response_model=PostPublicWithRelations)
async def read_post(
    session: SessionDep,
    post_id: UUID,
):
    post = await post_service.get_by_id(session, post_id)

    return post


@router.put("/{post_id}", response_model=PostPublicWithRelations)
async def update_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: UUID,
    post_in: PostUpdate,
):
    post = await post_service.update_post(
        session, current_user=current_user, post_id=post_id, post_in=post_in
    )
    return post


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: UUID,
):
    await post_service.delete_post(session, post_id, current_user)
    return MessageResponse(message="Post deleted successfully")


@router.get("/author/{author_id}", response_model=PaginatedResponse[PostReadWithAuthor])
async def read_posts_by_author(
    session: SessionDep,
    current_user: CurrentUser,
    author_id: UUID,
    params: PaginationParams = Depends(),
    include_deleted: bool = False,
    only_deleted: bool = False,
):
    posts = await post_service.get_posts_by_author(
        session, current_user, author_id, params, include_deleted, only_deleted
    )
    return posts
