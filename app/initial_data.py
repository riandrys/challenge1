import asyncio
import logging

from app.core.db import init_db, async_session_maker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    async with async_session_maker() as session:
        await init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    asyncio.get_event_loop().run_until_complete(init())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
