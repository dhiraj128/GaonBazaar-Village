import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_otp_bypass_restricted_for_public_numbers():
    """Verify fixed '123456' OTP cannot be used by unauthorized public numbers."""
    settings.TESTING = False
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            public_phone = "9876543219"
            
            # 1. Send OTP to public number
            send_res = await client.post("/api/v1/auth/otp/send", json={
                "phone": public_phone,
                "role": "customer"
            })
            assert send_res.status_code == 200
            send_data = send_res.json()
            assert send_data["mock_otp"] is None, "Public numbers must NEVER expose mock_otp in API response"

            # 2. Attempt fixed OTP '123456' bypass on public number -> must fail
            verify_res = await client.post("/api/v1/auth/otp/verify", json={
                "phone": public_phone,
                "otp": "123456",
                "role": "customer"
            })
            assert verify_res.status_code == 400, "Fixed OTP bypass must be rejected for public non-whitelisted numbers"
            assert "गलत ओटीपी" in verify_res.json()["detail"]

            # 3. Verify authorized whitelisted test persona (9800000000) requires genuine challenge issuance first
            from app.api.v1.auth import OTP_STORAGE
            test_phone = "9800000000"
            OTP_STORAGE.pop(test_phone, None)
            t_send = await client.post("/api/v1/auth/otp/send", json={
                "phone": test_phone,
                "role": "customer"
            })
            assert t_send.status_code == 200
            assert t_send.json()["mock_otp"] is None, "Even for test personas, response must never leak usable OTP"

            t_verify = await client.post("/api/v1/auth/otp/verify", json={
                "phone": test_phone,
                "otp": "123456",
                "role": "customer"
            })
            assert t_verify.status_code == 200
            assert "access_token" in t_verify.json()
    finally:
        settings.TESTING = True

@pytest.mark.asyncio
async def test_admin_authentication_and_route_protection():
    """Verify all admin endpoints require valid JWT admin token or X-Admin-Key."""
    settings.TESTING = False
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Anonymous access is strictly rejected
            anon_res = await client.get("/api/v1/admin/overview")
            assert anon_res.status_code == 403, "Anonymous access to admin overview must return 403 Forbidden"

            # 2. Invalid login fails
            bad_login = await client.post("/api/v1/admin/auth/login", json={
                "phone": "9800000099",
                "secret_key": "wrong_key",
                "otp": "000000"
            })
            assert bad_login.status_code == 401

            # 3. Successful admin login with Admin Key
            good_login = await client.post("/api/v1/admin/auth/login", json={
                "phone": "9800000099",
                "secret_key": settings.ADMIN_API_KEY
            })
            assert good_login.status_code == 200
            admin_token = good_login.json()["access_token"]
            assert good_login.json()["user"]["role"] == "admin"

            # 4. Authenticated request using JWT token succeeds
            auth_headers = {"Authorization": f"Bearer {admin_token}"}
            overview_res = await client.get("/api/v1/admin/overview", headers=auth_headers)
            assert overview_res.status_code == 200
            assert overview_res.json()["pilot_area"] == "Minapur, Muzaffarpur, Bihar"

            # 5. Access with X-Admin-Key header also succeeds
            key_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
            vendors_res = await client.get("/api/v1/admin/vendors", headers=key_headers)
            assert vendors_res.status_code == 200
            assert isinstance(vendors_res.json(), list)
    finally:
        settings.TESTING = True

@pytest.mark.asyncio
async def test_financial_safeguards_for_test_accounts():
    """Verify orders placed by test accounts cannot trigger real external payment captures."""
    settings.TESTING = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Authenticate test customer 9800000000 cleanly
        headers = await issue_and_verify_test_token(client, "9800000000", "customer")

        # Fetch nearby stores
        stores_res = await client.get("/api/v1/stores/nearby?latitude=26.2210&longitude=85.3500&radius_km=8.0")
        store_id = stores_res.json()[0]["id"]

        # Add delivery address for customer
        addr_res = await client.post("/api/v1/addresses", headers=headers, json={
            "title": "Home",
            "recipient_name": "Ramesh Singh",
            "phone": "9800000000",
            "latitude": 26.2210,
            "longitude": 85.3500,
            "village": "Chaturshi",
            "landmark": "Near Shiv Mandir",
            "is_default": True
        })
        assert addr_res.status_code == 201
        addr_id = addr_res.json()["id"]

        # Fetch store products
        prods_res = await client.get(f"/api/v1/stores/{store_id}/products")
        prod_id = prods_res.json()[0]["id"]

        # Place simulated online order
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": store_id,
            "delivery_address_id": addr_id,
            "items": [{"product_id": prod_id, "quantity": 1}],
            "payment_method": "ONLINE"
        })
        assert order_res.status_code == 201
        order_data = order_res.json()
        assert order_data["payment_method"] == "ONLINE_SIMULATED", "Test account orders must use simulated mode to avoid real financial gateway capture"
        assert order_data["payment_status"] == "SIMULATED", "Simulated orders must be tracked as SIMULATED, not genuinely PAID"
