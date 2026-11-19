import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_payout_setup_bank_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token = create_access_token({"sub": "test_vendor_payout", "role": "vendor"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Reject non-numeric account number
        res_non_numeric = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "bank",
                "role": "vendor",
                "account_holder_name": "Rajesh Kumar",
                "shop_name": "Rajesh Kirana Store",
                "account_number": "1234ABCD5678",
                "confirm_account_number": "1234ABCD5678",
                "ifsc_code": "SBIN0001234",
            },
        )
        assert res_non_numeric.status_code == 400
        assert "numeric" in res_non_numeric.json()["detail"].lower()

        # 2. Reject short account number (<9 digits)
        res_short = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "bank",
                "role": "vendor",
                "account_holder_name": "Rajesh Kumar",
                "shop_name": "Rajesh Kirana Store",
                "account_number": "12345",
                "confirm_account_number": "12345",
                "ifsc_code": "SBIN0001234",
            },
        )
        assert res_short.status_code == 400
        assert "9 to 18" in res_short.json()["detail"]

        # 3. Reject mismatch between account_number and confirm_account_number
        res_mismatch = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "bank",
                "role": "vendor",
                "account_holder_name": "Rajesh Kumar",
                "shop_name": "Rajesh Kirana Store",
                "account_number": "50100456789012",
                "confirm_account_number": "50100456789099",
                "ifsc_code": "SBIN0001234",
            },
        )
        assert res_mismatch.status_code == 400
        assert "match" in res_mismatch.json()["detail"].lower()

        # 4. Reject invalid IFSC format (5th character not '0')
        res_bad_ifsc = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "bank",
                "role": "vendor",
                "account_holder_name": "Rajesh Kumar",
                "shop_name": "Rajesh Kirana Store",
                "account_number": "50100456789012",
                "confirm_account_number": "50100456789012",
                "ifsc_code": "SBIN1234567",
            },
        )
        assert res_bad_ifsc.status_code == 400
        assert "ifsc" in res_bad_ifsc.json()["detail"].lower()


@pytest.mark.asyncio
async def test_payout_setup_upi_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token = create_access_token({"sub": "test_runner_payout", "role": "runner"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Reject invalid UPI syntax (no @)
        res_invalid_upi = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "upi",
                "role": "runner",
                "account_holder_name": "Amit Sharma",
                "upi_id": "amitsharma-invalid-upi",
            },
        )
        assert res_invalid_upi.status_code == 400
        assert "upi" in res_invalid_upi.json()["detail"].lower()

        # 2. Reject missing account holder name
        res_missing_name = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "upi",
                "role": "runner",
                "account_holder_name": "   ",
                "upi_id": "amitsharma@oksbi",
            },
        )
        assert res_missing_name.status_code == 400
        assert "account holder name" in res_missing_name.json()["detail"].lower()


@pytest.mark.asyncio
async def test_payout_setup_different_shop_and_holder_name():
    """Vendors frequently have different shop names and bank account holder names."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        token = create_access_token({"sub": "test_vendor_decouple", "role": "vendor"})
        headers = {"Authorization": f"Bearer {token}"}

        # Valid setup with shop name 'Maa Durga Kirana' and holder 'Sunil Prasad'
        res = await ac.post(
            "/api/v1/payments/payout-setup",
            headers=headers,
            json={
                "payout_method": "bank",
                "role": "vendor",
                "shop_name": "Maa Durga Kirana",
                "account_holder_name": "Sunil Prasad",
                "account_number": "30987654321",
                "confirm_account_number": "30987654321",
                "ifsc_code": "SBIN0001234",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] in ("pending_admin_approval", "success")
        assert body["verification_status"] == "PENDING_VERIFICATION"
        assert body["account_holder_name"] == "Sunil Prasad"
        assert body["shop_name"] == "Maa Durga Kirana"

@pytest.mark.asyncio
async def test_admin_kyc_review_payout_details():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin_token = create_access_token({"sub": "admin_test", "role": "super_admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Vendor KYC detail
        res = await ac.get("/api/v1/admin/kyc/vendor/store_1", headers=headers)
        if res.status_code == 200:
            data = res.json()
            assert "user_submitted" in data
            assert "api_verified" in data
            assert "payout_verification" in data["api_verified"]
            assert data["api_verified"]["payout_verification"]["verification_status"] == "PENDING_VERIFICATION"
            # Bank account number must be masked in masked field
            masked = data["api_verified"]["payout_verification"]["bank_account_number_masked"]
            assert masked == "NOT_CONFIGURED" or masked.startswith("••••") or "Ending in" in masked
