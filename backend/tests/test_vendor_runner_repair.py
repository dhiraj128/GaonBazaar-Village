import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_vendor_and_runner_endpoints_and_actions():
    ts = int(time.time() * 100) % 100000000
    vendor_phone = f"98{ts:08d}"
    runner_phone = f"96{ts:08d}"
    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register Vendor
        v_headers = await issue_and_verify_test_token(client, vendor_phone, "vendor")

        # 2. Onboard Store
        store_res = await client.post("/api/v1/stores/onboard", headers=v_headers, json={
            "shop_name": "Minapur Sharda Kirana",
            "owner_name": "Raju Sharma",
            "category": "Grocery",
            "latitude": 26.2230,
            "longitude": 85.3520,
            "village": "Chaturshi",
            "landmark": "Near Panchayat Bhavan",
            "block": "Minapur",
            "district": "Muzaffarpur",
            "upi_id": "raju.sharma@upi"
        })
        assert store_res.status_code == 200
        store = store_res.json()
        store_id = store["id"]
        assert store["is_approved"] is False

        # 3. GET /stores/me returns vendor store
        me_res = await client.get("/api/v1/stores/me", headers=v_headers)
        assert me_res.status_code == 200
        assert me_res.json()["shop_name"] == "Minapur Sharda Kirana"
        assert me_res.json()["is_approved"] is False

        # 4. Attempt to go online before approval fails
        online_fail = await client.patch("/api/v1/stores/status", headers=v_headers, json={"is_online": True})
        assert online_fail.status_code == 400

        # 5. Admin approves Store
        app_res = await client.post(f"/api/v1/admin/vendors/{store_id}/approve", headers=adm_headers)
        assert app_res.status_code == 200

        # 6. Now going online succeeds
        online_succ = await client.patch("/api/v1/stores/status", headers=v_headers, json={"is_online": True})
        assert online_succ.status_code == 200
        assert online_succ.json()["is_online"] is True

        # 7. Add product to store
        p_res = await client.post("/api/v1/vendor/products", headers=v_headers, json={
            "custom_name_en": "Chakki Atta",
            "custom_name_hi": "ताज़ा चक्की आटा",
            "category": "Grocery",
            "unit": "1 kg",
            "price": 38.0,
            "stock_quantity": 40,
            "in_stock": True
        })
        assert p_res.status_code == 200
        prod = p_res.json()
        prod_id = prod["id"]

        # 8. Update product stock via PATCH
        stock_patch = await client.patch(f"/api/v1/stores/products/{prod_id}/stock", headers=v_headers, json={
            "in_stock": False,
            "stock_quantity": 0,
            "price": 40.0
        })
        assert stock_patch.status_code == 200
        assert stock_patch.json()["in_stock"] is False
        assert stock_patch.json()["price"] == 40.0

        # 9. Register Runner
        r_headers = await issue_and_verify_test_token(client, runner_phone, "runner")

        # 10. GET /runner/me returns runner profile (pending approval)
        r_me = await client.get("/api/v1/runner/me", headers=r_headers)
        assert r_me.status_code == 200
        assert r_me.json()["is_approved"] is False
        r_id = r_me.json()["id"]

        # 11. Runner cannot go online before approval
        r_online_fail = await client.patch("/api/v1/runner/status", headers=r_headers, json={"is_online": True})
        assert r_online_fail.status_code == 400

        # 12. Admin approves runner
        r_app = await client.post(f"/api/v1/admin/runners/{r_id}/approve", headers=adm_headers)
        assert r_app.status_code == 200

        # 13. Runner can now go online
        r_online_succ = await client.patch("/api/v1/runner/status", headers=r_headers, json={"is_online": True})
        assert r_online_succ.status_code == 200
        assert r_online_succ.json()["is_online"] is True
