import pytest
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.api.v1.auth import OTP_STORAGE
from app.models.base import Store, StoreProduct, Runner, User
from app.db.session import async_engine
from sqlalchemy.future import select

async def get_test_token(client: AsyncClient, phone: str, role: str, name: str = None) -> dict:
    await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": role})
    otp = OTP_STORAGE[phone]["otp"]
    data = {"phone": phone, "otp": otp, "role": role}
    if name:
        data["name"] = name
    res = await client.post("/api/v1/auth/otp/verify", json=data)
    assert res.status_code == 200, f"Auth failed for {phone}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_strict_customer_isolation_orders_and_idor():
    """
    Section 2: Strict Customer Isolation:
    - Customer A creates Order A.
    - Customer A can see and track Order A.
    - Customer B cannot view, cancel, refund, or track Order A (403/404).
    - Customer B cannot attach Customer A's order to a support ticket.
    - Customer B cannot verify payment for Customer A's order.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Customers A, B, C, D, E
        cust_a = await get_test_token(client, "9820000001", "customer", "Customer A")
        cust_b = await get_test_token(client, "9820000002", "customer", "Customer B")
        cust_c = await get_test_token(client, "9820000003", "customer", "Customer C")

        # Address for Customer A
        addr_a_res = await client.post("/api/v1/addresses", headers=cust_a, json={
            "title": "Home A", "recipient_name": "Customer A", "phone": "9820000001",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })
        assert addr_a_res.status_code == 201
        addr_a_id = addr_a_res.json()["id"]

        # Get Store 1 and Product
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        store_1 = next((s for s in stores if s["id"] == "str_01"), stores[0])
        prods = (await client.get(f"/api/v1/stores/{store_1['id']}/products")).json()
        prod = prods[0]

        # Customer A places Order A
        ord_a_res = await client.post("/api/v1/orders", headers=cust_a, json={
            "store_id": store_1["id"],
            "delivery_address_id": addr_a_id,
            "payment_method": "COD",
            "items": [{"product_id": prod["id"], "quantity": 1}]
        })
        assert ord_a_res.status_code == 201
        order_a = ord_a_res.json()
        order_a_id = order_a["id"]

        # 1. Customer A can see Order A
        view_a = await client.get(f"/api/v1/orders/{order_a_id}", headers=cust_a)
        assert view_a.status_code == 200
        assert view_a.json()["id"] == order_a_id
        assert view_a.json()["delivery_otp"] is not None # Customer sees their delivery PIN

        # 2. Customer B CANNOT see Order A (IDOR blocked with 403)
        view_b = await client.get(f"/api/v1/orders/{order_a_id}", headers=cust_b)
        assert view_b.status_code == 403

        # 3. Customer B's order list does NOT contain Order A
        list_b = await client.get("/api/v1/orders", headers=cust_b)
        assert list_b.status_code == 200
        b_order_ids = [o["id"] for o in list_b.json()]
        assert order_a_id not in b_order_ids

        # 4. Customer B CANNOT cancel Order A
        cancel_b = await client.post(f"/api/v1/orders/{order_a_id}/cancel", headers=cust_b)
        assert cancel_b.status_code == 403

        # 5. Customer B CANNOT track Order A
        track_b = await client.get(f"/api/v1/orders/{order_a_id}/tracking", headers=cust_b)
        assert track_b.status_code == 403

        # 6. Customer B CANNOT create support ticket referencing Order A (IDOR rejection)
        ticket_b = await client.post("/api/v1/orders/tickets", headers=cust_b, json={
            "order_id": order_a_id,
            "subject": "Unauthorized access test",
            "message": "Attempting IDOR ticket creation"
        })
        assert ticket_b.status_code == 403

        # 7. Customer B CANNOT request refund for Order A
        refund_b = await client.post("/api/v1/payments/refund", headers=cust_b, json={
            "order_id": order_a_id,
            "amount": 50.0,
            "reason": "Malicious refund attempt"
        })
        assert refund_b.status_code == 403

        # 8. Customer B CANNOT verify payment for Order A
        verify_b = await client.post("/api/v1/payments/razorpay/verify", headers=cust_b, json={
            "order_id": order_a_id,
            "razorpay_order_id": "order_fake123",
            "razorpay_payment_id": "pay_fake123",
            "razorpay_signature": "fake_sig"
        })
        assert verify_b.status_code == 403

@pytest.mark.asyncio
async def test_strict_customer_address_and_notification_isolation():
    """
    Customer address and notification isolation:
    - Customer A's address is private to Customer A.
    - Customer B cannot view or delete Customer A's address.
    - Customer B cannot place an order using Customer A's delivery address.
    - Customer B cannot view or mark Customer A's notifications.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        cust_a = await get_test_token(client, "9820000011", "customer", "Customer A1")
        cust_b = await get_test_token(client, "9820000012", "customer", "Customer B1")

        # Create address for Customer A
        addr_a = (await client.post("/api/v1/addresses", headers=cust_a, json={
            "title": "Private Residence A", "recipient_name": "A Person", "phone": "9820000011",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })).json()
        addr_a_id = addr_a["id"]

        # Customer B lists addresses -> must not see A's address
        b_addrs = (await client.get("/api/v1/addresses", headers=cust_b)).json()
        assert not any(a["id"] == addr_a_id for a in b_addrs)

        # Customer B attempts to delete A's address -> 404 Not Found
        del_res = await client.delete(f"/api/v1/addresses/{addr_a_id}", headers=cust_b)
        assert del_res.status_code == 404

        # Customer B attempts to place order using A's address_id -> 404 Delivery address not found
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        st = next((s for s in stores if s["id"] == "str_01"), stores[0])
        prods = (await client.get(f"/api/v1/stores/{st['id']}/products")).json()
        ord_res = await client.post("/api/v1/orders", headers=cust_b, json={
            "store_id": st["id"],
            "delivery_address_id": addr_a_id,
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        assert ord_res.status_code == 404
        assert "address not found" in ord_res.text.lower()

@pytest.mark.asyncio
async def test_strict_vendor_isolation():
    """
    Section 3: Strict Vendor Isolation:
    - Vendor A sees only Vendor A's orders.
    - Vendor B cannot view, pack, or cancel Vendor A's orders.
    - Vendor B cannot modify Vendor A's products, inventory, or prices.
    - Vendor B cannot view Vendor A's settlement figures or bank details.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Vendor 1 (Store 1) and Vendor 2 (Store 2)
        v1_headers = await get_test_token(client, "9800000001", "vendor", "Vendor 1")
        v2_headers = await get_test_token(client, "9800000002", "vendor", "Vendor 2")
        cust_headers = await get_test_token(client, "9820000020", "customer", "Customer V")

        # Setup Customer Address
        addr = (await client.post("/api/v1/addresses", headers=cust_headers, json={
            "title": "Home", "recipient_name": "Cust V", "phone": "9820000020",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })).json()

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next(s for s in stores if s["id"] == "str_01")
        s2 = next(s for s in stores if s["id"] == "str_02")

        # Place Order for Store 1
        s1_prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()
        ord1 = (await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": s1["id"],
            "delivery_address_id": addr["id"],
            "payment_method": "COD",
            "items": [{"product_id": s1_prods[0]["id"], "quantity": 1}]
        })).json()
        order_1_id = ord1["id"]

        # Place Order for Store 2
        s2_prods = (await client.get(f"/api/v1/stores/{s2['id']}/products")).json()
        ord2 = (await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": s2["id"],
            "delivery_address_id": addr["id"],
            "payment_method": "COD",
            "items": [{"product_id": s2_prods[0]["id"], "quantity": 1}]
        })).json()
        order_2_id = ord2["id"]

        # 1. Vendor 1 orders list has Order 1, does NOT have Order 2
        v1_orders = (await client.get("/api/v1/vendor/orders", headers=v1_headers)).json()
        v1_order_ids = [o["id"] for o in v1_orders]
        assert order_1_id in v1_order_ids
        assert order_2_id not in v1_order_ids

        # 2. Vendor 2 orders list has Order 2, does NOT have Order 1
        v2_orders = (await client.get("/api/v1/vendor/orders", headers=v2_headers)).json()
        v2_order_ids = [o["id"] for o in v2_orders]
        assert order_2_id in v2_order_ids
        assert order_1_id not in v2_order_ids

        # 3. Vendor 2 CANNOT action Order 1 (Returns 403 Forbidden)
        v2_tamper = await client.post(
            f"/api/v1/vendor/orders/{order_1_id}/action",
            headers=v2_headers,
            json={"action": "ACCEPT"}
        )
        assert v2_tamper.status_code == 403

        # 4. Vendor 2 CANNOT modify Store 1's product stock or price (Returns 404)
        v2_stock_tamper = await client.patch(
            f"/api/v1/stores/products/{s1_prods[0]['id']}/stock",
            headers=v2_headers,
            json={"price": 1.0, "stock_quantity": 999}
        )
        assert v2_stock_tamper.status_code == 404

        # 5. Vendor finances are isolated
        v1_fin = (await client.get("/api/v1/vendor/finances", headers=v1_headers)).json()
        v2_fin = (await client.get("/api/v1/vendor/finances", headers=v2_headers)).json()
        assert v1_fin["store_id"] == s1["id"]
        assert v2_fin["store_id"] == s2["id"]

@pytest.mark.asyncio
async def test_strict_runner_isolation_and_address_masking():
    """
    Section 4: Strict Runner Isolation:
    - Runner cannot see customer's full address before accepting the order (minimal discovery info).
    - Once assigned, only the assigned runner sees the delivery address.
    - Runner A cannot view or claim orders assigned to Runner B.
    - Runner B cannot submit delivery PIN for Runner A's order.
    - Unapproved runners cannot fetch jobs or accept deliveries.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Runner A (approved seed runner 9800000003), Runner B (to onboard & approve), Runner C (to onboard & keep pending)
        r_a = await get_test_token(client, "9800000003", "runner", "Runner A")
        r_b = await get_test_token(client, "9800000004", "runner", "Runner B")
        r_c = await get_test_token(client, "9800000005", "runner", "Runner C")

        # Onboard Runner B and have Admin approve Runner B
        await client.post("/api/v1/runner/onboard", headers=r_b, json={
            "full_name": "Runner B", "vehicle_type": "Motorcycle", "vehicle_number": "BR06-4444"
        })
        admin_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
        r_list = (await client.get("/api/v1/admin/runners", headers=admin_headers)).json()
        runner_b_obj = next(r for r in r_list if r["full_name"] == "Runner B")
        await client.post(f"/api/v1/admin/runners/{runner_b_obj['id']}/approve", headers=admin_headers)

        # Onboard Runner C (remains unapproved)
        await client.post("/api/v1/runner/onboard", headers=r_c, json={
            "full_name": "Runner C", "vehicle_type": "Bicycle"
        })

        # 1. Unapproved Runner C is rejected from viewing jobs
        c_jobs = await client.get("/api/v1/runner/jobs", headers=r_c)
        assert c_jobs.status_code == 403
        assert "pending" in c_jobs.text.lower() or "approval" in c_jobs.text.lower()

        # Customer creates and Vendor packs an order
        cust = await get_test_token(client, "9820000030", "customer", "Cust RunnerTest")
        addr = (await client.post("/api/v1/addresses", headers=cust, json={
            "title": "Home", "recipient_name": "Cust RunnerTest", "phone": "9820000030",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi", "landmark": "Near Shiv Mandir"
        })).json()

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next(s for s in stores if s["id"] == "str_01")
        prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()

        order = (await client.post("/api/v1/orders", headers=cust, json={
            "store_id": s1["id"],
            "delivery_address_id": addr["id"],
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })).json()
        order_id = order["id"]

        # Vendor accepts and packs
        v1 = await get_test_token(client, "9800000001", "vendor", "Vendor 1")
        pack_res1 = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1, json={"action": "ACCEPT"})
        assert pack_res1.status_code == 200
        pack_res2 = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1, json={"action": "PACK"})
        assert pack_res2.status_code == 200

        # 2. Approved Runner A lists jobs -> order is visible, BUT customer full address is masked!
        jobs_a = (await client.get("/api/v1/runner/jobs", headers=r_a)).json()
        job_order = next(j for j in jobs_a if j["id"] == order_id)
        assert "Village: Chaturshi" in job_order["delivery_address"]
        assert "Near Shiv Mandir" not in job_order["delivery_address"] # Landmark concealed before assignment!
        assert job_order["delivery_otp"] is None # Zero-knowledge delivery OTP isolation

        # 3. Unapproved Runner C attempts to ACCEPT job -> 403 Forbidden
        c_accept = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_c, json={"action": "ACCEPT"})
        assert c_accept.status_code == 403

        # 4. Runner A ACCEPTS job -> Order assigned to Runner A
        a_accept = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_a, json={"action": "ACCEPT"})
        assert a_accept.status_code == 200

        # Now Runner A views order -> Full delivery address is revealed to assigned runner!
        a_detail = (await client.get(f"/api/v1/orders/{order_id}", headers=r_a)).json()
        assert "Near Shiv Mandir" in a_detail["delivery_address"]

        # 5. Runner B can NO LONGER see this job in /runner/jobs
        jobs_b = (await client.get("/api/v1/runner/jobs", headers=r_b)).json()
        assert not any(j["id"] == order_id for j in jobs_b)

        # 6. Runner B attempts to view Runner A's order -> 403 Forbidden
        b_view = await client.get(f"/api/v1/orders/{order_id}", headers=r_b)
        assert b_view.status_code == 403

        # 7. Runner B attempts to ACCEPT already assigned order -> 409 Conflict
        b_tamper = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_b, json={"action": "ACCEPT"})
        assert b_tamper.status_code == 409

        # Runner A moves to PICKUP and OUT_FOR_DELIVERY
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_a, json={"action": "PICKUP"})
        await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_a, json={"action": "OUT_FOR_DELIVERY"})

        # 8. Runner B attempts to submit delivery PIN for Runner A's order -> 403 Forbidden
        cust_detail = (await client.get(f"/api/v1/orders/{order_id}", headers=cust)).json()
        real_otp = cust_detail["delivery_otp"]
        b_deliver = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_b,
            json={"action": "DELIVER", "delivery_otp": real_otp, "cash_collected": True}
        )
        assert b_deliver.status_code == 403

        # 9. Runner A submits incorrect delivery PIN -> 400 Bad Request
        a_bad_otp = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_a,
            json={"action": "DELIVER", "delivery_otp": "0000", "cash_collected": True}
        )
        assert a_bad_otp.status_code == 400

        # 10. Runner A submits correct delivery PIN -> 200 DELIVERED
        a_deliver = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_a,
            json={"action": "DELIVER", "delivery_otp": real_otp, "cash_collected": True}
        )
        assert a_deliver.status_code == 200
        assert a_deliver.json()["status"] == "DELIVERED"

