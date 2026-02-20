"""Integration test fixtures - in-memory SQLite for fast tests."""

import asyncio
import os
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# Set test env before importing app modules
os.environ["SECRET_KEY"] = "test-secret-key-for-integration-tests-32ch"
os.environ["HMAC_SECRET_KEY"] = "test-hmac-secret-key-for-integration-32ch"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "minioadmin"
os.environ["MINIO_SECRET_KEY"] = "minioadmin"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
os.environ["ENVIRONMENT"] = "test"

from olimpqr.infrastructure.database.base import Base
from olimpqr.infrastructure.database import get_db
from olimpqr.main import app

# Import all models to register them with Base metadata
from olimpqr.infrastructure.database.models import (  # noqa: F401
    UserModel,
    ParticipantModel,
    CompetitionModel,
    RegistrationModel,
    EntryTokenModel,
    AttemptModel,
    ScanModel,
    AuditLogModel,
    InstitutionModel,
    RoomModel,
    SeatAssignmentModel,
    DocumentModel,
    ParticipantEventModel,
    AnswerSheetModel,
)
from olimpqr.infrastructure.security import create_access_token
from olimpqr.domain.value_objects import UserRole


# In-memory async SQLite engine for tests
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override DB dependency for tests."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the DB dependency
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create and drop tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create httpx AsyncClient for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a test DB session."""
    async with TestSessionLocal() as session:
        yield session


def make_auth_header(user_id=None, email="test@example.com", role=UserRole.ADMIN):
    """Create Authorization header with JWT token."""
    if user_id is None:
        user_id = uuid4()
    token = create_access_token(user_id=user_id, email=email, role=role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user in the test DB and return (user_model, auth_headers)."""
    from olimpqr.infrastructure.security import hash_password

    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email="admin@test.com",
        password_hash=hash_password("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    headers = make_auth_header(user_id=user_id, email="admin@test.com", role=UserRole.ADMIN)
    return user, headers


@pytest_asyncio.fixture
async def participant_user(db_session: AsyncSession):
    """Create a participant user + profile and return (user_model, participant_model, auth_headers)."""
    from olimpqr.infrastructure.security import hash_password

    user_id = uuid4()
    participant_id = uuid4()

    user = UserModel(
        id=user_id,
        email="participant@test.com",
        password_hash=hash_password("partpass123"),
        role=UserRole.PARTICIPANT,
        is_active=True,
    )
    db_session.add(user)

    participant = ParticipantModel(
        id=participant_id,
        user_id=user_id,
        full_name="Test Participant",
        school="Test School",
        grade=10,
    )
    db_session.add(participant)
    await db_session.commit()

    headers = make_auth_header(user_id=user_id, email="participant@test.com", role=UserRole.PARTICIPANT)
    return user, participant, headers


@pytest_asyncio.fixture
async def invigilator_user(db_session: AsyncSession):
    """Create an invigilator user and return (user_model, auth_headers)."""
    from olimpqr.infrastructure.security import hash_password

    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email="invigilator@test.com",
        password_hash=hash_password("invigilpass123"),
        role=UserRole.INVIGILATOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    headers = make_auth_header(user_id=user_id, email="invigilator@test.com", role=UserRole.INVIGILATOR)
    return user, headers


@pytest_asyncio.fixture
async def institution(db_session: AsyncSession):
    """Create a test institution."""
    inst_id = uuid4()
    inst = InstitutionModel(
        id=inst_id,
        name="Test Institution",
        short_name="TI",
        city="Test City",
    )
    db_session.add(inst)
    await db_session.commit()
    return inst
