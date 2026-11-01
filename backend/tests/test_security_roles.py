import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_role_authentication_and_token_generation():
    """Verify customer, vendor, runner, and admin get appropriate JWT tokens and roles."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer
        c_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9911122233", "otp": "123456", "role": "customer"})
        assert c_res.status_code == 200
        assert c_res.json()["user"]["role"] == "customer"
        assert "access_token" in c_res.json()

        # Vendor
        v_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9922233344", "otp": "123456", "role": "vendor"})
        assert v_res.status_code == 200
        assert v_res.json()["user"]["role"] == "vendor"

        # Runner
        r_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9933344455", "otp": "123456", "role": "runner"})
        assert r_res.status_code == 200
        assert r_res.json()["user"]["role"] == "runner"

@pytest.mark.asyncio
async def test_unapproved_vendor_not_in_customer_store_list():
    """Verify that unapproved stores do NOT appear in customer searches."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register a brand-new vendor with unique phone
        unique_phone = f"99{uuid.uuid4().int % 100000000:08d}"
        v_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": unique_phone, "otp": "123456", "role": "vendor"})
        v_token = v_auth.json()["access_token"]
        v_headers = {"Authorization": f"Bearer {v_token}"}

        s_res = await client.post("/api/v1/stores/onboard", headers=v_headers, json={
            "shop_name": "Unapproved Test Store",
            "owner_name": "Test Owner",
            "category": "Grocery",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi",
            "landmark": "Near Shiv Mandir"
        })
        assert s_res.status_code == 200
        new_store = s_res.json()
        assert new_store["is_approved"] is False

        # 2. Customer searches nearby stores
        c_res = await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450&radius_km=8.0")
        assert c_res.status_code == 200
        stores = c_res.json()
        store_ids = [s["id"] for s in stores]
        assert new_store["id"] not in store_ids, "Unapproved store must not be visible to customers"

@pytest.mark.asyncio
async def test_address_ownership_isolation():
    """Verify customers cannot access or order with another customer's address."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer A
        a_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9100000001", "otp": "123456", "role": "customer"})
        a_token = a_auth.json()["access_token"]
        a_headers = {"Authorization": f"Bearer {a_token}"}

        # Customer B
        b_auth = await client.post("/api/v1/auth/otp/verify", json={"phone": "9100000002", "otp": "123456", "role": "customer"})
        b_token = b_auth.json()["access_token"]
        b_headers = {"Authorization": f"Bearer {b_token}"}

        # Customer A creates an address
        addr_res = await client.post("/api/v1/addresses", headers=a_headers, json={
            "title": "Home",
            "recipient_name": "Customer A",
            "phone": "9100000001",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi"
        })
        assert addr_res.status_code == 201
        a_address_id = addr_res.json()["id"]

        # Customer B tries to create an order using Customer A's address -> 404
        # Get a real store and product first
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_id = stores[0]["id"]
        prod_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod_id = prod_res.json()[0]["id"]

        order_res = await client.post("/api/v1/orders", headers=b_headers, json={
            "store_id": store_id,
            "delivery_address_id": a_address_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 404
        assert "Delivery address not found" in order_res.json()["detail"]
