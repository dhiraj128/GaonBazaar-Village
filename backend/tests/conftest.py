import pytest_asyncio
from app.db.session import async_engine
from app.models.base import Base
from app.main import app

@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with app.router.lifespan_context(app):
        yield
