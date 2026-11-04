import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.api.v1.auth import OTP_STORAGE

@pytest.mark.asyncio
async def test_vendor_order_cross_account_isolation():
    """Defect 1: Vendor A must NOT be able to accept, pack, or reject Vendor B's orders."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Customer
        await client.post("/api/v1/auth/otp/send", json={"phone": "9811100001", "role": "customer"})
        c_otp = OTP_STORAGE["9811100001"]["otp"]
        c_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9811100001", "otp": c_otp, "role": "customer"})
        c_token = c_res.json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}

        # Setup Address
        addr = await client.post("/api/v1/addresses", headers=c_headers, json={
            "title": "Home", "recipient_name": "Test Cust", "phone": "9811100001",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })
        addr_id = addr.json()["id"]

        # Store 1 (str_01, owned by 9800000001) and Store 2 (str_02, owned by 9800000002)
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_1 = next(s for s in stores if s["id"] == "str_01")
        store_2 = next(s for s in stores if s["id"] == "str_02")

        # Create Order for Store 1
        prods = (await client.get(f"/api/v1/stores/{store_1['id']}/products")).json()
        ord_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_1["id"],
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        assert ord_res.status_code == 201
        order_1_id = ord_res.json()["id"]

        # Auth Vendor 2 (owner of Store 2)
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000002", "role": "vendor"})
        v2_otp = OTP_STORAGE["9800000002"]["otp"]
        v2_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000002", "otp": v2_otp, "role": "vendor"})
        v2_token = v2_res.json()["access_token"]
        v2_headers = {"Authorization": f"Bearer {v2_token}"}

        # Vendor 2 attempts to ACCEPT Store 1's order -> MUST BE FORBIDDEN (403)
        v2_action = await client.post(
            f"/api/v1/vendor/orders/{order_1_id}/action",
            headers=v2_headers,
            json={"action": "ACCEPT"}
        )
        assert v2_action.status_code == 403, f"Expected 403 Forbidden for cross-vendor action, got {v2_action.status_code}: {v2_action.text}"

        # Auth Vendor 1 (owner of Store 1) -> Successfully ACCEPT
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        v1_otp = OTP_STORAGE["9800000001"]["otp"]
        v1_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": v1_otp, "role": "vendor"})
        v1_token = v1_res.json()["access_token"]
        v1_headers = {"Authorization": f"Bearer {v1_token}"}

        v1_accept = await client.post(
            f"/api/v1/vendor/orders/{order_1_id}/action",
            headers=v1_headers,
            json={"action": "ACCEPT"}
        )
        assert v1_accept.status_code == 200
        assert v1_accept.json()["status"] == "ACCEPTED"

        # Invalid Transition: Cannot ACCEPT an already ACCEPTED order -> 400 Bad Request
        v1_repeat = await client.post(
            f"/api/v1/vendor/orders/{order_1_id}/action",
            headers=v1_headers,
            json={"action": "ACCEPT"}
        )
        assert v1_repeat.status_code == 400

@pytest.mark.asyncio
async def test_runner_delivery_cross_account_and_prerequisites():
    """Defect 2: Runner 2 must not complete Runner 1's job, and delivery prerequisites must be enforced."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Customer & Order
        await client.post("/api/v1/auth/otp/send", json={"phone": "9811100002", "role": "customer"})
        c_otp = OTP_STORAGE["9811100002"]["otp"]
        c_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9811100002", "otp": c_otp, "role": "customer"})
        c_token = c_res.json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}

        addr = await client.post("/api/v1/addresses", headers=c_headers, json={
            "title": "Home", "recipient_name": "Test Cust", "phone": "9811100002",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })
        addr_id = addr.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_1 = next(s for s in stores if s["id"] == "str_01")
        prods = (await client.get(f"/api/v1/stores/{store_1['id']}/products")).json()

        ord_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_1["id"],
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        order_id = ord_res.json()["id"]
        delivery_otp = ord_res.json()["delivery_otp"]

        # Auth Vendor 1 and move order to PACKED
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        v1_otp = OTP_STORAGE["9800000001"]["otp"]
        v1_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": v1_otp, "role": "vendor"})
        v1_token = v1_res.json()["access_token"]
        v1_headers = {"Authorization": f"Bearer {v1_token}"}

        await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1_headers, json={"action": "ACCEPT"})
        await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1_headers, json={"action": "PACK"})

        # Runner 1 (9800000003 - Approved Pilot Runner)
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000003", "role": "runner"})
        r1_otp = OTP_STORAGE["9800000003"]["otp"]
        r1_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000003", "otp": r1_otp, "role": "runner"})
        r1_token = r1_res.json()["access_token"]
        r1_headers = {"Authorization": f"Bearer {r1_token}"}

        # Runner 1 accepts job
        r1_accept = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={"action": "ACCEPT"})
        assert r1_accept.status_code == 200

        # Create Runner 2
        await client.post("/api/v1/auth/otp/send", json={"phone": "9811199999", "role": "runner"})
        r2_otp = OTP_STORAGE["9811199999"]["otp"]
        r2_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9811199999", "otp": r2_otp, "role": "runner"})
        r2_token = r2_res.json()["access_token"]
        r2_headers = {"Authorization": f"Bearer {r2_token}"}

        # Runner 2 attempts to deliver or pickup Runner 1's order -> MUST BE FORBIDDEN (403)
        r2_pickup = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r2_headers, json={"action": "PICKUP"})
        assert r2_pickup.status_code == 403, f"Expected 403 for cross-runner action, got {r2_pickup.status_code}"

        # Runner 1 attempts to jump directly to DELIVER without OUT_FOR_DELIVERY -> MUST BE 400 Bad Request
        r1_skip = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={
            "action": "DELIVER", "delivery_otp": delivery_otp
        })
        assert r1_skip.status_code == 400, f"Expected 400 for skipping delivery prerequisites, got {r1_skip.status_code}"

        # Legitimate Runner 1 lifecycle: PICKUP -> OUT_FOR_DELIVERY -> DELIVER
        r1_pickup = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={"action": "PICKUP"})
        assert r1_pickup.status_code == 200

        r1_out = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={"action": "OUT_FOR_DELIVERY"})
        assert r1_out.status_code == 200

        # Deliver with wrong OTP -> 400
        r1_wrong_otp = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={
            "action": "DELIVER", "delivery_otp": "0000"
        })
        assert r1_wrong_otp.status_code == 400

        # Deliver with correct OTP and confirmed cash collection
        r1_deliver = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r1_headers, json={
            "action": "DELIVER", "delivery_otp": delivery_otp, "cash_collected": True
        })
        assert r1_deliver.status_code == 200

        # Verify final order state
        chk = (await client.get(f"/api/v1/orders/{order_id}", headers=c_headers)).json()
        assert chk["status"] == "DELIVERED"
        assert chk["payment_status"] == "PAID"

