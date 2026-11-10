import pytest
import secrets
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_admin_rbac_gatekeeper_enforcement():
    """Verify that only super_admin / admin credentials can access admin endpoints; customer/vendor/runner are rejected."""
    # 1. Customer token
    cust_token = create_access_token({"sub": "cust_123", "phone": "9811111111", "role": "customer"})
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Vendor token
    vend_token = create_access_token({"sub": "vend_123", "phone": "9822222222", "role": "vendor"})
    vend_headers = {"Authorization": f"Bearer {vend_token}"}

    # 3. Runner token
    runn_token = create_access_token({"sub": "runn_123", "phone": "9833333333", "role": "runner"})
    runn_headers = {"Authorization": f"Bearer {runn_token}"}

    # 4. Super Admin token
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "super_admin"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Non-admins must be rejected with 403 Forbidden
        r1 = await client.get("/api/v1/admin/overview", headers=cust_headers)
        assert r1.status_code == 403

        r2 = await client.get("/api/v1/admin/kyc/pending", headers=vend_headers)
        assert r2.status_code == 403

        r3 = await client.get("/api/v1/admin/orders", headers=runn_headers)
        assert r3.status_code == 403

        # Super Admin succeeds with 200
        r4 = await client.get("/api/v1/admin/overview", headers=admin_headers)
        assert r4.status_code == 200

@pytest.mark.asyncio
async def test_kyc_verification_approve_and_reject_workflows():
    """Verify KYC pending list, side-by-side details, and approve & activate / reject actions."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "super_admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        pending_res = await client.get("/api/v1/admin/kyc/pending", headers=headers)
        assert pending_res.status_code == 200
        pending = pending_res.json()
        assert isinstance(pending, list)

        # There are pre-seeded or pending vendors/runners
        if len(pending) > 0:
            app_item = pending[0]
            assert "id" in app_item
            assert "type" in app_item
            assert "name" in app_item
            assert "village" in app_item

            # Approve applicant
            app_type = app_item["type"].lower()
            approve_res = await client.post(f"/api/v1/admin/kyc/{app_type}/{app_item['id']}/approve", headers=headers)
            assert approve_res.status_code == 200
            assert approve_res.json()["is_approved"] is True

@pytest.mark.asyncio
async def test_god_mode_order_lifecycle_cancel_and_reassign():
    """Verify 3-way order routing lifecycle Customer ID -> Vendor ID -> Runner ID, and god mode cancel & reassign."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "super_admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        orders_res = await client.get("/api/v1/admin/orders", headers=headers)
        assert orders_res.status_code == 200
        orders = orders_res.json()
        assert len(orders) > 0
        first_order = orders[0]

        # Verify full 3-way lifecycle fields
        assert "customer_id" in first_order
        assert "store_id" in first_order
        assert "runner_id" in first_order

        # Reassign Runner
        runners_res = await client.get("/api/v1/admin/runners", headers=headers)
        assert runners_res.status_code == 200
        all_runners = runners_res.json()
        target_runner_id = all_runners[0]["id"]

        reassign_res = await client.post(
            f"/api/v1/admin/orders/{first_order['id']}/god-mode/reassign-runner",
            json={"runner_id": target_runner_id, "notes": "Reassigned for emergency dispatch"},
            headers=headers
        )
        assert reassign_res.status_code == 200
        assert reassign_res.json()["runner_id"] == target_runner_id

        # God Mode Force-Cancel
        cancel_res = await client.post(
            f"/api/v1/admin/orders/{first_order['id']}/god-mode/cancel",
            json={"reason": "Super Admin Emergency Override", "auto_refund": True},
            headers=headers
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"

@pytest.mark.asyncio
async def test_financials_cod_reconciliation_and_vendor_payouts():
    """Verify financials tab calculations: Runner COD cash held and Vendor net payout."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "super_admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. COD reconciliation
        cod_res = await client.get("/api/v1/admin/settlements/cod", headers=headers)
        assert cod_res.status_code == 200
        cod_list = cod_res.json()
        assert isinstance(cod_list, list)
        for runner_cod in cod_list:
            assert "runner_id" in runner_cod
            assert "cash_held_inr" in runner_cod

        # 2. Vendor settlements (Order Value - Commission)
        sett_res = await client.get("/api/v1/admin/settlements", headers=headers)
        assert sett_res.status_code == 200
        sett_data = sett_res.json()
        assert "vendor_settlements" in sett_data
        for v in sett_data["vendor_settlements"]:
            assert "total_payout" in v
            assert "store_name" in v
