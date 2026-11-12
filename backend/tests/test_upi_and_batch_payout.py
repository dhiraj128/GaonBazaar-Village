import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.base import User, Store, Address, Order, OrderTimeline, Runner
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_direct_upi_intent_flow_and_verification():
    """Verify Direct UPI intent marks PENDING_VERIFICATION and UTR submission confirms PAID."""
    import secrets
    settings.TESTING = True

    c_phone = f"98{secrets.randbelow(89999999) + 10000000}"
    v_phone = f"97{secrets.randbelow(89999999) + 10000000}"

    async with AsyncSessionLocal() as session:
        # Create test customer, vendor, store, address, order
        now = datetime.now(timezone.utc)
        cust = User(phone=c_phone, name="Test Customer", role="customer")
        vendor = User(phone=v_phone, name="Test Vendor", role="vendor")
        session.add_all([cust, vendor])
        await session.flush()

        store = Store(
            owner_id=vendor.id,
            shop_name="UPI Kirana Store",
            owner_name="Test Vendor",
            category="Grocery",
            village="Chaturshi",
            latitude=26.23,
            longitude=85.36,
            is_approved=True
        )
        session.add(store)
        await session.flush()

        addr = Address(
            user_id=cust.id,
            title="Home",
            recipient_name="Test Customer",
            phone=c_phone,
            village="Chaturshi",
            latitude=26.23,
            longitude=85.36
        )
        session.add(addr)
        await session.flush()

        order = Order(
            customer_id=cust.id,
            store_id=store.id,
            vendor_id=vendor.id,
            delivery_address_id=addr.id,
            subtotal=250.0,
            delivery_fee=20.0,
            platform_fee=3.0,
            total_amount=273.0,
            payment_method="UPI",
            payment_status="PENDING",
            delivery_otp="4321",
            cancel_until=now + timedelta(seconds=180)
        )
        session.add(order)
        await session.commit()
        order_id = order.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Step 1: Customer opens UPI Intent (No UTR yet) -> status should be PENDING_VERIFICATION
        init_res = await client.post("/api/v1/payments/verify-upi", json={
            "order_id": order_id,
            "upi_app": "gpay",
            "amount": 273.0
        })
        assert init_res.status_code == 200
        init_data = init_res.json()
        assert init_data["status"] == "PENDING_VERIFICATION"
        assert init_data["payment_status"] == "PENDING_VERIFICATION"

        # 2. Check pollable status endpoint
        poll_res = await client.get(f"/api/v1/payments/upi-status/{order_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        assert poll_data["payment_status"] == "PENDING_VERIFICATION"
        assert poll_data["amount"] == 273.0

        # 3. Step 2: Customer enters 12-digit UTR from GPay -> status transitions to PAID
        utr_res = await client.post("/api/v1/payments/verify-upi", json={
            "order_id": order_id,
            "utr_number": "431829103842",
            "upi_app": "gpay",
            "amount": 273.0
        })
        assert utr_res.status_code == 200
        utr_data = utr_res.json()
        assert utr_data["status"] == "SUCCESS"
        assert utr_data["payment_status"] == "PAID"
        assert utr_data["utr_number"] == "431829103842"

        # 4. Check status again -> PAID
        final_poll = await client.get(f"/api/v1/payments/upi-status/{order_id}")
        assert final_poll.status_code == 200
        assert final_poll.json()["payment_status"] == "PAID"
        assert final_poll.json()["transaction_id"] == "431829103842"


@pytest.mark.asyncio
async def test_weekly_batch_payout_execution():
    """Verify Super Admin weekly batch payout endpoint calculates and settles verified accounts."""
    settings.TESTING = True

    admin_token = create_access_token(
        data={"sub": "usr_superadmin", "phone": "9800000099", "role": "super_admin"},
        expires_delta=timedelta(hours=2)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/admin/settlements/process-weekly-batch",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "batch_id" in data
        assert "settled_vendors" in data
        assert "settled_runners" in data
        assert "total_settled_amount" in data
