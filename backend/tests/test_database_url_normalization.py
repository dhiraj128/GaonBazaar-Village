import pytest
from httpx import AsyncClient, ASGITransport
from app.core.config import clean_and_normalize_database_url
from app.main import app

def test_supabase_direct_to_pooler_normalization():
    # Direct IPv6 Supabase host must be rewritten to AWS IPv4 pooler
    direct_url = "postgresql://postgres:mysecretpassword@db.vxewgvrjhjpntfvsmuez.supabase.co:5432/postgres"
    async_url = clean_and_normalize_database_url(direct_url, is_async=True)
    sync_url = clean_and_normalize_database_url(direct_url, is_async=False)
    
    assert "aws-0-ap-south-1.pooler.supabase.com" in async_url
    assert "postgres.vxewgvrjhjpntfvsmuez:mysecretpassword" in async_url
    assert async_url.startswith("postgresql+asyncpg://")
    assert sync_url.startswith("postgresql://")

def test_password_special_characters_encoded():
    # Passwords with special characters like # and @ must be properly percent-encoded
    raw_url = "postgresql://postgres:P@ss#word!99@db.vxewgvrjhjpntfvsmuez.supabase.co:5432/postgres"
    async_url = clean_and_normalize_database_url(raw_url, is_async=True)
    
    assert "P%40ss%23word%2199" in async_url
    assert "aws-0-ap-south-1.pooler.supabase.com:5432" in async_url

def test_pooler_url_preserves_custom_port_and_user_ref():
    # Pooler on port 6543
    pooler_url = "postgresql://postgres:Secret123@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    async_url = clean_and_normalize_database_url(pooler_url, is_async=True)
    
    assert "postgres.vxewgvrjhjpntfvsmuez:Secret123" in async_url
    assert ":6543" in async_url

def test_sqlite_urls_unaltered():
    sqlite_url = "sqlite:///./gaonbazaar.db"
    async_url = clean_and_normalize_database_url(sqlite_url, is_async=True)
    sync_url = clean_and_normalize_database_url(sqlite_url, is_async=False)
    
    assert async_url == "sqlite+aiosqlite:///./gaonbazaar.db"
    assert sync_url == "sqlite:///./gaonbazaar.db"

@pytest.mark.asyncio
async def test_health_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # /health must return 200 with service info
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "database" in data

        # /health/db must return connection info
        res_db = await client.get("/health/db")
        assert res_db.status_code == 200
        db_data = res_db.json()
        assert db_data["status"] in ["connected", "disconnected"]
