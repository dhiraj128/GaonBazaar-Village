import hmac
import hashlib
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_razorpay_order_and_verify_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login as customer
        login_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        assert login_res.status_code == 200
        session_id = login_res.json()["session_id"]
        
        verify_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000000",
            "otp": "123456",
            "session_id": session_id
        })
        assert verify_res.status_code == 200
        token = verify_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check payment gateway status endpoint
        status_res = await client.get("/api/v1/payments/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["cod_enabled"] is True
        assert status_data["default_method"] == "COD"
        
        # 3. Get customer addresses
        addr_res = await client.get("/api/v1/addresses", headers=headers)
        assert addr_res.status_code == 200
        addr_id = addr_res.json()[0]["id"]
        
        # 4. Get store products
        prod_res = await client.get("/api/v1/stores/str_01/products")
        assert prod_res.status_code == 200
        products = prod_res.json()
        assert len(products) > 0
        prod_id = products[0]["id"]
        
        # 5. Create Order with ONLINE payment method
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": "str_01",
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order_data = order_res.json()
        order_id = order_data["id"]
        assert order_data["payment_status"] == "PENDING"
        assert order_data["payment_method"] == "ONLINE"
        # Customer MUST see delivery_otp
        assert order_data["delivery_otp"] is not None
        customer_otp = order_data["delivery_otp"]
        
        # 6. Test unconfigured Razorpay returns 503 prompting COD
        rzp_order_res = await client.post("/api/v1/payments/razorpay/order", headers=headers, json={
            "order_id": order_id
        })
        assert rzp_order_res.status_code == 503
        assert "Cash on Delivery" in rzp_order_res.json()["detail"]

        # 7. Test Razorpay payment verification strictly enforces HMAC-SHA256
        # A. Mock / invalid signature must be REJECTED (no test_sig bypass!)
        fake_verify = await client.post("/api/v1/payments/razorpay/verify", headers=headers, json={
            "order_id": order_id,
            "razorpay_order_id": "order_fake_123",
            "razorpay_payment_id": "pay_fake_456",
            "razorpay_signature": "test_sig_verified"
        })
        assert fake_verify.status_code == 400
        assert "Invalid Razorpay payment signature" in fake_verify.json()["detail"]

        # B. Mathematically valid HMAC-SHA256 signature calculated with server secret MUST SUCCEED
        test_rzp_order_id = "order_rzp_test_secure_99"
        test_rzp_payment_id = "pay_rzp_test_capture_88"
        msg = f"{test_rzp_order_id}|{test_rzp_payment_id}"
        valid_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        valid_verify = await client.post("/api/v1/payments/razorpay/verify", headers=headers, json={
            "order_id": order_id,
            "razorpay_order_id": test_rzp_order_id,
            "razorpay_payment_id": test_rzp_payment_id,
            "razorpay_signature": valid_signature
        })
        assert valid_verify.status_code == 200
        assert valid_verify.json()["status"] == "SUCCESS"

        # 8. Check order status is now PAID
        check_order = await client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert check_order.status_code == 200
        assert check_order.json()["payment_status"] == "PAID"
        assert check_order.json()["payment_method"] == "ONLINE"
        # Customer still sees delivery OTP
        assert check_order.json()["delivery_otp"] == customer_otp

@pytest.mark.asyncio
async def test_order_security_and_delivery_otp_isolation():
    """
    Stage A3 Test: Delivery PIN must NEVER be exposed to Vendor or Runner.
    Runner enters it at delivery for backend verification.
    Unauthorized users cannot inspect order details.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Customer login and place COD order
        c_login = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        c_sess = c_login.json()["session_id"]
        c_tok = (await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000000", "otp": "123456", "session_id": c_sess})).json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_tok}"}

        addr_id = (await client.get("/api/v1/addresses", headers=c_headers)).json()[0]["id"]
        prod_id = (await client.get("/api/v1/stores/str_01/products")).json()[0]["id"]

        order_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": "str_01",
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order = order_res.json()
        order_id = order["id"]
        customer_otp = order["delivery_otp"]
        assert customer_otp is not None and len(customer_otp) >= 4

        # 2. Vendor login
        v_login = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        v_sess = v_login.json()["session_id"]
        v_tok = (await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": "123456", "session_id": v_sess})).json()["access_token"]
        v_headers = {"Authorization": f"Bearer {v_tok}"}

        # Check vendor orders: delivery_otp MUST BE None
        v_orders = (await client.get("/api/v1/vendor/orders", headers=v_headers)).json()
        matching_v_order = next((o for o in v_orders if o["id"] == order_id), None)
        assert matching_v_order is not None
        assert matching_v_order["delivery_otp"] is None, "Security violation: Vendor received customer delivery OTP!"

        # Vendor accepts and packs order
        acc = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v_headers, json={"action": "ACCEPT"})
        assert acc.status_code == 200
        pck = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v_headers, json={"action": "PACKED"})
        assert pck.status_code == 200

        # 3. Runner login (9800000003 is Santosh Kumar, runner)
        r_login = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000003", "role": "runner"})
        r_sess = r_login.json()["session_id"]
        r_tok = (await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000003", "otp": "123456", "session_id": r_sess})).json()["access_token"]
        r_headers = {"Authorization": f"Bearer {r_tok}"}

        # Check runner jobs: delivery_otp MUST BE None
        r_jobs = (await client.get("/api/v1/runner/jobs", headers=r_headers)).json()
        matching_r_job = next((j for j in r_jobs if j["id"] == order_id), None)
        assert matching_r_job is not None
        assert matching_r_job["delivery_otp"] is None, "Security violation: Runner received customer delivery OTP!"

        # Runner accepts, picks up, and marks out for delivery
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "ACCEPT"})
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "PICKUP"})
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "OUT_FOR_DELIVERY"})

        # 4. Runner location update & live tracking check
        loc_res = await client.put("/api/v1/runner/location", headers=r_headers, json={"latitude": 26.2235, "longitude": 85.3525})
        assert loc_res.status_code == 200

        # Customer live tracking
        track_res = await client.get(f"/api/v1/orders/{order_id}/tracking", headers=c_headers)
        assert track_res.status_code == 200
        track_data = track_res.json()
        assert track_data["is_live_tracking_active"] is True
        assert track_data["runner_latitude"] == 26.2235

        # 5. Delivery attempt with WRONG OTP must FAIL
        wrong_del = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": "0000",
            "cash_collected": True
        })
        assert wrong_del.status_code == 400
        assert "Invalid Customer Delivery OTP" in wrong_del.json()["detail"] or "ओटीपी" in wrong_del.json()["detail"]

        # 6. Delivery attempt with CORRECT verbal customer OTP must SUCCEED
        good_del = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": customer_otp,
            "cash_collected": True
        })
        assert good_del.status_code == 200

        # 7. Verify order status DELIVERED and COD payment status PAID
        delivered_order = (await client.get(f"/api/v1/orders/{order_id}", headers=c_headers)).json()
        assert delivered_order["status"] == "DELIVERED"
        assert delivered_order["payment_status"] == "PAID"
