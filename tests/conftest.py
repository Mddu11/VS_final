import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient 
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import AsyncMock, patch

from app.main import app
from app.dependencies import get_db, get_current_admin, get_current_user
from app.models import Base, User, RoleEnum

# Используем SQLite в памяти для максимальной скорости и изоляции
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Переопределение зависимостей ---
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

async def override_get_current_admin():
    return User(
        id=1, 
        username="admin_test",
        email="admin@test.com", 
        role=RoleEnum.admin
    )

async def override_get_current_user():
    return User(
        id=2, 
        username="player_test",
        email="player@test.com", 
        role=RoleEnum.player
    )

# Применяем переопределения
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_admin] = override_get_current_admin
app.dependency_overrides[get_current_user] = override_get_current_user

# --- Фикстуры БД и Клиента ---
@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# --- Фикстуры авторизации и заглушки ---
@pytest_asyncio.fixture
def admin_token_headers():
    return {"Authorization": "Bearer fake-admin-token"}

@pytest_asyncio.fixture(autouse=True)
def mock_redis():
    """
    Заглушка для Redis, чтобы тесты не требовали реальный сервер Redis.
    """
    with patch("redis.asyncio.from_url") as mock:
        mock_redis_client = AsyncMock()
        mock.return_value = mock_redis_client
        yield mock_redis_client