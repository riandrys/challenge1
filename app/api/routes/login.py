from datetime import timedelta
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.services.user_service import user_service
from app.schemas.auth import Token

router = APIRouter(tags=["login"])


@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await user_service.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")
