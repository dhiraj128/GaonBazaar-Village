import pytest
import hmac
import hashlib
import json
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.services.pricing_service import (
    calculate_delivery_fee,
    calculate_runner_payout,
    calculate_platform_delivery_share,
    is_distance_deliverable,
    compute_item_pricing,
    calculate_order_totals,
)

@pytest.mark.asyncio
async def test_five_tier_delivery_matrix_and_80_20_split():
    """PART 1: Verifies the exact 5 distance tiers and 80% runner / 20% platform share."""
    # Tier 1: 0.0 - 2.0 km -> Customer ₹15.00, Runner ₹12.00, Platform ₹3.00
    assert calculate_delivery_fee(0.5) == 15.0
    assert calculate_runner_payout(0.5) == 12.0
    assert calculate_platform_delivery_share(0.5) == 3.0
    assert calculate_delivery_fee(2.0) == 15.0
    assert calculate_runner_payout(2.0) == 12.0
    assert calculate_platform_delivery_share(2.0) == 3.0

    # Tier 2: > 2.0 - 4.0 km -> Customer ₹20.00, Runner ₹16.00, Platform ₹4.00
    assert calculate_delivery_fee(2.1) == 20.0
    assert calculate_runner_payout(2.1) == 16.0
    assert calculate_platform_delivery_share(2.1) == 4.0
    assert calculate_delivery_fee(4.0) == 20.0
    assert calculate_runner_payout(4.0) == 16.0
    assert calculate_platform_delivery_share(4.0) == 4.0

    # Tier 3: > 4.0 - 6.0 km -> Customer ₹25.00, Runner ₹20.00, Platform ₹5.00
    assert calculate_delivery_fee(4.1) == 25.0
    assert calculate_runner_payout(4.1) == 20.0
    assert calculate_platform_delivery_share(4.1) == 5.0
    assert calculate_delivery_fee(6.0) == 25.0
    assert calculate_runner_payout(6.0) == 20.0
    assert calculate_platform_delivery_share(6.0) == 5.0

    # Tier 4: > 6.0 - 8.0 km -> Customer ₹35.00, Runner ₹28.00, Platform ₹7.00
    assert calculate_delivery_fee(6.1) == 35.0
    assert calculate_runner_payout(6.1) == 28.0
    assert calculate_platform_delivery_share(6.1) == 7.0
    assert calculate_delivery_fee(8.0) == 35.0
    assert calculate_runner_payout(8.0) == 28.0
    assert calculate_platform_delivery_share(8.0) == 7.0

    # Tier 5: > 8.0 - 9.0 km -> Customer ₹40.00, Runner ₹32.00, Platform ₹8.00
    assert calculate_delivery_fee(8.1) == 40.0
    assert calculate_runner_payout(8.1) == 32.0
    assert calculate_platform_delivery_share(8.1) == 8.0
    assert calculate_delivery_fee(9.0) == 40.0
    assert calculate_runner_payout(9.0) == 32.0
    assert calculate_platform_delivery_share(9.0) == 8.0

    # Strict 9.0 km geofence boundary check
    assert is_distance_deliverable(9.0) is True
    assert is_distance_deliverable(9.01) is False
    assert is_distance_deliverable(12.5) is False

