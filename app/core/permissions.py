from typing import Protocol
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user_model import User


class OwnableResource(Protocol):
    author_id: UUID


class PermissionChecker:

    @staticmethod
    def is_owner(user: User, resource: OwnableResource) -> bool:
        return user.id == resource.author_id

    @staticmethod
    def is_superuser(user: User) -> bool:
        return user.is_superuser

    @staticmethod
    def can_modify(user: User, resource: OwnableResource) -> bool:
        return PermissionChecker.is_superuser(user) or PermissionChecker.is_owner(user, resource)

    @staticmethod
    def can_delete(user: User, resource: OwnableResource) -> bool:
        return PermissionChecker.is_superuser(user) or PermissionChecker.is_owner(user, resource)

    @staticmethod
    def can_view_deleted(user: User) -> bool:
        return PermissionChecker.is_superuser(user)

    @staticmethod
    def require_owner_or_superuser(user: User, resource: OwnableResource) -> None:
        if not PermissionChecker.can_modify(user, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to perform this action"
            )

    @staticmethod
    def require_superuser(user: User) -> None:
        if not PermissionChecker.is_superuser(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superuser privileges required"
            )


permission_checker = PermissionChecker()