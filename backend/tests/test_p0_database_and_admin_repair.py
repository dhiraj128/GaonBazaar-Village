import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_db_sanitized_and_no_leak():
    """Verify /health/db does not leak raw internal SQL errors or tracebacks."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health/db")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "readiness" in data
        assert data["readiness"] in ["ready", "degraded"]
        # Ensure no SQL traceback or raw syntax error is leaked
        assert "traceback" not in str(data).lower()
        assert "programmingerror" not in str(data).lower()
        assert "undefinedtableerror" not in str(data).lower()

@pytest.mark.asyncio
async def test_seed_database_endpoint_is_strictly_protected():
    """Verify /api/v1/system/seed-database rejects unauthorized calls with HTTP 403."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Unauthenticated call -> 403
        unauth_res = await client.post("/api/v1/system/seed-database")
        assert unauth_res.status_code == 403
        
        # 2. Invalid admin key -> 403
        bad_key_res = await client.post(
            "/api/v1/system/seed-database",
            headers={"X-Admin-Key": "invalid_unauthorized_key"}
        )
        assert bad_key_res.status_code == 403

        # 3. Valid admin key -> 200
        valid_res = await client.post(
            "/api/v1/system/seed-database",
            headers={"X-Admin-Key": settings.ADMIN_API_KEY}
        )
        assert valid_res.status_code == 200
        assert valid_res.json()["status"] == "success"

@pytest.mark.asyncio
async def test_admin_auth_passcode_and_phone_whitelist():
    """Verify Admin authentication accepts 123456 or Admin Key for 9800000099, but strictly rejects non-admin phones."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Non-admin phone (e.g. Customer 9800000000) entering 123456 -> 403 Forbidden
        cust_fail = await client.post("/api/v1/admin/auth/login", json={
            "phone": "9800000000",
            "secret_key": "123456"
        })
        assert cust_fail.status_code == 403
        assert "not authorized for administrative access" in cust_fail.json()["detail"]

        # 2. Non-admin phone entering random password -> 403 Forbidden
        public_fail = await client.post("/api/v1/admin/auth/login", json={
            "phone": "9812345678",
            "secret_key": "any_secret"
        })
        assert public_fail.status_code == 403

        # 3. Authorized Admin phone with wrong passcode -> 401 Unauthorized
        admin_bad_pw = await client.post("/api/v1/admin/auth/login", json={
            "phone": "9800000099",
            "secret_key": "wrong_passcode"
        })
        assert admin_bad_pw.status_code == 401

        # 4. Authorized Admin phone with staging challenge '123456' -> 200 OK
        admin_ok_passcode = await client.post("/api/v1/admin/auth/login", json={
            "phone": "9800000099",
            "secret_key": "123456"
        })
        assert admin_ok_passcode.status_code == 200
        token = admin_ok_passcode.json()["access_token"]
        assert token is not None
        assert admin_ok_passcode.json()["user"]["role"] == "admin"

        # 5. Authorized Admin phone with master ADMIN_API_KEY -> 200 OK
        admin_ok_key = await client.post("/api/v1/admin/auth/login", json={
            "phone": "9800000099",
            "secret_key": settings.ADMIN_API_KEY
        })
        assert admin_ok_key.status_code == 200
        assert admin_ok_key.json()["access_token"] is not None

@pytest.mark.asyncio
async def test_payment_diagnostic_endpoint_protection():
    """Verify /api/v1/payments/diagnostic is restricted to Super Admin and returns clean diagnostics without secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Unauthenticated -> 403
        res_unauth = await client.get("/api/v1/payments/diagnostic")
        assert res_unauth.status_code == 403

        # 2. Authorized via X-Admin-Key -> 200
        res_auth = await client.get(
            "/api/v1/payments/diagnostic",
            headers={"X-Admin-Key": settings.ADMIN_API_KEY}
        )
        assert res_auth.status_code == 200
        diag = res_auth.json()
        assert "has_key_id" in diag
        assert "key_prefix" in diag
        assert "has_key_secret" in diag
        assert "configured" in diag
        assert "gateway_handshake" in diag
        # Ensure raw secrets are NEVER exposed in response
        assert settings.RAZORPAY_KEY_SECRET not in str(diag)
        assert settings.RAZORPAY_KEY_ID not in str(diag)
