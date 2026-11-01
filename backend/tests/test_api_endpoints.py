import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_and_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform_fee"] == 3.0
        assert data["max_delivery_radius_km"] == 8.0

@pytest.mark.asyncio
async def test_otp_send_and_verify_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Send OTP
        send_resp = await client.post("/api/v1/auth/otp/send", json={
            "phone": "9876543210",
            "role": "customer"
        })
        assert send_resp.status_code == 200
        s_data = send_resp.json()
        assert "session_id" in s_data
        
        # 2. Verify OTP
        verify_resp = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9876543210",
            "otp": "123456"
        })
        assert verify_resp.status_code == 200
        v_data = verify_resp.json()
        assert "access_token" in v_data
        assert v_data["user"]["phone"] == "9876543210"

@pytest.mark.asyncio
async def test_nearby_stores_and_two_featured_rule():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/stores/nearby?latitude=26.2230&longitude=85.3520&radius_km=8.0")
        assert resp.status_code == 200
        stores = resp.json()
        assert len(stores) >= 2
        # Exactly two featured stores rule
        featured_count = len([s for s in stores if s["is_featured"] is True])
        assert featured_count == 2
