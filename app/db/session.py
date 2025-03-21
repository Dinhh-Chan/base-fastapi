# app/db/session.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Đảm bảo rằng URL có prefix là postgresql+asyncpg
db_url = settings.SQLALCHEMY_DATABASE_URI
if "sqlite" in db_url:
    # SQLite async
    engine = create_async_engine(
        db_url,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        pool_pre_ping=True,
        echo=settings.DB_ECHO_LOG,
    )
else:
    # PostgreSQL async
    engine = create_async_engine(
        db_url,
        pool_pre_ping=True,
        echo=settings.DB_ECHO_LOG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()