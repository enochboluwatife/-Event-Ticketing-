import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from geoalchemy2.elements import WKTElement

from app.database import Base
from app.main import app
from app.api.deps import get_db
from app.models import User, Event

# Test database URL - using 'db' as the hostname to connect to the database container
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/eventdb_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session.
    
    This fixture is used by pytest-asyncio to manage the event loop.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Drop and recreate all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session for testing
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "testpassword" hashed
        location=WKTElement('POINT(3.3792 6.5244)', srid=4326)  # Lagos, Nigeria
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_event(db_session: AsyncSession, sample_user: User) -> Event:
    """Create a sample event for testing."""
    event = Event(
        title="Test Concert",
        description="A test concert event",
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=3),
        total_tickets=100,
        tickets_sold=0,
        venue_address="Eko Hotel, Lagos",
        venue_location=WKTElement('POINT(3.4283 6.4281)', srid=4326)  # Victoria Island, Lagos
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)
    return event