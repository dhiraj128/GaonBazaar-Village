import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_full_synthetic_order_lifecycle():
    """
    STRICT VERIFICATION: Complete Synthetic Order Lifecycle across Customer, Vendor, Runner, and Admin.
    Validates:
    - First-time Address Creation with Mandatory Rural Landmark
    - Cart Sync and COD Order Placement
    - Secure Customer Delivery OTP Masking & Reveal Endpoint (GET /orders/{id}/delivery-otp)
    - Strict Multi-User OTP Isolation (Runner, Vendor, and Other Customers get 403 Forbidden)
    - Order Live Tracking with True Runner Telemetry (No Hardcoded Phone, Live Coordinates, Real Timestamps)
    - Runner Location Update (POST /runner/location) recording timestamp
    - Vendor Accept & Pack Lifecycle
    - Runner Accept, Pickup, Out-for-Delivery Lifecycle
    - Invalid OTP Delivery Rejection (HTTP 400)
    - Valid OTP Handover & Cash Collection Confirmation (HTTP 200 -> DELIVERED, PAID)
    - Admin Supervisory Verification
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Customer Authentication (Primary test user 9800000000)
        cust_headers = await issue_and_verify_test_token(client, "9800000000", "customer")

        # 2. First-time Customer Address Creation (Phase 6)
        new_addr_payload = {
            "title": "Home",
            "recipient_name": "Ramesh Kumar",
            "phone": "9800000000",
            "address_line": "House 12, Ward 4, Near Shiv Temple",
            "village": "Rampur Tola",
            "landmark": "Near Panchayat Bhawan and Primary School",
            "latitude": 26.2315,
            "longitude": 85.3610,
            "is_default": True
        }
        addr_resp = await client.post("/api/v1/addresses", headers=cust_headers, json=new_addr_payload)
        assert addr_resp.status_code in [200, 201], f"Address creation failed: {addr_resp.text}"
        addr_data = addr_resp.json()
        address_id = addr_data["id"]
        assert addr_data["village"] == "Rampur Tola"
        assert addr_data["landmark"] == "Near Panchayat Bhawan and Primary School"

        # 3. Product Selection from Authorized Store (Store 1: str_01)
        prods_resp = await client.get("/api/v1/stores/str_01/products")
        assert prods_resp.status_code == 200
        prods = prods_resp.json()
        assert len(prods) > 0
        product = prods[0]
        product_id = product["id"]

        # 4. Cart Sync
        cart_sync = await client.post("/api/v1/cart/sync", json={
            "store_id": "str_01",
            "delivery_latitude": 26.2315,
            "delivery_longitude": 85.3610,
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert cart_sync.status_code == 200
        cart_info = cart_sync.json()
        assert cart_info["is_serviceable"] is True
        assert cart_info["platform_fee"] == 3.0

        # 5. Place COD Order
        order_resp = await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": "str_01",
            "delivery_address_id": address_id,
            "payment_method": "COD",
            "items": [{"product_id": product_id, "quantity": 1}],
            "customer_notes": "Call near Panchayat Bhawan"
        })
        assert order_resp.status_code == 201, f"Order placement failed: {order_resp.text}"
        order_data = order_resp.json()
        order_id = order_data["id"]
        customer_otp = order_data["delivery_otp"]
        assert order_data["status"] == "PLACED"
        assert len(customer_otp) == 4

        # 6. Customer Delivery OTP Reveal Endpoint (GET /orders/{id}/delivery-otp)
        otp_reveal_resp = await client.get(f"/api/v1/orders/{order_id}/delivery-otp", headers=cust_headers)
        assert otp_reveal_resp.status_code == 200
        otp_json = otp_reveal_resp.json()
        assert otp_json["delivery_otp"] == customer_otp

        # 7. Strict Multi-User Security / IDOR Isolation on Delivery OTP
        # A) Other customer must receive 403 Forbidden
        other_cust_headers = await issue_and_verify_test_token(client, "9876543210", "customer")
        blocked_cust = await client.get(f"/api/v1/orders/{order_id}/delivery-otp", headers=other_cust_headers)
        assert blocked_cust.status_code == 403

        # B) Vendor must receive 403 Forbidden
        vendor_headers = await issue_and_verify_test_token(client, "9800000001", "vendor")
        blocked_vendor = await client.get(f"/api/v1/orders/{order_id}/delivery-otp", headers=vendor_headers)
        assert blocked_vendor.status_code == 403

        # C) Runner must receive 403 Forbidden (Delivery partner cannot read OTP in advance!)
        runner_headers = await issue_and_verify_test_token(client, "9800000003", "runner")
        blocked_runner = await client.get(f"/api/v1/orders/{order_id}/delivery-otp", headers=runner_headers)
        assert blocked_runner.status_code == 403

        # 8. Check Initial Live Tracking (Phase 2 & 3)
        tracking_init = await client.get(f"/api/v1/orders/{order_id}/tracking", headers=cust_headers)
        assert tracking_init.status_code == 200
        t_data = tracking_init.json()
        assert t_data["order_id"] == order_id
        assert t_data["destination_landmark"] == "Near Panchayat Bhawan and Primary School"
        assert t_data["destination_village"] == "Rampur Tola"
        assert t_data["store_name"] is not None
        assert t_data["is_live_tracking_active"] is False  # not yet picked up
        assert len(t_data["timeline"]) >= 1

        # 9. Vendor Accepts and Packs Order
        v_accept = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=vendor_headers,
            json={"action": "ACCEPT"}
        )
        assert v_accept.status_code == 200

        v_pack = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=vendor_headers,
            json={"action": "PACKED"}
        )
        assert v_pack.status_code == 200

        # 10. Runner Location Telemetry Update (Phase 3)
        loc_resp = await client.post(
            "/api/v1/runner/location",
            headers=runner_headers,
            json={"latitude": 26.2340, "longitude": 85.3620}
        )
        assert loc_resp.status_code == 200
        loc_data = loc_resp.json()
        assert loc_data["latitude"] == 26.2340
        assert loc_data["updated_at"] is not None

        # 11. Runner Accepts and Picks Up Order
        r_accept = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "ACCEPT"}
        )
        assert r_accept.status_code == 200

        r_pickup = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "PICKUP"}
        )
        assert r_pickup.status_code == 200

        # 11b. Runner goes Out For Delivery
        r_out = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "OUT_FOR_DELIVERY"}
        )
        assert r_out.status_code == 200

        # 12. Check Active Live Tracking
        tracking_live = await client.get(f"/api/v1/orders/{order_id}/tracking", headers=cust_headers)
        assert tracking_live.status_code == 200
        live_data = tracking_live.json()
        assert live_data["is_live_tracking_active"] is True
        assert live_data["runner_latitude"] == 26.2340
        assert live_data["runner_longitude"] == 85.3620
        assert live_data["last_location_updated_at"] is not None
        assert live_data["runner_phone"] == "9800000003"  # Real runner phone, not 9876543210!

        # 13. Runner Attempts Delivery with Wrong OTP -> MUST FAIL (HTTP 400)
        r_bad_delivery = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "DELIVER", "delivery_otp": "9999", "cash_collected": True}
        )
        assert r_bad_delivery.status_code == 400
        assert "otp" in r_bad_delivery.text.lower() or "invalid" in r_bad_delivery.text.lower()

        # 14. Runner Delivers with Genuine Customer OTP -> SUCCEEDS (HTTP 200)
        r_good_delivery = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "DELIVER", "delivery_otp": customer_otp, "cash_collected": True}
        )
        assert r_good_delivery.status_code == 200

        # 15. Final Verification of Completed Order
        order_final = await client.get(f"/api/v1/orders/{order_id}", headers=cust_headers)
        assert order_final.status_code == 200
        final_info = order_final.json()
        assert final_info["status"] == "DELIVERED"
        assert final_info["payment_status"] == "PAID"
        assert len(final_info["timeline"]) >= 5

        # 16. Admin God Mode Verification
        admin_headers = await issue_and_verify_test_token(client, "9800000099", "admin")
        admin_otp = await client.get(f"/api/v1/orders/{order_id}/delivery-otp", headers=admin_headers)
        assert admin_otp.status_code == 200
        assert admin_otp.json()["delivery_otp"] == customer_otp
