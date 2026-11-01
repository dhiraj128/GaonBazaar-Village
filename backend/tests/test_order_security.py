from datetime import datetime, timedelta, timezone
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select
from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.base import Order

@pytest.mark.asyncio
async def test_eight_km_radius_enforcement_on_order_creation():
    """Verify that orders exceeding the 8.0 km service radius are rejected by backend."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Auth customer
        c_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9811122233", "otp": "123456", "role": "customer"})
        c_token = c_auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {c_token}"}

        # Address 15 km away from Minapur center (e.g., latitude 26.0500, longitude 85.3400)
        far_addr = await client.post("/api/v1/addresses", headers=headers, json={
            "title": "Out of Range Farm",
            "recipient_name": "Far Away Customer",
            "phone": "9811122233",
            "latitude": 26.0500,
            "longitude": 85.3400,
            "village": "Far Locality"
        })
        far_addr_id = far_addr.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_id = stores[0]["id"]
        prod_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod_id = prod_res.json()[0]["id"]

        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": store_id,
            "delivery_address_id": far_addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 400
        assert "Maximum allowed delivery radius is 8.0 km" in order_res.json()["detail"]

@pytest.mark.asyncio
async def test_price_manipulation_protection():
    """Verify that backend calculates prices exclusively from DB products and ignores client inputs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        c_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9822233344", "otp": "123456", "role": "customer"})
        c_token = c_auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {c_token}"}

        # Valid nearby address
        addr_res = await client.post("/api/v1/addresses", headers=headers, json={
            "title": "Home",
            "recipient_name": "Price Check Customer",
            "phone": "9822233344",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi"
        })
        addr_id = addr_res.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_id = stores[0]["id"]
        prod_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod = prod_res.json()[0]
        actual_price = prod["price"]

        # Attempt to order 2 units
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": store_id,
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod["id"], "quantity": 2, "unit_price": 0.01}] # Attempt client injection
        })
        assert order_res.status_code == 201
        order_data = order_res.json()
        expected_subtotal = actual_price * 2
        assert order_data["subtotal"] == expected_subtotal
        assert order_data["platform_fee"] == 3.0 # Invariant ₹3.00

@pytest.mark.asyncio
async def test_order_cancellation_enforces_180s_window():
    """Verify customer can cancel within 180 seconds, but cancellation fails once deadline passes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        c_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9833344455", "otp": "123456", "role": "customer"})
        c_token = c_auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {c_token}"}

        addr_res = await client.post("/api/v1/addresses", headers=headers, json={
            "title": "Home",
            "recipient_name": "Cancel Test",
            "phone": "9833344455",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi"
        })
        addr_id = addr_res.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_id = stores[0]["id"]
        prod_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod_id = prod_res.json()[0]["id"]

        # 1. Place Order
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": store_id,
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order_id = order_res.json()["id"]

        # 2. Simulate expired cancel deadline in database
        async with AsyncSessionLocal() as session:
            o_res = await session.execute(select(Order).where(Order.id == order_id))
            db_order = o_res.scalars().first()
            # Set cancel_until to 10 seconds in the past
            db_order.cancel_until = datetime.now(timezone.utc) - timedelta(seconds=10)
            await session.commit()

        # 3. Attempt to cancel -> must return 400 with timeout message
        cancel_res = await client.post(f"/api/v1/orders/{order_id}/cancel", headers=headers)
        assert cancel_res.status_code == 400
        assert "रद्द करने की 180 सेकंड की समय सीमा समाप्त हो चुकी है" in cancel_res.json()["detail"]

@pytest.mark.asyncio
async def test_delivery_otp_verification_security():
    """Verify runner cannot deliver an order with a wrong OTP, and must supply correct 4-digit customer OTP."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer
        c_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9844455566", "otp": "123456", "role": "customer"})
        c_token = c_auth.json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}

        # Runner
        r_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9855566677", "otp": "123456", "role": "runner"})
        r_token = r_auth.json()["access_token"]
        r_headers = {"Authorization": f"Bearer {r_token}"}

        addr_res = await client.post("/api/v1/addresses", headers=c_headers, json={
            "title": "Home",
            "recipient_name": "OTP Test",
            "phone": "9844455566",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi"
        })
        addr_id = addr_res.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_id = stores[0]["id"]
        prod_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod_id = prod_res.json()[0]["id"]

        order_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_id,
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        order = order_res.json()
        order_id = order["id"]
        correct_otp = order["delivery_otp"]

        # Runner accepts and advances
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "ACCEPT"})
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "PICKUP"})
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "OUT_FOR_DELIVERY"})

        # 1. Wrong OTP -> 400
        wrong_res = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": "0000" if correct_otp != "0000" else "9999"
        })
        assert wrong_res.status_code == 400
        assert "गलत डिलीवरी ओटीपी" in wrong_res.json()["detail"]

        # 2. Correct OTP -> Success
        success_res = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": correct_otp
        })
        assert success_res.status_code == 200
        assert success_res.json()["message"] == "Order status updated to DELIVERED"
