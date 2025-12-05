"""
Database configuration and session management for YogaFlow.
Uses SQLAlchemy async for non-blocking database operations.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.core.logging_config import logger

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Provides async context manager for database operations.
    Ensures proper cleanup even if exceptions occur.

    Yields:
        AsyncSession: SQLAlchemy async database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_database_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as error:
            await session.rollback()
            logger.error("Database session error", error=str(error), exc_info=True)
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    Should be called on application startup.

    Note:
        In production, use Alembic migrations instead of create_all.
        This is for development convenience only.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully")


async def close_database() -> None:
    """
    Close database connections.

    Should be called on application shutdown to ensure
    all connections are properly closed.
    """
    await engine.dispose()
    logger.info("Database connections closed")
