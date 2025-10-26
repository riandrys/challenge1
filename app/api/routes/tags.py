from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_active_superuser,
    SessionDep,
    get_current_user,
    CurrentUser,
)
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
from app.schemas.tag_schema import TagCreate, TagUpdate, TagPublic
from app.services.tag_service import tag_service


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "/",
    response_model=PaginatedResponse[TagPublic],
    summary="Retrieve all tags",
    description="Retrieve all tags with pagination. Any user can access this.",
    dependencies=[Depends(get_current_user)],
)
async def read_tags(
    session: SessionDep,
    current_user: CurrentUser,
    params: PaginationParams = Depends(),
    include_deleted: bool = False,
    only_deleted: bool = False,
):
    return await tag_service.get_tags(
        session, current_user, params, include_deleted, only_deleted
    )


@router.post(
    "/",
    response_model=TagPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
    description="Create a new tag. Only superusers can create tags.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_tag(
    session: SessionDep,
    tag_in: TagCreate,
):
    return await tag_service.create_tag(session, tag_in)


@router.get(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Retrieve a tag by ID",
    description="Retrieve a tag by its ID. Any user can access this.",
    dependencies=[Depends(get_current_user)],
)
async def read_tag_by_id(
    session: SessionDep,
    tag_id: UUID,
):
    return await tag_service.get_tag_by_id(session, tag_id)


@router.put(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Update a tag by ID",
    description="Update an existing tag by its ID. Only superusers can update tags.",
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_tag(
    session: SessionDep,
    tag_id: UUID,
    tag_in: TagUpdate,
):
    return await tag_service.update_tag(session, tag_id, tag_in)


@router.delete(
    "/{tag_id}",
    summary="Delete a tag by ID",
    description="Delete an existing tag by its ID. Only superusers can delete tags.",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=MessageResponse,
)
async def delete_tag(
    session: SessionDep,
    tag_id: UUID,
):
    await tag_service.delete_tag(session, tag_id)
    return MessageResponse(message="Tag deleted successfully")


@router.post(
    "/{tag_id}/restore",
    summary="Restore a tag by ID",
    description="Restore a deleted tag by its ID. Only superusers can delete tags.",
    response_model=TagPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
async def restore(
    session: SessionDep,
    tag_id: UUID,
):
    return await tag_service.restore_tag(session, tag_id)
