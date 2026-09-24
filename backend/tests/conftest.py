"""Test fixtures.

Session scope: drop/recreate the test database, then run Alembic to head.
Function scope: each test runs inside an outer transaction that is rolled back
afterwards, so tests never see each other's writes. The app's own commits land
on a savepoint (``join_transaction_mode="create_savepoint"``) and are undone
with that rollback.
"""

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.db import get_session
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DATABASE_URL = get_settings().effective_test_database_url


async def _recreate_test_database() -> None:
    """Drop and recreate the test database from the maintenance connection."""
    url = make_url(TEST_DATABASE_URL)
    database = url.database
    assert database, "TEST_DATABASE_URL must name a database"

    admin = await asyncpg.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database="postgres",
    )
    try:
        await admin.execute(f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')
        await admin.execute(f'CREATE DATABASE "{database}"')
    finally:
        await admin.close()


def _run_migrations() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.attributes["sqlalchemy_url"] = TEST_DATABASE_URL
    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    # Deliberately a sync fixture: Alembic's async env.py calls asyncio.run(),
    # which would fail inside a running test event loop.
    asyncio.run(_recreate_test_database())
    _run_migrations()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = lambda: db_session
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
            yield http_client
    finally:
        app.dependency_overrides.pop(get_session, None)
