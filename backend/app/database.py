"""
Database configuration và connection management
PostgreSQL với SQLAlchemy async
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.config import settings


class Base(DeclarativeBase):
    """
    Base class cho tất cả database models
    """
    pass


# Tạo async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Tạo async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Event listeners
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set database connection parameters
    """
    if "postgresql" in settings.DATABASE_URL:
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET timezone TO 'UTC'")


async def get_db() -> AsyncSession:
    """
    Dependency để lấy database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()