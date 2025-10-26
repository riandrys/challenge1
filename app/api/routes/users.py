from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from typing import Any

from fastapi.params import Depends

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.schemas.user_schema import (
    UserPublic,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)
from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=PaginatedResponse[UserPublic],
)
async def read_users(
    session: SessionDep,
    current_user: CurrentUser,
    params: PaginationParams = Depends(),  # type: ignore[assignment]
    include_deleted: bool = False,
    only_deleted: bool = False,
):
    return await user_service.get_users(
        session,
        current_user,
        params=params,
        include_deleted=include_deleted,
        only_deleted=only_deleted,
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(session: SessionDep, user_in: UserCreate) -> Any:
    user = await user_service.create_user(session, user_in)
    return user


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(
    session: SessionDep,
    user_in: UserRegister,
):
    user_create = UserCreate.model_validate(user_in)
    user = await user_service.create_user(session, user_create)
    return user


@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: CurrentUser,
):
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
):
    user_update = UserUpdate.model_validate(user_in)
    user = await user_service.update_user(session, current_user, user_update)

    return user


@router.delete("/me", response_model=MessageResponse)
async def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser,
) -> MessageResponse:
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    await user_service.delete_user(session, user_id=current_user.id)
    return MessageResponse(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: UUID,
):
    user = await user_service.get_user_by_id(session, user_id)
    if user == current_user:
        return UserPublic.model_validate(user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    session: SessionDep,
    user_id: UUID,
    user_in: UserUpdate,
):
    user_to_update = await user_service.get_user_by_id(session, user_id)
    user = await user_service.update_user(session, user_to_update, user_in)

    return user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=MessageResponse,
)
async def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: UUID
) -> MessageResponse:
    user = await user_service.get_user_by_id(session, user_id)
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    await user_service.delete_user(session, user_id)
    return MessageResponse(message="User deleted successfully")


@router.post(
    "/{user_id}/restore",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def restore_user(
    session: SessionDep,
    user_id: UUID,
):
    user = await user_service.restore_user(session, user_id)
    return user
