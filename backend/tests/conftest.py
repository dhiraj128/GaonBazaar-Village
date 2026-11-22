import pytest
import pytest_asyncio
from app.core.config import settings
from app.db.session import async_engine
from app.models.base import Base, OtpChallenge
from app.main import app
from app.api.v1.auth import OTP_STORAGE
from sqlalchemy import delete

# Secure test-only credentials (distinct from default dev and never used in production)
TEST_ADMIN_API_KEY = "test-sec-admin-key-9999-secure-auth-token"
TEST_SECRET_KEY = "test-sec-jwt-signing-key-9999-secure-auth-token"

settings.TESTING = True
settings.ENVIRONMENT = "test"
settings.ADMIN_API_KEY = TEST_ADMIN_API_KEY
settings.SECRET_KEY = TEST_SECRET_KEY

@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    settings.TESTING = True
    settings.ENVIRONMENT = "test"
    settings.ADMIN_API_KEY = TEST_ADMIN_API_KEY
    settings.SECRET_KEY = TEST_SECRET_KEY
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
    """Helper for tests to authenticate test accounts cleanly without bypass."""
    if role in ["admin", "super_admin", "hub_manager"]:
        res = await client.post("/api/v1/admin/auth/login", json={"phone": phone, "secret_key": settings.ADMIN_API_KEY})
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": role})
    otp = OTP_STORAGE[phone]["otp"]
    data = {"phone": phone, "otp": otp, "role": role}
    if name:
        data["name"] = name
    res = await client.post("/api/v1/auth/otp/verify", json=data)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