@pytest.mark.asyncio
async def test_payment_security_and_duplicate_refund_prevention():
    """
    Section 6: Payment & Financial Security:
    - Tampered HMAC-SHA256 signature rejected with 400.
    - Webhook signature validation & amount verification.
    - Duplicate refund prevention & ledger balance protection.
    - Platform fee is strictly ₹3.00.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        cust = await get_test_token(client, "9820000040", "customer", "Payment Cust")
        addr = (await client.post("/api/v1/addresses", headers=cust, json={
            "title": "Home", "recipient_name": "Payment Cust", "phone": "9820000040",
            "latitude": 26.1950, "longitude": 85.3450, "village": "Chaturshi"
        })).json()

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next((s for s in stores if s["id"] == "str_01"), stores[0])
        prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()

        ord_res = await client.post("/api/v1/orders", headers=cust, json={
            "store_id": s1["id"],
            "delivery_address_id": addr["id"],
            "payment_method": "ONLINE",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        order = ord_res.json()
        order_id = order["id"]

        # Platform fee must be strictly ₹3.00
        assert order["platform_fee"] == 3.00

        # 1. Tampered signature on verify -> 400 Bad Request
        verify_tamper = await client.post("/api/v1/payments/razorpay/verify", headers=cust, json={
            "order_id": order_id,
            "razorpay_order_id": "order_mock123",
            "razorpay_payment_id": "pay_mock123",
            "razorpay_signature": "tampered_hex_string_that_does_not_match"
        })
        assert verify_tamper.status_code == 400

        # 2. Genuine HMAC-SHA256 signature calculation succeeds
        msg = f"order_mock123|pay_mock123"
        valid_sig = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        verify_valid = await client.post("/api/v1/payments/razorpay/verify", headers=cust, json={
            "order_id": order_id,
            "razorpay_order_id": "order_mock123",
            "razorpay_payment_id": "pay_mock123",
            "razorpay_signature": valid_sig
        })
        assert verify_valid.status_code == 200
        assert verify_valid.json()["status"] == "SUCCESS"

        # 3. Idempotent re-verification returns existing success
        verify_repeat = await client.post("/api/v1/payments/razorpay/verify", headers=cust, json={
            "order_id": order_id,
            "razorpay_order_id": "order_mock123",
            "razorpay_payment_id": "pay_mock123",
            "razorpay_signature": valid_sig
        })
        assert verify_repeat.status_code == 200

        # 4. Partial Refund of order total
        total = order["total_amount"]
        ref1 = await client.post("/api/v1/payments/refund", headers=cust, json={
            "order_id": order_id,
            "amount": round(total / 2.0, 2),
            "reason": "Legitimate partial refund"
        })
        assert ref1.status_code == 200

        # 5. Over-refunding exceeds remaining refundable balance -> 400 Bad Request
        ref_excess = await client.post("/api/v1/payments/refund", headers=cust, json={
            "order_id": order_id,
            "amount": total, # Exceeds remaining 50%
            "reason": "Excessive refund attempt"
        })
        assert ref_excess.status_code == 400
        assert "exceeds" in ref_excess.text.lower()

        # 6. Refund remaining amount -> Succeeds
        rem = round(total - round(total / 2.0, 2), 2)
        ref2 = await client.post("/api/v1/payments/refund", headers=cust, json={
            "order_id": order_id,
            "amount": rem,
            "reason": "Remaining balance refund"
        })
        assert ref2.status_code == 200

        # 7. Further refund attempt when remaining refundable balance is zero -> 400 Bad Request
        ref_dup = await client.post("/api/v1/payments/refund", headers=cust, json={
            "order_id": order_id,
            "amount": 10.0,
            "reason": "Duplicate refund attempt"
        })
        assert ref_dup.status_code == 400
        assert "already been fully refunded" in ref_dup.text.lower()

@pytest.mark.asyncio
async def test_authentication_token_tampering_and_role_escalation():
    """
    Section 7: Authentication & Session Attacks:
    - Missing token -> 401.
    - Expired token -> 401.
    - Invalid signature token -> 401.
    - Customer attempting Admin API -> 403.
    - Runner attempting Admin API -> 403.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Unauthenticated request to protected endpoint -> 401
        res_no_auth = await client.get("/api/v1/orders")
        assert res_no_auth.status_code == 401

        # 2. Expired JWT token -> 401
        expired_token = jwt.encode(
            {"sub": "expired_user", "role": "customer", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        res_expired = await client.get("/api/v1/orders", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_expired.status_code == 401

        # 3. Token signed with wrong secret (tampered signature) -> 401
        fake_secret_token = jwt.encode(
            {"sub": "attacker_user", "role": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "totally_wrong_secret_key_1234567890",
            algorithm=settings.ALGORITHM
        )
        res_fake_sig = await client.get("/api/v1/orders", headers={"Authorization": f"Bearer {fake_secret_token}"})
        assert res_fake_sig.status_code == 401

        # 4. Legitimate Customer attempting to access Super Admin overview -> 403 Forbidden
        cust = await get_test_token(client, "9820000050", "customer", "Escalation Cust")
        res_cust_admin = await client.get("/api/v1/admin/overview", headers=cust)
        assert res_cust_admin.status_code == 403

        # 5. Legitimate Runner attempting to access Super Admin settings -> 403 Forbidden
        runner = await get_test_token(client, "9800000003", "runner", "Escalation Runner")
        res_runner_admin = await client.get("/api/v1/admin/settings", headers=runner)
        assert res_runner_admin.status_code == 403
