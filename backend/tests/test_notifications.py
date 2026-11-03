import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_notifications_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer logs in
        headers = await issue_and_verify_test_token(client, "9800000000", "customer")
        
        # 1. Fetch notifications
        res = await client.get("/api/v1/notifications", headers=headers)
        assert res.status_code == 200
        notifs = res.json()
        assert isinstance(notifs, list)
        
        # 2. Mark all as read
        mark_res = await client.post("/api/v1/notifications/mark-all-read", headers=headers)
        assert mark_res.status_code == 200
        assert mark_res.json()["success"] is True

        # 3. Verify notifications list reflect read status
        res2 = await client.get("/api/v1/notifications", headers=headers)
        assert res2.status_code == 200
        for n in res2.json():
            assert n["is_read"] is True
