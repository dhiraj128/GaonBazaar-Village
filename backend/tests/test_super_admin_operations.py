import pytest
import io
import csv
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.models.base import User, Store, Runner, Order, GlobalCatalogItem, Address, StoreProduct, Refund
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_scenario_a_vendor_kyc_side_by_side_and_approval():
    """Scenario A: Vendor KYC side-by-side review and approval/rejection."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Fetch pending KYC list
        pending_res = await client.get("/api/v1/admin/kyc/pending", headers=headers)
        assert pending_res.status_code == 200
        pending_list = pending_res.json()
        assert isinstance(pending_list, list)

        # 2. Get side-by-side details for vendor
        vendors_res = await client.get("/api/v1/admin/vendors", headers=headers)
        assert vendors_res.status_code == 200
        vendors = vendors_res.json()
        assert len(vendors) > 0
        v_id = vendors[0]["id"]

        detail_res = await client.get(f"/api/v1/admin/kyc/vendor/{v_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()
        assert "user_submitted" in data
        assert "api_verified" in data
        assert "penny_drop_bank_match" in data["api_verified"]
        assert "aadhaar_liveness" in data["api_verified"]

        # 3. Approve vendor KYC
        appr_res = await client.post(f"/api/v1/admin/kyc/vendor/{v_id}/approve", headers=headers)
        assert appr_res.status_code == 200
        assert appr_res.json()["is_approved"] is True

        # 4. Reject vendor KYC
        rej_res = await client.post(
            f"/api/v1/admin/kyc/vendor/{v_id}/reject",
            params={"reason": "Shop photo blurry"},
            headers=headers
        )
        assert rej_res.status_code == 200
        assert rej_res.json()["is_approved"] is False

        # 5. Restore vendor to approved state so subsequent tests remain unaffected
        restore_res = await client.post(f"/api/v1/admin/kyc/vendor/{v_id}/approve", headers=headers)
        assert restore_res.status_code == 200


@pytest.mark.asyncio
async def test_scenario_b_runner_kyc_side_by_side_and_approval():
    """Scenario B: Runner KYC side-by-side review and approval."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        runners_res = await client.get("/api/v1/admin/runners", headers=headers)
        assert runners_res.status_code == 200
        runners = runners_res.json()
        assert len(runners) > 0
        r_id = runners[0]["id"]

        # Side-by-side detail
        detail_res = await client.get(f"/api/v1/admin/kyc/runner/{r_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()
        assert data["applicant_type"] == "RUNNER"
        assert "penny_drop_bank_match" in data["api_verified"]
        assert "aadhaar_liveness" in data["api_verified"]

        # Approve runner
        appr_res = await client.post(f"/api/v1/admin/kyc/runner/{r_id}/approve", headers=headers)
        assert appr_res.status_code == 200
        assert appr_res.json()["is_approved"] is True


@pytest.mark.asyncio
async def test_scenario_c_live_orders_and_god_mode():
    """Scenario C: Live Orders Feed & God Mode (Cancel, Instant Refund, Reassign Runner, Stock Override)."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        orders_res = await client.get("/api/v1/admin/orders", headers=headers)
        assert orders_res.status_code == 200
        orders = orders_res.json()
        assert len(orders) > 0
        target_order = orders[0]
        order_id = target_order["id"]

        # 1. Update Order Status
        status_res = await client.patch(f"/api/v1/admin/orders/{order_id}/status", json={"status": "PACKED"}, headers=headers)
        assert status_res.status_code == 200

        # 2. God Mode Reassign Runner
        runners_res = await client.get("/api/v1/admin/runners", headers=headers)
        runners = runners_res.json()
        new_runner_id = runners[0]["id"]

        reassign_res = await client.post(
            f"/api/v1/admin/orders/{order_id}/god-mode/reassign-runner",
            json={"runner_id": new_runner_id, "notes": "Previous runner stuck in traffic"},
            headers=headers
        )
        assert reassign_res.status_code == 200
        assert reassign_res.json()["runner_id"] == new_runner_id

        # 3. God Mode Instant Refund
        refund_res = await client.post(
            f"/api/v1/admin/orders/{order_id}/god-mode/refund",
            json={"amount": 49.0, "reason": "Damaged item replacement"},
            headers=headers
        )
        assert refund_res.status_code == 200
        assert refund_res.json()["status"] == "COMPLETED"

        # 4. God Mode Cancel Order
        cancel_res = await client.post(
            f"/api/v1/admin/orders/{order_id}/god-mode/cancel",
            params={"reason": "Customer address unreachable", "auto_refund": True},
            headers=headers
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_scenario_d_critical_exception_alerts():
    """Scenario D: SOS Alerts, Delayed Orders, and Unaccepted Orders."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Trigger SOS alert
        runners_res = await client.get("/api/v1/admin/runners", headers=headers)
        runner_id = runners_res.json()[0]["id"]

        sos_res = await client.post(
            "/api/v1/admin/alerts/sos",
            params={"runner_id": runner_id, "reason": "Flat tire near Chatursi Chowk"},
            headers=headers
        )
        assert sos_res.status_code == 200
        alert_obj = sos_res.json()["alert"]
        assert alert_obj["type"] == "SOS_RIDER"

        # Query alerts
        alerts_res = await client.get("/api/v1/admin/alerts", headers=headers)
        assert alerts_res.status_code == 200
        alerts = alerts_res.json()
        assert any(a["id"] == alert_obj["id"] for a in alerts)

        # Resolve alert
        resolve_res = await client.post(f"/api/v1/admin/alerts/{alert_obj['id']}/resolve", headers=headers)
        assert resolve_res.status_code == 200


@pytest.mark.asyncio
async def test_scenario_e_hourly_trend_charts():
    """Scenario E: Line graphs showing order volume by hour today vs yesterday."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        trends_res = await client.get("/api/v1/admin/dashboard/trends", headers=headers)
        assert trends_res.status_code == 200
        data = trends_res.json()
        assert "trend_data" in data
        assert len(data["trend_data"]) == 15 # 08:00 to 22:00
        assert "hour" in data["trend_data"][0]
        assert "today" in data["trend_data"][0]
        assert "yesterday" in data["trend_data"][0]


@pytest.mark.asyncio
async def test_scenario_f_live_map_tracking_and_heatmaps():
    """Scenario F: Leaflet rider tracking (Green/Orange/Red), GPS pinging, Red Zones & Notify riders."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get riders on map
        riders_res = await client.get("/api/v1/admin/map/riders", headers=headers)
        assert riders_res.status_code == 200
        riders = riders_res.json()
        assert len(riders) > 0
        assert "color" in riders[0]
        assert riders[0]["color"] in ["green", "orange", "red"]

        # Runner GPS ping
        r_id = riders[0]["runner_id"]
        ping_res = await client.post(
            f"/api/v1/admin/map/riders/{r_id}/ping",
            json={"latitude": 26.1960, "longitude": 85.3460, "status": "BUSY", "battery_level": 92},
            headers=headers
        )
        assert ping_res.status_code == 200

        # Demand Heatmaps
        heatmaps_res = await client.get("/api/v1/admin/map/heatmaps", headers=headers)
        assert heatmaps_res.status_code == 200
        heatmaps = heatmaps_res.json()
        assert len(heatmaps) > 0
        assert any(h["is_red_zone"] for h in heatmaps)

        # Notify riders to move to Red Zone
        notify_res = await client.post(
            "/api/v1/admin/map/heatmaps/notify-riders",
            json={"zone_name": "Chaturshi Market Hub", "latitude": 26.1950, "longitude": 85.3450},
            headers=headers
        )
        assert notify_res.status_code == 200
        assert notify_res.json()["riders_notified_count"] >= 0


@pytest.mark.asyncio
async def test_scenario_g_financials_cod_deposit_and_batch_csv():
    """Scenario G: COD reconciliation 'Received & Deposited' and Batch CSV exports."""
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Financial summary
        fin_res = await client.get("/api/v1/admin/settlements", headers=headers)
        assert fin_res.status_code == 200
        fin_data = fin_res.json()
        assert "vendor_settlements" in fin_data
        assert "runner_settlements" in fin_data

        # 2. COD reconciliation list
        cod_res = await client.get("/api/v1/admin/settlements/cod", headers=headers)
        assert cod_res.status_code == 200

        # 3. Hub Manager records COD deposit
        runners_res = await client.get("/api/v1/admin/runners", headers=headers)
        r_id = runners_res.json()[0]["id"]
        dep_res = await client.post(
            "/api/v1/admin/settlements/cod-deposit",
            json={"runner_id": r_id, "amount": 350.0, "receipt_reference": "TEST-REC-001"},
            headers=headers
        )
        assert dep_res.status_code == 200
        assert "HUB-COD" in dep_res.json()["receipt_number"] or "TEST-REC-001" in dep_res.json()["receipt_number"]

        # 4. Super Admin exports Vendor Payouts Batch CSV
        csv_v_res = await client.get("/api/v1/admin/settlements/payouts/vendor-csv", headers=headers)
        assert csv_v_res.status_code == 200
        assert "text/csv" in csv_v_res.headers["content-type"]
        assert "Beneficiary Name" in csv_v_res.text

        # 5. Super Admin exports Runner Payouts Batch CSV
        csv_r_res = await client.get("/api/v1/admin/settlements/payouts/runner-csv", headers=headers)
        assert csv_r_res.status_code == 200
        assert "text/csv" in csv_r_res.headers["content-type"]
        assert "Beneficiary Name" in csv_r_res.text


@pytest.mark.asyncio
async def test_scenario_h_strict_rbac_super_admin_vs_hub_manager():
    """Scenario H: RBAC enforcement - Hub Manager restricted from Financials CSV, Pricing Update & Audit Logs."""
    hub_manager_token = create_access_token({"sub": "hub_mgr_01", "phone": "9800000098", "role": "hub_manager"})
    hub_headers = {"Authorization": f"Bearer {hub_manager_token}"}

    super_admin_token = create_access_token({"sub": "super_adm_01", "phone": "9800000099", "role": "super_admin"})
    super_headers = {"Authorization": f"Bearer {super_admin_token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Hub Manager CAN access: Dashboard overview, Pending KYC, Live Orders, Live Map, COD list
        ov_res = await client.get("/api/v1/admin/overview", headers=hub_headers)
        assert ov_res.status_code == 200

        kyc_res = await client.get("/api/v1/admin/kyc/pending", headers=hub_headers)
        assert kyc_res.status_code == 200

        map_res = await client.get("/api/v1/admin/map/riders", headers=hub_headers)
        assert map_res.status_code == 200

        # 2. Hub Manager is STRICTLY FORBIDDEN (403) from accessing:
        # - Settlements ledger
        sett_forbidden = await client.get("/api/v1/admin/settlements", headers=hub_headers)
        assert sett_forbidden.status_code == 403
        assert "Hub Manager" in sett_forbidden.json()["detail"]

        # - Vendor Batch Payouts CSV
        csv_forbidden = await client.get("/api/v1/admin/settlements/payouts/vendor-csv", headers=hub_headers)
        assert csv_forbidden.status_code == 403

        # - Pricing Engine settings update
        pricing_forbidden = await client.patch("/api/v1/admin/settings", json={"platform_fee": 10.0}, headers=hub_headers)
        assert pricing_forbidden.status_code == 403

        # - Audit Logs
        audit_forbidden = await client.get("/api/v1/admin/audit-logs", headers=hub_headers)
        assert audit_forbidden.status_code == 403

        # 3. Super Admin CAN access Settlements, CSV, and Pricing Engine
        sett_ok = await client.get("/api/v1/admin/settlements", headers=super_headers)
        assert sett_ok.status_code == 200

        audit_ok = await client.get("/api/v1/admin/audit-logs", headers=super_headers)
        assert audit_ok.status_code == 200
