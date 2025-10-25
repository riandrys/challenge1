from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from app.models.user_model import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.user_repository import user_repository

from app.core.config import settings
from app.schemas.user_schema import UserCreate

engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Max connections beyond pool_size
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db(session: AsyncSession) -> None:
    user = await session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    if not user.first():
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await user_repository.create(session=session, obj_in=user_in)
