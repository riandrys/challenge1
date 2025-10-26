from fastapi import APIRouter

from app.api.routes import login, users, tags, posts, comments


api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(tags.router)
api_router.include_router(posts.router)
api_router.include_router(comments.router)
