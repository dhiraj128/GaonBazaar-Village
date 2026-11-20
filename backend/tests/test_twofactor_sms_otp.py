import os
import re
import pytest
import httpx
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.services.sms import normalize_indian_phone, send_sms_otp

def test_normalize_indian_phone_formats():
    """Verify normalize_indian_phone handles multiple input variations correctly."""
    # 1. Standard 10-digit
    assert normalize_indian_phone("9876543210") == "9876543210"

    # 2. +91 prefix with/without spaces and hyphens
    assert normalize_indian_phone("+919876543210") == "9876543210"
    assert normalize_indian_phone("+91 98765-43210") == "9876543210"
    assert normalize_indian_phone("+91 (987) 654-3210") == "9876543210"

    # 3. 91 country code without +
    assert normalize_indian_phone("919876543210") == "9876543210"

    # 4. Leading 0 trunk prefix
    assert normalize_indian_phone("09876543210") == "9876543210"

    # 5. Invalid numbers must raise HTTP 400
    with pytest.raises(HTTPException) as exc_info:
        normalize_indian_phone("")
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        normalize_indian_phone("12345")
    assert exc_info.value.status_code == 400

    with pytest.raises(HTTPException) as exc_info:
        normalize_indian_phone("1234567890") # Starts with 1 (not 5-9)
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_twofactor_sms_otp_success_mock(monkeypatch):
    """Verify send_sms_otp dispatches to 2Factor.in endpoint and parses success JSON."""
    test_key = "2factor-test-api-key-success-123"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    mock_resp = httpx.Response(
        200,
        json={"Status": "Success", "Details": "session-uuid-success-test-789"},
        request=httpx.Request("GET", "https://2factor.in")
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        result = await send_sms_otp("+91 98765-43210", "654321")

        # Verify correct URL format: https://2factor.in/API/V1/{KEY}/SMS/+91{PHONE}/{OTP}/OTP1
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url == f"https://2factor.in/API/V1/{test_key}/SMS/+919876543210/654321/OTP1"

        # Verify response structure
        assert result["status"] == "delivered"
        assert result["provider"] == "2factor"
        assert result["session_id"] == "session-uuid-success-test-789"

@pytest.mark.asyncio
async def test_twofactor_sms_otp_error_response_502(monkeypatch):
    """Verify that when 2Factor.in returns Status: Error, an HTTP 502 is raised with error details."""
    test_key = "2factor-test-api-key-err"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    mock_resp = httpx.Response(
        200,
        json={"Status": "Error", "Details": "Invalid API Key"},
        request=httpx.Request("GET", "https://2factor.in")
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        with pytest.raises(HTTPException) as exc_info:
            await send_sms_otp("9876543210", "112233")

        assert exc_info.value.status_code == 502
        assert "Invalid API Key" in exc_info.value.detail

@pytest.mark.asyncio
async def test_twofactor_sms_otp_http_error_from_gateway(monkeypatch):
    """Verify that when 2Factor.in returns HTTP 400/500, clear HTTP errors are returned."""
    test_key = "2factor-test-api-key-http-err"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    mock_resp = httpx.Response(
        400,
        json={"Status": "Error", "Details": "Invalid Mobile Number"},
        request=httpx.Request("GET", "https://2factor.in")
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        with pytest.raises(HTTPException) as exc_info:
            await send_sms_otp("9876543210", "112233")

        assert exc_info.value.status_code == 400
        assert "Invalid Mobile Number" in exc_info.value.detail

@pytest.mark.asyncio
async def test_twofactor_sms_otp_network_timeout(monkeypatch):
    """Verify network connection timeout raises HTTP 502 Bad Gateway."""
    test_key = "2factor-test-api-key-timeout"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectTimeout("Connection to 2Factor.in timed out")

        with pytest.raises(HTTPException) as exc_info:
            await send_sms_otp("9876543210", "112233")

        assert exc_info.value.status_code == 502
        assert "Unable to reach SMS gateway" in exc_info.value.detail

@pytest.mark.asyncio
async def test_auth_endpoints_send_and_verify_with_2factor_mock(monkeypatch):
    """
    Test full auth flow via FastAPI endpoints:
    1. /api/v1/auth/otp/send and /api/v1/auth/send-otp
    2. /api/v1/auth/otp/verify and /api/v1/auth/verify-otp
    with 2Factor.in mocked.
    """
    settings.TESTING = True
    test_key = "2factor-mock-e2e-key"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    mock_resp = httpx.Response(
        200,
        json={"Status": "Success", "Details": "session-e2e-12345"},
        request=httpx.Request("GET", "https://2factor.in")
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            # 1. Send OTP via /api/v1/auth/send-otp with formatted phone number
            send_res = await client.post("/api/v1/auth/send-otp", json={
                "phone": "+91 98888-77777",
                "role": "customer"
            })
            assert send_res.status_code == 200
            send_data = send_res.json()
            session_id = send_data["session_id"]
            assert session_id is not None
            assert send_data["delivery_status"] in ("dispatched", "delivered")
            assert send_data["status"] == "sent"

            # Check that 2Factor GET was dispatched with normalized phone
            called_url = mock_get.call_args[0][0]
            assert "/SMS/+919888877777/" in called_url

            # Extract generated OTP from in-memory cache to verify
            from app.api.v1.auth import OTP_STORAGE
            stored_otp = OTP_STORAGE["9888877777"]["otp"]

            # 2. Verify OTP via /api/v1/auth/verify-otp
            verify_res = await client.post("/api/v1/auth/verify-otp", json={
                "phone": "+91 98888 77777",
                "otp": stored_otp,
                "session_id": session_id,
                "role": "customer"
            })
            assert verify_res.status_code == 200
            auth_data = verify_res.json()
            assert "access_token" in auth_data
            assert auth_data["user"]["phone"] == "9888877777"
            assert auth_data["user"]["role"] == "customer"

@pytest.mark.asyncio
async def test_auth_send_otp_non_blocking_instant_response_on_background_error(monkeypatch):
    """Verify send_otp returns 200 immediately with BackgroundTasks even if 2Factor has an issue."""
    settings.TESTING = True
    test_key = "2factor-failing-key"
    monkeypatch.setenv("TWOFACTOR_API_KEY", test_key)

    mock_resp = httpx.Response(
        200,
        json={"Status": "Error", "Details": "DND Blocked or Insufficient Balance"},
        request=httpx.Request("GET", "https://2factor.in")
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp

            send_res = await client.post("/api/v1/auth/otp/send", json={
                "phone": "9877766655",
                "role": "customer"
            })
            assert send_res.status_code == 200
            resp_data = send_res.json()
            assert resp_data["status"] == "sent"
            assert resp_data["delivery_status"] == "dispatched"
