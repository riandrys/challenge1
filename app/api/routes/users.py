import uuid

from fastapi import APIRouter, HTTPException, status
from typing import Any

from fastapi.params import Depends

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models.user_model import (
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
    "",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=PaginatedResponse[UserPublic],
)
async def read_users(
    session: SessionDep,
    params: PaginationParams = Depends(),  # type: ignore[assignment]
    show_deleted_users: bool = False,
) -> PaginatedResponse[UserPublic]:
    return await user_service.get_users(
        session,
        skip=params.skip,
        limit=params.limit,
        include_deleted=show_deleted_users,
    )


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(session: SessionDep, user_in: UserCreate) -> Any:
    user = await user_service.create_user(session, user_in)
    return user


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(
    session: SessionDep,
    user_in: UserRegister,
) -> UserPublic:
    user_create = UserCreate.model_validate(user_in)
    user = await user_service.create_user(session, user_create)
    return UserPublic.model_validate(user)


@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: CurrentUser,
) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.put("/me", response_model=UserPublic)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
) -> UserPublic:
    user_update = UserUpdate.model_validate(user_in)
    user = await user_service.update_user(session, current_user, user_update)

    return UserPublic.model_validate(user)


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
    user_id: uuid.UUID,
) -> UserPublic:
    user = await user_service.get_user_by_id(session, user_id)
    if user == current_user:
        return UserPublic.model_validate(user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return UserPublic.model_validate(user)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    user_to_update = await user_service.get_user_by_id(session, user_id)
    user = await user_service.update_user(session, user_to_update, user_in)

    return UserPublic.model_validate(user)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=MessageResponse,
)
async def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> MessageResponse:
    user = await user_service.get_user_by_id(session, user_id)
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    await user_service.delete_user(session, user_id)
    return MessageResponse(message="User deleted successfully")
