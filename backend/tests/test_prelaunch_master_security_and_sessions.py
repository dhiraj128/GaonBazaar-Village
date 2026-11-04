import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_token_revocation_on_logout():
    """
    OWASP ASVS 5.0 - Session Management:
    - User logs in and obtains a valid JWT token.
    - User accesses protected endpoints successfully.
    - User logs out via POST /api/v1/auth/logout.
    - Subsequent requests with the revoked token are rejected with 401 Unauthorized.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Customer login
        headers = await issue_and_verify_test_token(client, "9800000010", "customer")
        
        # 2. Access protected endpoint -> 200 OK
        resp1 = await client.get("/api/v1/addresses", headers=headers)
        assert resp1.status_code == 200
        
        # 3. Call logout
        logout_resp = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_resp.status_code == 200
        assert logout_resp.json()["status"] == "SUCCESS"
        
        # 4. Attempt unauthorized session reuse with the revoked token -> 401 Unauthorized
        resp2 = await client.get("/api/v1/addresses", headers=headers)
        assert resp2.status_code == 401
        assert "revoked" in resp2.text.lower() or "expired" in resp2.text.lower()

@pytest.mark.asyncio
async def test_account_suspension_enforcement():
    """
    OWASP ASVS 5.0 - Access Control:
    - User has an active session.
    - Super Admin / Hub Manager suspends the user account (is_active=False).
    - Immediate suspension enforcement rejects user requests with 403 Forbidden.
    - When admin reinstates the user (is_active=True), access is restored.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
        
        # 1. Customer login
        cust_headers = await issue_and_verify_test_token(client, "9800000011", "customer")
        
        # Get customer user ID
        me_resp = await client.get("/api/v1/auth/me", headers=cust_headers)
        assert me_resp.status_code == 200
        user_id = me_resp.json()["id"]
        
        # 2. Admin suspends customer account
        suspend_resp = await client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            headers=admin_headers,
            json={"is_active": False, "reason": "Security audit test suspension"}
        )
        assert suspend_resp.status_code == 200
        assert suspend_resp.json()["is_active"] is False
        
        # 3. Suspended customer attempts access -> MUST receive 403 Forbidden
        blocked_resp = await client.get("/api/v1/addresses", headers=cust_headers)
        assert blocked_resp.status_code == 403
        assert "suspended" in blocked_resp.text.lower() or "निलंबित" in blocked_resp.text
        
        # 4. Admin reinstates customer account
        reinstate_resp = await client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            headers=admin_headers,
            json={"is_active": True, "reason": "Audit passed, account restored"}
        )
        assert reinstate_resp.status_code == 200
        assert reinstate_resp.json()["is_active"] is True
        
        # 5. Customer access restored -> 200 OK
        restored_resp = await client.get("/api/v1/addresses", headers=cust_headers)
        assert restored_resp.status_code == 200
