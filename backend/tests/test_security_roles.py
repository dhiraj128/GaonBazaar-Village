import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_role_authentication_and_token_generation():
    """Verify customer, vendor, runner get appropriate JWT tokens and roles."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer
        c_headers = await issue_and_verify_test_token(client, "9911122233", "customer")
        assert "Authorization" in c_headers

        # Vendor
        v_headers = await issue_and_verify_test_token(client, "9922233344", "vendor")
        assert "Authorization" in v_headers

        # Runner
        r_headers = await issue_and_verify_test_token(client, "9933344455", "runner")
        assert "Authorization" in r_headers

@pytest.mark.asyncio
async def test_unapproved_vendor_not_in_customer_store_list():
    """Verify that unapproved stores do NOT appear in customer searches."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register a brand-new vendor with unique phone
        unique_phone = f"99{uuid.uuid4().int % 100000000:08d}"
        v_headers = await issue_and_verify_test_token(client, unique_phone, "vendor")

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
        a_headers = await issue_and_verify_test_token(client, "9100000001", "customer")

        # Customer B
        b_headers = await issue_and_verify_test_token(client, "9100000002", "customer")

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
