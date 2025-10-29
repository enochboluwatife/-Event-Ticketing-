from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: An async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()