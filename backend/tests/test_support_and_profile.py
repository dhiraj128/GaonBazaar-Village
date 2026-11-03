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

@pytest.mark.asyncio
async def test_profile_avatar_and_village_details():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ts = int(time.time() * 100) % 100000000
        phone = f"96{ts:08d}"
        headers = await issue_and_verify_test_token(client, phone, "customer")

        # 1. Update village and panchayat
        patch_res = await client.patch("/api/v1/auth/me", headers=headers, json={
            "name": "Radha Devi",
            "primary_village": "Benaghara",
            "primary_panchayat": "Minapur North"
        })
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["primary_village"] == "Benaghara"
        assert data["primary_panchayat"] == "Minapur North"

        # 2. Upload avatar
        avatar_payload = {"avatar_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
        av_res = await client.post("/api/v1/auth/avatar", headers=headers, json=avatar_payload)
        assert av_res.status_code == 200
        assert av_res.json()["avatar_url"] == avatar_payload["avatar_data"]

        # 3. Verify /me returns saved fields
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["primary_village"] == "Benaghara"
        assert me_res.json()["avatar_url"] == avatar_payload["avatar_data"]

@pytest.mark.asyncio
async def test_order_scoped_chat_and_location_sharing():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create customer and place an order
        cust_headers = await issue_and_verify_test_token(client, "9800000000", "customer")
        stores_res = await client.get("/api/v1/stores/nearby?latitude=26.2230&longitude=85.3520", headers=cust_headers)
        assert stores_res.status_code == 200
        store = stores_res.json()[0]
        store_id = store["id"]

        products_res = await client.get(f"/api/v1/stores/{store_id}/products", headers=cust_headers)
        product_id = products_res.json()[0]["id"]

        addr_res = await client.post("/api/v1/addresses", headers=cust_headers, json={
            "title": "Home",
            "recipient_name": "Ramesh Singh",
            "phone": "9800000000",
            "latitude": 26.2210,
            "longitude": 85.3500,
            "village": "Chaturshi",
            "landmark": "Near Shiv Mandir"
        })
        addr_id = addr_res.json()["id"]

        order_res = await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": store_id,
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order_id = order_res.json()["id"]

        # 1. Customer sends text message
        cust_msg = await client.post(f"/api/v1/orders/{order_id}/messages", headers=cust_headers, json={
            "message_type": "TEXT",
            "content": "कृपया शिव मंदिर के पास आकर कॉल करें (Call near temple)"
        })
        assert cust_msg.status_code == 201
        assert cust_msg.json()["sender_role"] == "customer"
        assert cust_msg.json()["content"] == "कृपया शिव मंदिर के पास आकर कॉल करें (Call near temple)"

        # 2. Customer attaches GPS Location Pin
        pin_msg = await client.post(f"/api/v1/orders/{order_id}/messages", headers=cust_headers, json={
            "message_type": "LOCATION_PIN",
            "latitude": 26.2215,
            "longitude": 85.3505,
            "location_title": "Shiv Mandir Main Gate"
        })
        assert pin_msg.status_code == 201
        assert pin_msg.json()["message_type"] == "LOCATION_PIN"
        assert pin_msg.json()["latitude"] == 26.2215

        # 3. Runner logs in and reads messages
        runner_headers = await issue_and_verify_test_token(client, "9800000003", "runner")
        list_msgs = await client.get(f"/api/v1/orders/{order_id}/messages", headers=runner_headers)
        assert list_msgs.status_code == 200
        msgs = list_msgs.json()
        assert len(msgs) >= 2
        assert any(m["message_type"] == "LOCATION_PIN" for m in msgs)

        # 4. Runner replies
        runner_reply = await client.post(f"/api/v1/orders/{order_id}/messages", headers=runner_headers, json={
            "message_type": "TEXT",
            "content": "हाँ, मैं 5 मिनट में पहुँच रहा हूँ (Arriving in 5 mins)"
        })
        assert runner_reply.status_code == 201
        assert runner_reply.json()["sender_role"] == "runner"
