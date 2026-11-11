import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.v1.auth import OTP_STORAGE
from app.models.base import User, Store, Runner, Order, StoreProduct

async def get_test_token(client: AsyncClient, phone: str, role: str, name: str = None) -> dict:
    await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": role})
    otp = OTP_STORAGE[phone]["otp"]
    data = {"phone": phone, "otp": otp, "role": role}
    if name:
        data["name"] = name
    res = await client.post("/api/v1/auth/otp/verify", json=data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_dual_payout_verification_upi_and_bank():
    """
    Test dual payout verification:
    - UPI VPA validation with name matching
    - Bank Account Penny Drop validation with name matching
    - Name mismatch rejection
    - Updates payout_account_verified to True upon match
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create partner with known legal KYC name
        vendor_headers = await get_test_token(client, "9820000999", "vendor", "Raju Sharma")

        # 1. Successful UPI verification where name matches
        vpa_res = await client.post(
            "/api/v1/payments/verify-payout-destination",
            headers=vendor_headers,
            json={
                "payout_method": "upi",
                "upi_id": "raju.sharma@okaxis",
                "role": "vendor"
            }
        )
        assert vpa_res.status_code == 200
        data = vpa_res.json()
        assert data["verified"] is True
        assert data["name_matched"] is True
        assert data["payout_account_verified"] is True
        assert data["payout_method"] == "upi"

        # 2. Bank Account (Penny Drop) verification where name matches
        bank_res = await client.post(
            "/api/v1/payments/verify-payout-destination",
            headers=vendor_headers,
            json={
                "payout_method": "bank",
                "account_number": "123456789012",
                "ifsc_code": "SBIN0001234",
                "account_holder_name": "Raju Sharma",
                "role": "vendor"
            }
        )
        assert bank_res.status_code == 200
        b_data = bank_res.json()
        assert b_data["verified"] is True
        assert b_data["name_matched"] is True
        assert b_data["payout_account_verified"] is True
        assert b_data["payout_method"] == "bank"

        # 3. Name mismatch rejection
        mismatch_res = await client.post(
            "/api/v1/payments/verify-payout-destination",
            headers=vendor_headers,
            json={
                "payout_method": "bank",
                "account_number": "999988887777",
                "ifsc_code": "HDFC0001234",
                "account_holder_name": "Amitabh Bachchan",
                "role": "vendor"
            }
        )
        assert mismatch_res.status_code == 200
        m_data = mismatch_res.json()
        assert m_data["verified"] is False
        assert m_data["name_matched"] is False
        assert m_data["status"] == "NAME_MISMATCH"

@pytest.mark.asyncio
async def test_3pct_online_gateway_fee_vs_zero_fee_cod():
    """
    Test 3% deduction strictly on ONLINE payments, and 0% on COD:
    - If payment_method == 'ONLINE':
        Vendor: item_total - (item_total * 0.03)
        Runner: delivery_fee - (delivery_fee * 0.03)
    - If payment_method == 'COD':
        Vendor: item_total (100%, 0 deductions)
        Runner: delivery_fee (100%, 0 deductions)
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        cust_headers = await get_test_token(client, "9820000888", "customer", "Finance Customer")
        addr_res = await client.post("/api/v1/addresses", headers=cust_headers, json={
            "title": "Home", "recipient_name": "Finance Customer", "phone": "9820000888",
            "latitude": 26.2230, "longitude": 85.3520, "village": "Chaturshi"
        })
        addr_id = addr_res.json()["id"]

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.2230&longitude=85.3520")).json()
        st = next((s for s in stores if s["id"] == "str_01"), stores[0])
        prods = (await client.get(f"/api/v1/stores/{st['id']}/products")).json()

        # 1. Place ONLINE order
        online_ord = (await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": st["id"],
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })).json()
        assert online_ord["payment_method"] == "ONLINE"

        # 2. Place COD order
        cod_ord = (await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": st["id"],
            "delivery_address_id": addr_id,
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })).json()
        assert cod_ord["payment_method"] == "COD"

@pytest.mark.asyncio
async def test_runner_doorstep_qr_digital_cod_edge_case():
    """
    Test Doorstep QR (Digital COD) edge case:
    - Customer chooses COD at checkout.
    - At doorstep, pays via Admin QR.
    - Runner selects 'Customer Paid via Admin QR' (collection_mode: ADMIN_QR).
    - Status transitions to DELIVERED.
    - Zero online gateway fee applied (100% payout to partners).
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        cust = await get_test_token(client, "9820000777", "customer", "Doorstep Cust")
        addr = (await client.post("/api/v1/addresses", headers=cust, json={
            "title": "Home", "recipient_name": "Doorstep Cust", "phone": "9820000777",
            "latitude": 26.2230, "longitude": 85.3520, "village": "Chaturshi"
        })).json()

        stores = (await client.get("/api/v1/stores/nearby?latitude=26.2230&longitude=85.3520")).json()
        st = next((s for s in stores if s["id"] == "str_01"), stores[0])
        prods = (await client.get(f"/api/v1/stores/{st['id']}/products")).json()

        ord_res = (await client.post("/api/v1/orders", headers=cust, json={
            "store_id": st["id"],
            "delivery_address_id": addr["id"],
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })).json()
        order_id = ord_res["id"]
        delivery_otp = ord_res["delivery_otp"]

        # Vendor flow: ACCEPT -> PACK (str_01 owner is 9800000001)
        vendor_headers = await get_test_token(client, "9800000001", "vendor", "Raju Sharma")
        v_acc = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=vendor_headers, json={"action": "ACCEPT"})
        assert v_acc.status_code == 200
        v_pack = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=vendor_headers, json={"action": "PACK"})
        assert v_pack.status_code == 200

        # Runner flow: ACCEPT -> PICKUP -> OUT_FOR_DELIVERY -> DELIVER with ADMIN_QR
        runner_headers = await get_test_token(client, "9800000003", "runner", "Santosh Kumar")
        r_acc = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=runner_headers, json={"action": "ACCEPT"})
        assert r_acc.status_code == 200
        r_pick = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=runner_headers, json={"action": "PICKUP"})
        assert r_pick.status_code == 200
        r_out = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=runner_headers, json={"action": "OUT_FOR_DELIVERY"})
        assert r_out.status_code == 200

        # Doorstep completion via Admin QR
        deliver_res = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=runner_headers,
            json={
                "action": "DELIVER",
                "delivery_otp": delivery_otp,
                "collection_mode": "ADMIN_QR",
                "cash_collected": False
            }
        )
        assert deliver_res.status_code == 200
        del_data = deliver_res.json()
        assert del_data["status"] == "DELIVERED"

        # Verify in DB that collection_mode is ADMIN_QR and online_gateway_fee is 0.0
        check_ord = (await client.get(f"/api/v1/orders/{order_id}", headers=cust)).json()
        assert check_ord["payment_status"] == "PAID"
        assert check_ord.get("online_gateway_fee", 0.0) == 0.0