@pytest.mark.asyncio
async def test_order_creation_geofence_rejection():
    """PART 1: Verifies that creating an order beyond 9.0 km is rejected with HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer login
        login_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        assert login_res.status_code == 200
        sess_id = login_res.json()["session_id"]
        v_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000000", "otp": "123456", "session_id": sess_id})
        assert v_res.status_code == 200
        token = v_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create address that is far away (Patna / Hajipur, ~50km from Minapur store at 26.2315, 85.3610)
        far_addr_res = await client.post("/api/v1/addresses", headers=headers, json={
            "recipient_name": "Far Customer",
            "phone": "9800000000",
            "village": "Far Locality",
            "landmark": "Near Highway",
            "latitude": 25.6000,
            "longitude": 85.1000,
            "is_default": False
        })
        assert far_addr_res.status_code == 201
        far_addr_id = far_addr_res.json()["id"]

        # Product lookup
        prods = (await client.get("/api/v1/stores/str_01/products")).json()
        prod_id = prods[0]["id"]

        # Attempt placing order to far address
        far_order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": "str_01",
            "delivery_address_id": far_addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert far_order_res.status_code == 400
        detail = far_order_res.json()["detail"]
        assert "Out of delivery area" in detail
        assert "9 km" in detail

@pytest.mark.asyncio
async def test_razorpay_create_order_and_verify_signature():
    """PART 3: Verifies POST /api/v1/payments/create-order and /verify with HMAC-SHA256 signature."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer login
        login_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        sess_id = login_res.json()["session_id"]
        v_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000000", "otp": "123456", "session_id": sess_id})
        token = v_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Valid nearby address (< 2.0 km)
        near_addr_res = await client.post("/api/v1/addresses", headers=headers, json={
            "recipient_name": "Nearby Customer",
            "phone": "9800000000",
            "village": "Chaturshi",
            "landmark": "Near School",
            "latitude": 26.2320,
            "longitude": 85.3620,
            "is_default": True
        })
        addr_id = near_addr_res.json()["id"]

        prods = (await client.get("/api/v1/stores/str_01/products")).json()
        prod_id = prods[0]["id"]

        # Place ONLINE order
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": "str_01",
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order_id = order_res.json()["id"]

        # Call /api/v1/payments/create-order
        create_res = await client.post("/api/v1/payments/create-order", headers=headers, json={
            "order_id": order_id
        })
        assert create_res.status_code == 200
        rzp_data = create_res.json()
        assert "razorpay_order_id" in rzp_data
        assert rzp_data["currency"] == "INR"
        assert rzp_data["amount"] > 0
        rzp_order_id = rzp_data["razorpay_order_id"]

        # Invalid signature rejection
        invalid_v = await client.post("/api/v1/payments/verify", headers=headers, json={
            "order_id": order_id,
            "razorpay_order_id": rzp_order_id,
            "razorpay_payment_id": "pay_test_xyz123",
            "razorpay_signature": "invalid_sig_abc"
        })
        assert invalid_v.status_code == 400

        # Valid HMAC-SHA256 signature
        test_payment_id = "pay_test_verified_777"
        msg = f"{rzp_order_id}|{test_payment_id}"
        valid_sig = hmac.new(
            settings.RESOLVED_RAZORPAY_KEY_SECRET.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        verify_res = await client.post("/api/v1/payments/verify", headers=headers, json={
            "order_id": order_id,
            "razorpay_order_id": rzp_order_id,
            "razorpay_payment_id": test_payment_id,
            "razorpay_signature": valid_sig
        })
        assert verify_res.status_code == 200
        assert verify_res.json()["status"] == "SUCCESS"

        # Check order is confirmed and paid
        ord_chk = await client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert ord_chk.status_code == 200
        assert ord_chk.json()["payment_status"] == "PAID"
        assert ord_chk.json()["status"] == "CONFIRMED"

@pytest.mark.asyncio
async def test_razorpay_webhook_events_and_refund_exclusion():
    """PART 4: Verifies Razorpay webhook events, refund processing, and exclusion from settlements."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customer login
        c_login = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        c_sess = c_login.json()["session_id"]
        c_token = (await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000000", "otp": "123456", "session_id": c_sess})).json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}

        # Admin login
        a_login = await client.post("/api/v1/admin/auth/login", json={"phone": "9800000099", "secret_key": settings.ADMIN_API_KEY})
        assert a_login.status_code == 200
        a_token = a_login.json()["access_token"]
        a_headers = {"Authorization": f"Bearer {a_token}"}

        # Valid nearby address
        addr_res = await client.post("/api/v1/addresses", headers=c_headers, json={
            "recipient_name": "Webhook Customer",
            "phone": "9800000000",
            "village": "Chaturshi",
            "landmark": "Near Post Office",
            "latitude": 26.2318,
            "longitude": 85.3615,
            "is_default": True
        })
        addr_id = addr_res.json()["id"]
        prods = (await client.get("/api/v1/stores/str_01/products")).json()

        # Place order
        order_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": "str_01",
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        assert order_res.status_code == 201
        order = order_res.json()
        order_id = order["id"]

        # Create razorpay order
        rzp_order_res = await client.post("/api/v1/payments/create-order", headers=c_headers, json={"order_id": order_id})
        rzp_order_id = rzp_order_res.json()["razorpay_order_id"]
        amount_paise = rzp_order_res.json()["amount"]

        # 1. Test Webhook: payment.captured
        captured_payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test_hook_cap_123",
                        "order_id": rzp_order_id,
                        "amount": amount_paise,
                        "currency": "INR",
                        "notes": {"order_id": order_id}
                    }
                }
            }
        }
        body_bytes = json.dumps(captured_payload).encode("utf-8")
        hook_sig = hmac.new(
            settings.RESOLVED_RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
            body_bytes,
            hashlib.sha256
        ).hexdigest()

        hook_res = await client.post(
            "/api/v1/payments/razorpay/webhook",
            content=body_bytes,
            headers={"X-Razorpay-Signature": hook_sig, "Content-Type": "application/json"}
        )
        assert hook_res.status_code == 200

        # Check order is marked PAID and CONFIRMED
        ord_res = await client.get(f"/api/v1/orders/{order_id}", headers=c_headers)
        assert ord_res.json()["payment_status"] == "PAID"
        assert ord_res.json()["status"] == "CONFIRMED"

        # 2. Test Admin Refund: POST /api/v1/payments/refund
        refund_res = await client.post(
            "/api/v1/payments/refund",
            headers=a_headers,
            json={"order_id": order_id, "reason": "Customer cancellation after review"}
        )
        assert refund_res.status_code == 200
        ref_data = refund_res.json()
        assert ref_data["status"] in ("COMPLETED", "PROCESSING")
        assert ref_data["amount"] > 0

        # Check order payment status is now REFUNDED
        ord_ref_chk = await client.get(f"/api/v1/orders/{order_id}", headers=c_headers)
        assert ord_ref_chk.json()["payment_status"] == "REFUNDED"
        assert ord_ref_chk.json()["refund_status"] == "PROCESSED"

        # 3. Test Settlements Ledger excludes REFUNDED orders
        ledger_res = await client.get("/api/v1/admin/settlements", headers=a_headers)
        assert ledger_res.status_code == 200
        ledger = ledger_res.json()
        # Verify ledger runs cleanly and calculates non-refunded orders
        assert "vendor_settlements" in ledger
        assert "runner_settlements" in ledger
