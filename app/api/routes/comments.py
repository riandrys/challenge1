# from fastapi import APIRouter, HTTPException, status
# from uuid import UUID
#
# from app.api.deps import CurrentUser, SessionDep
# from app.core.permissions import permission_checker
# from app.crud.comment import comment as comment_crud
# from app.crud.post import post as post_crud
# from app.models.comment_model import CommentCreate, CommentRead, CommentUpdate
# from app.schemas.common import PaginatedResponse, PaginationParams, MessageResponse
#
# router = APIRouter()
#
#
# @router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
# async def create_comment(
#     session: SessionDep,
#     current_user: CurrentUser,
#     comment_in: CommentCreate,
# ) -> CommentRead:
#     post = await post_crud.get(session, id=comment_in.post_id)
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Post not found",
#         )
#
#     comment = await comment_crud.create_with_author(
#         session,
#         obj_in=comment_in,
#         author_id=current_user.id,
#     )
#     return CommentRead.model_validate(comment)
#
#
# @router.get("/post/{post_id}", response_model=PaginatedResponse[CommentRead])
# async def read_comments_by_post(
#     session: SessionDep,
#     post_id: UUID,
#     params: PaginationParams = PaginationParams(),
# ) -> PaginatedResponse[CommentRead]:
#     comments = await comment_crud.get_by_post(
#         session,
#         post_id=post_id,
#         skip=params.skip,
#         limit=params.limit,
#     )
#
#     return PaginatedResponse.create(
#         items=[CommentRead.model_validate(comment) for comment in comments],
#         total=len(comments),
#         skip=params.skip,
#         limit=params.limit,
#     )
#
#
# @router.get("/{comment_id}", response_model=CommentRead)
# async def read_comment(
#     session: SessionDep,
#     comment_id: UUID,
# ) -> CommentRead:
#     comment = await comment_crud.get(session, id=comment_id)
#     if not comment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )
#     return CommentRead.model_validate(comment)
#
#
# @router.put("/{comment_id}", response_model=CommentRead)
# async def update_comment(
#     session: SessionDep,
#     current_user: CurrentUser,
#     comment_id: UUID,
#     comment_in: CommentUpdate,
# ) -> CommentRead:
#     comment = await comment_crud.get(session, id=comment_id)
#     if not comment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )
#
#     permission_checker.require_owner_or_superuser(current_user, comment)
#
#     comment = await comment_crud.update(session, db_obj=comment, obj_in=comment_in)
#     return CommentRead.model_validate(comment)
#
#
# @router.delete("/{comment_id}", response_model=MessageResponse)
# async def delete_comment(
#     session: SessionDep,
#     current_user: CurrentUser,
#     comment_id: UUID,
# ) -> MessageResponse:
#     comment = await comment_crud.get(session, id=comment_id)
#     if not comment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )
#
#     permission_checker.require_owner_or_superuser(current_user, comment)
#
#     await comment_crud.soft_delete(session, id=comment_id)
#     return MessageResponse(message="Comment deleted successfully")
