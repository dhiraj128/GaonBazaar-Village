import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_full_cross_platform_lifecycle():
    ts = int(time.time() * 100) % 100000000
    vendor_phone = f"98{ts:08d}"
    customer_phone = f"97{ts:08d}"
    runner_phone = f"96{ts:08d}"
    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Vendor Authentication & Onboarding
        vendor_headers = await issue_and_verify_test_token(client, vendor_phone, "vendor")

        onboard_store_res = await client.post(
            "/api/v1/stores/onboard",
            headers=vendor_headers,
            json={
                "shop_name": "Minapur Kisan Kirana",
                "owner_name": "Raju Prasad",
                "category": "Grocery",
                "latitude": 26.2230,
                "longitude": 85.3520,
                "village": "Chaturshi",
                "block": "Minapur",
                "district": "Muzaffarpur",
                "upi_id": "raju.kisan@upi"
            }
        )
        assert onboard_store_res.status_code == 200
        store_data = onboard_store_res.json()
        store_id = store_data["id"]
        assert store_data["is_approved"] is False

        # Attempt to go online before approval must fail
        online_fail = await client.patch(
            "/api/v1/stores/status",
            headers=vendor_headers,
            json={"is_online": True}
        )
        assert online_fail.status_code == 400

        # 2. Admin Approves Vendor Store
        admin_approve_store = await client.post(f"/api/v1/admin/vendors/{store_id}/approve", headers=adm_headers)
        assert admin_approve_store.status_code == 200

        # Now Vendor can go online
        online_ok = await client.patch(
            "/api/v1/stores/status",
            headers=vendor_headers,
            json={"is_online": True}
        )
        assert online_ok.status_code == 200
        assert online_ok.json()["is_online"] is True

        # Add a product to the store
        prod_res = await client.post(
            "/api/v1/vendor/products",
            headers=vendor_headers,
            json={
                "name_en": "Chakki Fresh Atta 5kg",
                "name_hi": "चक्की फ्रेश आटा 5 किलो",
                "category": "Atta & Flour",
                "unit": "5 kg",
                "price": 175.0,
                "mrp": 195.0,
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500",
                "in_stock": True,
                "stock_quantity": 40
            }
        )
        assert prod_res.status_code == 200
        product_id = prod_res.json()["id"]

        # 3. Customer Authentication & Address Setup
        cust_headers = await issue_and_verify_test_token(client, customer_phone, "customer")

        addr_res = await client.post(
            "/api/v1/addresses",
            headers=cust_headers,
            json={
                "recipient_name": "Sunil Kumar",
                "phone": customer_phone,
                "village": "Chaturshi",
                "block": "Minapur",
                "district": "Muzaffarpur",
                "state": "Bihar",
                "latitude": 26.2240,
                "longitude": 85.3530,
                "is_default": True
            }
        )
        assert addr_res.status_code == 201
        address_id = addr_res.json()["id"]

        # Customer Places Order
        order_res = await client.post(
            "/api/v1/orders",
            headers=cust_headers,
            json={
                "store_id": store_id,
                "delivery_address_id": address_id,
                "payment_method": "COD",
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": 1
                    }
                ]
            }
        )
        assert order_res.status_code == 201
        order_data = order_res.json()
        order_id = order_data["id"]
        delivery_otp = order_data["delivery_otp"]
        assert order_data["status"] == "PLACED"

        # 4. Vendor accepts and packs order
        accept_res = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=vendor_headers,
            json={"action": "ACCEPT"}
        )
        assert accept_res.status_code == 200
        assert accept_res.json()["status"] == "ACCEPTED"

        pack_res = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=vendor_headers,
            json={"action": "PACK"}
        )
        assert pack_res.status_code == 200
        assert pack_res.json()["status"] == "PACKED"

        # 5. Runner Authentication & Onboarding
        runner_headers = await issue_and_verify_test_token(client, runner_phone, "runner")

        onboard_runner_res = await client.post(
            "/api/v1/runner/onboard",
            headers=runner_headers,
            json={
                "full_name": "Dinesh Paswan",
                "vehicle_type": "Motorcycle",
                "vehicle_number": "BR-06-CD-9988",
                "driving_licence_no": "DL-062024112233",
                "upi_id": "dinesh.runner@upi"
            }
        )
        assert onboard_runner_res.status_code == 200
        runner_id = onboard_runner_res.json()["id"]
        assert onboard_runner_res.json()["is_approved"] is False

        # Super Admin approves Runner
        admin_approve_runner = await client.post(f"/api/v1/admin/runners/{runner_id}/approve", headers=adm_headers)
        assert admin_approve_runner.status_code == 200

        # Runner goes Online
        runner_duty = await client.patch(
            "/api/v1/runner/status",
            headers=runner_headers,
            json={"is_online": True}
        )
        assert runner_duty.status_code == 200
        assert runner_duty.json()["is_online"] is True

        # 6. Runner accepts, picks up, out for delivery, and delivers
        accept_job_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "ACCEPT"}
        )
        assert accept_job_res.status_code == 200
        assert accept_job_res.json()["status"] == "RUNNER_ASSIGNED"

        pickup_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "PICKUP"}
        )
        assert pickup_res.status_code == 200
        assert pickup_res.json()["status"] == "PICKED_UP"

        out_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "OUT_FOR_DELIVERY"}
        )
        assert out_res.status_code == 200
        assert out_res.json()["status"] == "OUT_FOR_DELIVERY"

        # Invalid OTP must fail with 400
        bad_otp_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "DELIVER", "delivery_otp": "0000"}
        )
        assert bad_otp_res.status_code == 400

        # Correct OTP succeeds with verified cash collection
        deliver_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={"action": "DELIVER", "delivery_otp": delivery_otp, "cash_collected": True}
        )
        assert deliver_res.status_code == 200
        assert deliver_res.json()["status"] == "DELIVERED"

        # 7. Check Vendor Finances
        vendor_fin_res = await client.get("/api/v1/vendor/finances", headers=vendor_headers)
        assert vendor_fin_res.status_code == 200
        fin_data = vendor_fin_res.json()
        assert fin_data["commission_rate"] == 0.0
        assert fin_data["total_sales"] >= 175.0
        assert fin_data["net_payout_due"] >= 175.0

        # 8. Check Runner Finances
        runner_fin_res = await client.get("/api/v1/runner/finances", headers=runner_headers)
        assert runner_fin_res.status_code == 200
        r_fin = runner_fin_res.json()
        assert r_fin["total_deliveries_count"] >= 1
        assert r_fin["total_delivery_earnings"] >= 15.0

        # 9. Super Admin Overview
        admin_overview_res = await client.get("/api/v1/admin/overview", headers=adm_headers)
        assert admin_overview_res.status_code == 200
        overview = admin_overview_res.json()
        assert "Minapur" in overview["pilot_area"]
        assert overview["max_delivery_radius_km"] == 8.0
        assert overview["vendor_commission_pct"] == 0.0
