import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.base import User, Store, Runner, Address, Order, OrderItem, Refund, Replacement
from app.core.security import create_access_token

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

def unique_phone():
    return f"99{uuid.uuid4().int % 100000000:08d}"

@pytest.mark.asyncio
async def test_full_and_partial_refund_lifecycle(client: AsyncClient, db_session):
    now = datetime.now(timezone.utc)
    tag = uuid.uuid4().hex[:6]
    
    # Setup test customer and store
    cust = User(id=f"usr_rf_{tag}", phone=unique_phone(), name="Refund Test Customer", role="customer")
    vendor_user = User(id=f"usr_vnd_{tag}", phone=unique_phone(), name="Refund Test Vendor", role="vendor")
    store = Store(
        id=f"str_rf_{tag}",
        owner_id=vendor_user.id,
        shop_name="Refund Store",
        owner_name="Refund Owner",
        category="Grocery",
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        is_approved=True
    )
    addr = Address(
        id=f"addr_rf_{tag}",
        user_id=cust.id,
        recipient_name="Refund Customer",
        phone=cust.phone,
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        block="Minapur",
        district="Muzaffarpur",
        is_default=True
    )
    
    order = Order(
        id=f"ord_rf_{tag}",
        customer_id=cust.id,
        store_id=store.id,
        delivery_address_id=addr.id,
        status="DELIVERED",
        subtotal=200.0,
        delivery_fee=15.0,
        platform_fee=3.0,
        total_amount=218.0,
        payment_method="ONLINE",
        payment_status="PAID",
        payment_order_id="order_rzp_mock_ref",
        transaction_id="pay_rzp_mock_ref",
        delivery_otp="4321",
        distance_km=0.8,
        runner_payout=10.0,
        cancel_until=now + timedelta(seconds=180)
    )
    
    db_session.add_all([cust, vendor_user, store, addr, order])
    await db_session.commit()

    cust_token = create_access_token({"sub": cust.id, "phone": cust.phone, "role": "customer"})
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})
    attacker_token = create_access_token({"sub": f"atk_{tag}", "phone": unique_phone(), "role": "customer"})

    # 1. IDOR Check: Attacker cannot request refund for customer's order
    resp_idor = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 50.0, "reason": "Hacked refund"},
        headers={"Authorization": f"Bearer {attacker_token}"}
    )
    assert resp_idor.status_code == 403

    # 2. Rejection of zero or negative refund
    resp_zero = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 0.0},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_zero.status_code == 400

    # 3. Partial Refund of ₹50.0
    resp_partial = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 50.0, "reason": "Damaged biscuits item", "refund_type": "ITEM_LEVEL"},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_partial.status_code == 200
    p_data = resp_partial.json()
    assert p_data["amount"] == 50.0
    assert p_data["status"] == "COMPLETED"
    assert p_data["order_id"] == order.id

    # 4. Check that order is now PARTIALLY_REFUNDED
    await db_session.refresh(order)
    assert order.payment_status == "PARTIALLY_REFUNDED"

    # 5. Excessive Refund check: remaining balance is 218.0 - 50.0 = 168.0. Requesting 170.0 must fail.
    resp_excess = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 170.0},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_excess.status_code == 400
    assert "exceeds remaining refundable balance" in resp_excess.json()["detail"]

    # 6. Complete remaining refund of ₹168.0 by Admin
    resp_full = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 168.0, "reason": "Customer goodwill full remaining refund"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_full.status_code == 200

    # 7. Verify order is now fully REFUNDED
    await db_session.refresh(order)
    assert order.payment_status == "REFUNDED"

    # 8. Requesting another refund on fully refunded order must be rejected
    resp_already = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 10.0},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_already.status_code == 400
    assert "already been fully refunded" in resp_already.json()["detail"]

    # 9. Verify GET /payments/refunds/{order_id}
    resp_list = await client.get(
        f"/api/v1/payments/refunds/{order.id}",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_list.status_code == 200
    ref_items = resp_list.json()
    assert len(ref_items) == 2
    assert sum(r["amount"] for r in ref_items) == 218.0


@pytest.mark.asyncio
async def test_cod_order_refund_handling(client: AsyncClient, db_session):
    now = datetime.now(timezone.utc)
    tag = uuid.uuid4().hex[:6]

    cust = User(id=f"usr_cod_{tag}", phone=unique_phone(), name="COD Customer", role="customer")
    vendor_user = User(id=f"usr_vnd_cod_{tag}", phone=unique_phone(), name="COD Vendor", role="vendor")
    store = Store(
        id=f"str_cod_{tag}",
        owner_id=vendor_user.id,
        shop_name="COD Store",
        owner_name="COD Owner",
        category="Grocery",
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        is_approved=True
    )
    addr = Address(
        id=f"addr_cod_{tag}",
        user_id=cust.id,
        recipient_name="COD Customer",
        phone=cust.phone,
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        block="Minapur",
        district="Muzaffarpur",
        is_default=True
    )
    
    order = Order(
        id=f"ord_cod_{tag}",
        customer_id=cust.id,
        store_id=store.id,
        delivery_address_id=addr.id,
        status="DELIVERED",
        subtotal=100.0,
        delivery_fee=15.0,
        platform_fee=3.0,
        total_amount=118.0,
        payment_method="COD",
        payment_status="PAID",
        delivery_otp="5555",
        distance_km=0.8,
        runner_payout=10.0,
        cancel_until=now + timedelta(seconds=180)
    )
    db_session.add_all([cust, vendor_user, store, addr, order])
    await db_session.commit()

    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})

    # Admin issues COD refund
    resp = await client.post(
        "/api/v1/payments/refund",
        json={"order_id": order.id, "amount": 118.0, "reason": "Damaged goods returned to vendor"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 118.0
    assert data["status"] == "COMPLETED"
    assert "cod_disb_" in data["gateway_refund_id"]

    await db_session.refresh(order)
    assert order.payment_status == "REFUNDED"


@pytest.mark.asyncio
async def test_replacement_workflow_and_zero_cost(client: AsyncClient, db_session):
    now = datetime.now(timezone.utc)
    tag = uuid.uuid4().hex[:6]

    cust = User(id=f"usr_rep_{tag}", phone=unique_phone(), name="Replacement Customer", role="customer")
    vendor_user = User(id=f"usr_vnd_rep_{tag}", phone=unique_phone(), name="Replacement Vendor", role="vendor")
    store = Store(
        id=f"str_rep_{tag}",
        owner_id=vendor_user.id,
        shop_name="Replacement Store",
        owner_name="Rep Owner",
        category="Grocery",
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        is_approved=True
    )
    addr = Address(
        id=f"addr_rep_{tag}",
        user_id=cust.id,
        recipient_name="Rep Customer",
        phone=cust.phone,
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        block="Minapur",
        district="Muzaffarpur",
        is_default=True
    )
    
    order = Order(
        id=f"ord_rep_{tag}",
        customer_id=cust.id,
        store_id=store.id,
        delivery_address_id=addr.id,
        status="DELIVERED",
        subtotal=150.0,
        delivery_fee=15.0,
        platform_fee=3.0,
        total_amount=168.0,
        payment_method="COD",
        payment_status="PAID",
        delivery_otp="9988",
        distance_km=0.8,
        runner_payout=10.0,
        cancel_until=now + timedelta(seconds=180)
    )
    db_session.add_all([cust, vendor_user, store, addr, order])
    await db_session.commit()

    cust_token = create_access_token({"sub": cust.id, "phone": cust.phone, "role": "customer"})
    admin_token = create_access_token({"sub": "admin_test", "phone": "9800000099", "role": "admin"})

    # 1. Customer requests replacement
    resp_req = await client.post(
        f"/api/v1/orders/{order.id}/replacement",
        json={
            "reason": "Damaged milk packet leaking in delivery bag",
            "items_json": '[{"product_name": "Fresh Cow Milk", "quantity": 1}]'
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_req.status_code == 200
    rep_data = resp_req.json()
    rep_id = rep_data["id"]
    assert rep_data["status"] == "REQUESTED"
    assert rep_data["customer_due"] == 0.0 # Customer owes ₹0 for approved free replacement

    # 2. Admin views replacement requests
    resp_admin_list = await client.get(
        "/api/v1/admin/replacements",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_admin_list.status_code == 200
    all_reps = resp_admin_list.json()
    assert any(r["id"] == rep_id for r in all_reps)

    # 3. Admin approves replacement
    resp_app = await client.post(
        f"/api/v1/admin/replacements/{rep_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_app.status_code == 200
    assert resp_app.json()["status"] == "APPROVED"

    # 4. Customer verifies refund & replacement status in support hub
    resp_support = await client.get(
        "/api/v1/support/refund-status",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    assert resp_support.status_code == 200
    support_items = resp_support.json()
    assert any("REPLACEMENT_APPROVED" in s["status"] for s in support_items)


@pytest.mark.asyncio
async def test_runner_payout_pricing_matrix_alignment(client: AsyncClient, db_session):
    now = datetime.now(timezone.utc)
    tag = uuid.uuid4().hex[:6]

    cust_user = User(id=f"usr_c_{tag}", phone=unique_phone(), name="Temp Customer", role="customer")
    runner_user = User(id=f"usr_r_{tag}", phone=unique_phone(), name="Tier Test Runner", role="runner")
    runner = Runner(id=f"rn_{tag}", user_id=runner_user.id, full_name="Tier Test Runner", is_approved=True, is_online=True)
    vendor_user = User(id=f"usr_v_{tag}", phone=unique_phone(), name="Tier Vendor", role="vendor")
    store = Store(
        id=f"str_t_{tag}",
        owner_id=vendor_user.id,
        shop_name="Tier Store",
        owner_name="Tier Owner",
        category="Grocery",
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        is_approved=True
    )
    addr = Address(
        id=f"addr_t_{tag}",
        user_id=cust_user.id,
        recipient_name="Temp Customer",
        phone=cust_user.phone,
        latitude=26.12,
        longitude=85.38,
        village="Chaturshi",
        block="Minapur",
        district="Muzaffarpur",
        is_default=True
    )
    
    # 2 Delivered Orders:
    # Order 1: distance 0.8 km, customer delivery_fee ₹15, runner_payout ₹10
    o1 = Order(
        id=f"ord_p1_{tag}",
        customer_id=cust_user.id,
        store_id=store.id,
        runner_id=runner.id,
        delivery_address_id=addr.id,
        status="DELIVERED",
        subtotal=100.0,
        delivery_fee=15.0,
        platform_fee=3.0,
        total_amount=118.0,
        payment_method="COD",
        payment_status="PAID",
        delivery_otp="1111",
        distance_km=0.8,
        runner_payout=10.0,
        cancel_until=now + timedelta(seconds=180)
    )
    # Order 2: distance 3.0 km, customer delivery_fee ₹25, runner_payout ₹18
    o2 = Order(
        id=f"ord_p2_{tag}",
        customer_id=cust_user.id,
        store_id=store.id,
        runner_id=runner.id,
        delivery_address_id=addr.id,
        status="DELIVERED",
        subtotal=120.0,
        delivery_fee=25.0,
        platform_fee=3.0,
        total_amount=148.0,
        payment_method="COD",
        payment_status="PAID",
        delivery_otp="2222",
        distance_km=3.0,
        runner_payout=18.0,
        cancel_until=now + timedelta(seconds=180)
    )
    db_session.add_all([cust_user, runner_user, runner, vendor_user, store, addr, o1, o2])
    await db_session.commit()

    runner_token = create_access_token({"sub": runner_user.id, "phone": runner_user.phone, "role": "runner"})

    # Check /runner/me endpoint
    resp_me = await client.get("/api/v1/runner/me", headers={"Authorization": f"Bearer {runner_token}"})
    assert resp_me.status_code == 200
    data = resp_me.json()
    
    # Authoritative runner earnings must be 10.0 + 18.0 = 28.0 (NOT customer delivery fee 15 + 25 = 40.0)
    assert data["today_earnings"] == 28.0
    assert data["completed_trips"] == 2
    assert data["cash_to_remit"] == 118.0 + 148.0