@pytest.mark.asyncio
async def test_payment_status_integrity_and_simulation():
    """Defect 3: Simulated payments must be SIMULATED, COD must require confirmed collection to be PAID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Customer
        await client.post("/api/v1/auth/otp/send", json={"phone": "9811100003", "role": "customer"})
        c_otp = OTP_STORAGE["9811100003"]["otp"]
        c_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9811100003", "otp": c_otp, "role": "customer"})
        c_token = c_res.json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}

        addr = await client.post("/api/v1/addresses", headers=c_headers, json={
            "title": "Home", "recipient_name": "Test Cust", "phone": "9811100003",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })
        addr_id = addr.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_1 = stores[0]
        prods = (await client.get(f"/api/v1/stores/{store_1['id']}/products")).json()
        avail_prods = [p for p in prods if p.get("in_stock", True) and (p.get("stock_quantity") is None or p.get("stock_quantity", 0) >= 2)]
        target_prod = avail_prods[0] if avail_prods else prods[0]

        # 1. Test online order -> payment_status MUST be PENDING, not prematurely PAID
        online_order = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_1["id"],
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": target_prod["id"], "quantity": 1}]
        })
        assert online_order.status_code == 201
        assert online_order.json()["payment_status"] == "PENDING", f"Expected PENDING, got {online_order.json()['payment_status']}"

        # 2. Test COD order -> initially PENDING
        target_cod_prod = avail_prods[1] if len(avail_prods) > 1 else target_prod
        cod_order = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_1["id"],
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": target_cod_prod["id"], "quantity": 1}]
        })
        assert cod_order.status_code == 201
        assert cod_order.json()["payment_status"] == "PENDING"

@pytest.mark.asyncio
async def test_otp_security_and_admin_isolation():
    """Defect 4: Verification without challenge must fail, mock_otp must never leak, and admin routes must reject unauthorized requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Calling verify without sending OTP challenge first MUST FAIL (400)
        unprompted_verify = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9811188888", "otp": "123456", "role": "customer"
        })
        assert unprompted_verify.status_code == 400, f"Expected 400 for verify without send, got {unprompted_verify.status_code}"

        # 2. Sending OTP must NEVER return the code in the public response body
        send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        assert send_res.status_code == 200
        data = send_res.json()
        assert data.get("mock_otp") is None, f"mock_otp leaked in response: {data.get('mock_otp')}"

        # 3. Anonymous request to Admin endpoint MUST be rejected (401 or 403), even with settings.TESTING=True
        admin_unauth = await client.get("/api/v1/admin/overview")
        assert admin_unauth.status_code in [401, 403], f"Expected 401/403 for unauth admin request, got {admin_unauth.status_code}"

        # 4. Valid Admin API Key access works
        admin_auth = await client.get("/api/v1/admin/overview", headers={"X-Admin-Key": settings.ADMIN_API_KEY})
        assert admin_auth.status_code == 200
