import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_customer_profile_update_and_support_hub():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ts = int(time.time() * 100) % 100000000
        phone = f"97{ts:08d}"
        
        # 1. Register customer
        headers = await issue_and_verify_test_token(client, phone, "customer")
        
        # 2. Get profile
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["phone"] == phone
        
        # 3. Update profile with real name and email
        update_res = await client.patch("/api/v1/auth/me", headers=headers, json={
            "name": "Sita Kumari",
            "email": "sita.kumari@example.com",
            "preferred_language": "hi"
        })
        assert update_res.status_code == 200
        assert update_res.json()["name"] == "Sita Kumari"
        assert update_res.json()["email"] == "sita.kumari@example.com"
        
        # 4. Verify persistence
        me_check = await client.get("/api/v1/auth/me", headers=headers)
        assert me_check.status_code == 200
        assert me_check.json()["name"] == "Sita Kumari"
        assert me_check.json()["email"] == "sita.kumari@example.com"
        
        # 5. Create Support Ticket
        ticket_res = await client.post("/api/v1/support/tickets", headers=headers, json={
            "subject": "Missing Item in Delivery",
            "message": "1 packet salt was not received in order."
        })
        assert ticket_res.status_code == 201
        ticket = ticket_res.json()
        assert ticket["subject"] == "Missing Item in Delivery"
        assert ticket["status"] == "OPEN"
        
        # 6. List tickets
        my_tickets = await client.get("/api/v1/support/tickets", headers=headers)
        assert my_tickets.status_code == 200
        assert len(my_tickets.json()) >= 1
        
        # 7. AI Support Chat
        ai_chat = await client.post("/api/v1/support/ai-chat", headers=headers, json={
            "query": "कहाँ है मेरा ऑर्डर?",
            "preferred_language": "hi"
        })
        assert ai_chat.status_code == 200
        assert "reply" in ai_chat.json()
