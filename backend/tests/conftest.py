import pytest
import pytest_asyncio
from app.core.config import settings
from app.db.session import async_engine
from app.models.base import Base
from app.main import app
from app.api.v1.auth import OTP_STORAGE

@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    settings.TESTING = True
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with app.router.lifespan_context(app):
        yield

@pytest.fixture
def admin_headers():
    return {"X-Admin-Key": settings.ADMIN_API_KEY}

async def issue_and_verify_test_token(client, phone: str, role: str = "customer", name: str = None) -> dict:
    """Helper for tests to issue real OTP challenge and verify cleanly without bypass."""
    await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": role})
    otp = OTP_STORAGE[phone]["otp"]
    data = {"phone": phone, "otp": otp, "role": role}
    if name:
        data["name"] = name
    res = await client.post("/api/v1/auth/otp/verify", json=data)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
