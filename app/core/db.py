from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.models import Base
from app.core.config import get_settings
from typing import Any, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(
    get_settings().DATABASE_URL,
    echo=False,
    future=True,
)

async_session: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Provides a context manager for asynchronous database sessions.

    This function yields an `AsyncSession` instance for use in database operations.
    The session is automatically closed after the operation.

    Returns:
        AsyncGenerator[AsyncSession, Any]: An asynchronous session generator.
    """
    logger.debug("🔌 Creating new database session.")
    async with async_session() as session:
        try:
            yield session
        finally:
            logger.debug("🔒 Database session closed.")


async def init_db():
    """
    Initializes the database by creating all tables defined in the ORM models.

    This function synchronously creates the database schema using the `Base.metadata.create_all`
    method. It could be extended to include logic for database migrations (e.g., using Alembic)
    if necessary.

    Note:
        This is a simple initialization; more complex migration strategies can be implemented
        for production scenarios.
    """
    logger.info("🛠️ Initializing database and creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database schema initialized.")


# Posibility to implement sophisticated way for migration logic, e.g., Alembic
