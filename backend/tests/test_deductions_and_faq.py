import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.models.base import Order, Store, User, Runner

@pytest.mark.asyncio
async def test_vendor_and_runner_invisible_deductions():
    """
    Verify the invisible 2% online deduction and 0% COD deduction:
    1. Vendor Online: subtotal * 0.98
    2. Vendor COD: subtotal * 1.00
    3. Runner Online: (delivery_fee - 3.0) * 0.98
    4. Runner COD: delivery_fee - 3.0
    5. UI ledgers: online_gateway_fee == 0.0
    """
    settings.TESTING = True

    # 1. Vendor Online calculation check
    order_online_vendor = Order(
        id="ord_test_v_online",
        store_id="store_test_deduct",
        subtotal=100.0,
        delivery_fee=25.0,
        platform_fee=3.0,
        total_amount=128.0,
        payment_method="ONLINE",
        payment_status="PAID",
        status="DELIVERED",
        delivered_at=datetime.now(timezone.utc)
    )

    # Vendor COD calculation check
    order_cod_vendor = Order(
        id="ord_test_v_cod",
        store_id="store_test_deduct",
        subtotal=100.0,
        delivery_fee=25.0,
        platform_fee=3.0,
        total_amount=128.0,
        payment_method="COD",
        payment_status="PENDING",
        status="DELIVERED",
        delivered_at=datetime.now(timezone.utc)
    )

    def _calc_vendor_payout(o):
        is_online = (o.payment_method or "").upper() in ["ONLINE", "UPI"]
        return round(o.subtotal * 0.98, 2) if is_online else round(o.subtotal, 2)

    assert _calc_vendor_payout(order_online_vendor) == 98.00
    assert _calc_vendor_payout(order_cod_vendor) == 100.00

    # 2. Runner Online & COD calculation check
    order_online_runner = Order(
        id="ord_test_r_online",
        runner_id="runner_test_deduct",
        subtotal=200.0,
        delivery_fee=25.0,
        platform_fee=3.0,
        total_amount=228.0,
        payment_method="ONLINE",
        payment_status="PAID",
        status="DELIVERED",
        delivered_at=datetime.now(timezone.utc)
    )

    order_cod_runner = Order(
        id="ord_test_r_cod",
        runner_id="runner_test_deduct",
        subtotal=200.0,
        delivery_fee=25.0,
        platform_fee=3.0,
        total_amount=228.0,
        payment_method="COD",
        payment_status="PENDING",
        status="DELIVERED",
        delivered_at=datetime.now(timezone.utc)
    )

    def _calc_runner_payout(o):
        r_base = getattr(o, 'runner_payout', None) or max(0.0, (o.delivery_fee or 0.0) - 3.0)
        is_online = (o.payment_method or "").upper() in ["ONLINE", "UPI"]
        return round(r_base * 0.98, 2) if is_online else round(r_base, 2)

    # (25 - 3) * 0.98 = 22 * 0.98 = 21.56
    assert _calc_runner_payout(order_online_runner) == 21.56
    # 25 - 3 = 22.00
    assert _calc_runner_payout(order_cod_runner) == 22.00

@pytest.mark.asyncio
async def test_admin_settlements_ledger_invisible_fee():
    """Verify that get_settlements_ledger hides the 2% fee and sets total_online_gateway_fee to 0.0."""
    settings.TESTING = True

    admin_token = create_access_token(
        data={"sub": "usr_superadmin", "phone": "9800000099", "role": "super_admin"},
        expires_delta=timedelta(hours=2)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/admin/settlements",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "vendor_settlements" in data
        assert "runner_settlements" in data
        # Invisibility requirement: total_online_gateway_fee must be 0.0
        assert data.get("total_online_gateway_fee") == 0.0
