import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_active_superuser, SessionDep
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
from app.schemas.tag_schema import TagCreate, TagUpdate, TagPublic
from app.services.tag_service import tag_service


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get(
    "/",
    response_model=PaginatedResponse[TagPublic],
    summary="Retrieve all tags",
    description="Retrieve all tags with pagination. Any user can access this.",
)
async def read_tags(
    session: SessionDep,
    params: PaginationParams = Depends(),
    show_deleted_tags: bool = False,
):
    return await tag_service.get_tags(session, params, show_deleted_tags)


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
)
async def read_tag_by_id(
    session: SessionDep,
    tag_id: uuid.UUID,
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
    tag_id: uuid.UUID,
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
    tag_id: uuid.UUID,
):
    await tag_service.delete_tag(session, tag_id)
    return MessageResponse(message="Tag deleted successfully")


@router.patch(
    "/{tag_id}",
    summary="Delete a tag by ID",
    description="Delete an existing tag by its ID. Only superusers can delete tags.",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TagPublic,
)
async def restore_tag(
    session: SessionDep,
    tag_id: uuid.UUID,
):
    return tag_service.restore_tag(session, tag_id)
