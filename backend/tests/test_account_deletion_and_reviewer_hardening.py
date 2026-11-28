import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_public_deletion_request_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Invalid phone
        resp = await ac.post("/api/v1/auth/public-deletion-request", json={
            "phone": "123",
            "role": "customer",
            "confirm": True
        })
        assert resp.status_code == 400

        # Valid phone
        resp2 = await ac.post("/api/v1/auth/public-deletion-request", json={
            "phone": "9800000010",
            "role": "customer",
            "reason": "Moving out of pilot village",
            "confirm": True
        })
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["status"] == "SUCCESS"
        assert "DEL-" in data["ticket_id"]
        assert "+91 98******10" in data["phone_masked"]

@pytest.mark.asyncio
async def test_admin_deletion_blocked():
    transport = ASGITransport(app=app)
    token = create_access_token(data={"sub": "admin_uuid_test", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Public deletion request for admin phone blocked
        resp_pub = await ac.post("/api/v1/auth/public-deletion-request", json={
            "phone": "9800000099",
            "role": "admin",
            "confirm": True
        })
        assert resp_pub.status_code == 403
