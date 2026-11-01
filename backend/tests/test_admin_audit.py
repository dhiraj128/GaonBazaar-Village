import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_admin_settings_dynamic_update_and_audit():
    """Verify admin can dynamically update platform fee and radius, and verify audit log."""
    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        try:
            # 1. Update settings with Admin Key
            update_res = await client.patch("/api/v1/admin/settings", headers=adm_headers, json={
                "platform_fee": 5.0,
                "max_delivery_radius_km": 10.0,
                "vendor_commission_pct": 0.0
            })
            assert update_res.status_code == 200
            data = update_res.json()
            assert data["platform_fee"] == 5.0
            assert data["max_delivery_radius_km"] == 10.0

            # 2. Verify audit logs record this
            audit_res = await client.get("/api/v1/admin/audit-logs", headers=adm_headers)
            assert audit_res.status_code == 200
            logs = audit_res.json()
            assert len(logs) > 0
            actions = [l["action"] for l in logs]
            assert "SETTINGS_UPDATED" in actions
        finally:
            # Always restore rural invariants
            settings.PLATFORM_FEE = 3.0
            settings.MAX_DELIVERY_RADIUS_KM = 8.0
            settings.DEFAULT_VENDOR_COMMISSION_PCT = 0.0


@pytest.mark.asyncio
async def test_admin_customer_management_and_tickets():
    """Verify admin customer listing, support tickets flow, and resolution."""
    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a customer and ticket
        c_headers = await issue_and_verify_test_token(client, "9700011122", "customer")

        # Verify customer appears in admin customer list
        cust_res = await client.get("/api/v1/admin/customers", headers=adm_headers)
        assert cust_res.status_code == 200
        customers = cust_res.json()
        phones = [c["phone"] for c in customers]
        assert "9700011122" in phones

        # Create support ticket
        t_res = await client.post("/api/v1/orders/tickets", headers=c_headers, json={
            "subject": "Delay in delivery",
            "message": "Runner is arriving 10 minutes late in Sivay Patti"
        })
        assert t_res.status_code == 200
        ticket_id = t_res.json()["id"]

        # Admin lists tickets
        all_t_res = await client.get("/api/v1/admin/tickets", headers=adm_headers)
        assert all_t_res.status_code == 200
        tickets = all_t_res.json()
        t_ids = [t["id"] for t in tickets]
        assert ticket_id in t_ids

        # Admin updates ticket to RESOLVED
        up_res = await client.patch(f"/api/v1/admin/tickets/{ticket_id}", headers=adm_headers, json={"status": "RESOLVED"})
        assert up_res.status_code == 200
        assert up_res.json()["status"] == "RESOLVED"

@pytest.mark.asyncio
async def test_admin_vendor_and_runner_approval_flow():
    """Verify admin can approve/reject vendors and runners."""
    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Onboard unapproved vendor
        v_headers = await issue_and_verify_test_token(client, "9611122233", "vendor")

        s_res = await client.post("/api/v1/stores/onboard", headers=v_headers, json={
            "shop_name": "Audit Test Kirana",
            "owner_name": "Ramesh Kumar",
            "category": "Grocery",
            "latitude": 26.1950,
            "longitude": 85.3450,
            "village": "Chaturshi"
        })
        store_id = s_res.json()["id"]

        # 2. Admin approves vendor
        appr_res = await client.post(f"/api/v1/admin/vendors/{store_id}/approve", headers=adm_headers)
        assert appr_res.status_code == 200
        assert appr_res.json()["is_approved"] is True

        # 3. Admin rejects/deactivates vendor
        rej_res = await client.post(f"/api/v1/admin/vendors/{store_id}/reject", headers=adm_headers)
        assert rej_res.status_code == 200
        assert rej_res.json()["is_approved"] is False
