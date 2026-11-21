import pytest
import pytest_asyncio
from app.core.config import settings
from app.db.session import async_engine
from app.models.base import Base, OtpChallenge
from app.main import app
from app.api.v1.auth import OTP_STORAGE
from sqlalchemy import delete

@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    settings.TESTING = True
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(delete(OtpChallenge))
        
    async with app.router.lifespan_context(app):
        from tests.test_data_seeder import seed_test_database
        await seed_test_database()
        yield

    await async_engine.dispose()

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
