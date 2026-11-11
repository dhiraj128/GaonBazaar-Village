import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_razorpay_compliance_backdoor_flow():
    """
    Test Global Razorpay Compliance Backdoor:
    - Phone: 9999999999
    - Backend intercepts before SMS dispatch: does NOT send real SMS
    - Returns session_id and delivery_channel: razorpay_compliance
    - Verification with exact OTP: 123456
    - Returns 200 OK and valid JWT bearer access token
    - User profile is authenticated as Razorpay Compliance Reviewer
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Send OTP challenge for Razorpay compliance number
        send_res = await client.post("/api/v1/auth/otp/send", json={
            "phone": "9999999999",
            "role": "customer"
        })
        assert send_res.status_code == 200
        send_data = send_res.json()
        assert send_data["delivery_channel"] == "razorpay_compliance"
        assert send_data["delivery_status"] == "delivered"
        session_id = send_data["session_id"]

        # 2. Verify with invalid OTP should fail
        bad_verify = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9999999999",
            "otp": "000000",
            "session_id": session_id,
            "role": "customer"
        })
        assert bad_verify.status_code == 400

        # 3. Verify with exact backdoor OTP 123456 must succeed
        verify_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9999999999",
            "otp": "123456",
            "session_id": session_id,
            "role": "customer"
        })
        assert verify_res.status_code == 200
        auth_data = verify_res.json()
        assert "access_token" in auth_data
        assert auth_data["token_type"] == "bearer"
        assert auth_data["user"]["phone"] == "9999999999"
        assert "Razorpay" in auth_data["user"]["name"]

@pytest.mark.asyncio
async def test_universal_live_otp_for_unregistered_number():
    """
    Test that new unregistered 10-digit Indian mobile numbers (e.g. 9812345678)
    can request and receive OTP challenge without whitelist blocking.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Request OTP for new number
        send_res = await client.post("/api/v1/auth/otp/send", json={
            "phone": "9812345678",
            "role": "customer"
        })
        assert send_res.status_code == 200
        send_data = send_res.json()
        assert send_data["delivery_channel"] == "sms"
        assert "session_id" in send_data
