import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.base import OtpChallenge, User, Store, Runner
from app.api.v1.auth import OTP_STORAGE

@pytest.mark.asyncio
async def test_otp_database_persistence_across_memory_wipe():
    """Verify OTP challenge is stored in DB and verifies successfully even after memory cache is cleared."""
    settings.TESTING = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        phone = "9800000000"
        
        # 1. Request OTP challenge
        send_res = await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": "customer"})
        assert send_res.status_code == 200
        send_data = send_res.json()
        session_id = send_data["session_id"]
        assert session_id is not None
        assert send_data["delivery_channel"] == "staging_sandbox"
        
        # 2. Verify challenge exists in persistent database table
        async with AsyncSessionLocal() as session:
            db_res = await session.execute(
                select(OtpChallenge).where(OtpChallenge.session_id == session_id)
            )
            challenge = db_res.scalars().first()
            assert challenge is not None
            assert challenge.phone == phone
            assert challenge.is_used is False
            assert challenge.attempts == 0
            
        # 3. Simulate total server restart / memory wipe by clearing OTP_STORAGE
        OTP_STORAGE.clear()
        assert phone not in OTP_STORAGE
        
        # 4. Verification must STILL succeed by querying persistent database table
        verify_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": phone,
            "otp": "123456",
            "session_id": session_id,
            "role": "customer"
        })
        assert verify_res.status_code == 200, f"Verification failed: {verify_res.text}"
        data = verify_res.json()
        assert "access_token" in data
        assert data["user"]["phone"] == phone
        assert data["user"]["role"] == "customer"
        
        # 5. Verify challenge is marked is_used in DB (single-use)
        async with AsyncSessionLocal() as session:
            db_res2 = await session.execute(
                select(OtpChallenge).where(OtpChallenge.session_id == session_id)
            )
            challenge2 = db_res2.scalars().first()
            assert challenge2.is_used is True

        # 6. Replay attack must be strictly rejected
        replay_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": phone,
            "otp": "123456",
            "session_id": session_id,
            "role": "customer"
        })
        assert replay_res.status_code == 400

@pytest.mark.asyncio
async def test_staging_personas_customer_vendor_runner_login():
    """Verify Customer, Vendor, and Runner staging personas can authenticate and have correct models created."""
    settings.TESTING = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        personas = [
            ("9800000000", "customer", "Minapur Pilot Customer"),
            ("9800000001", "vendor", "Chaturshi Kirana Store"),
            ("9800000003", "runner", "Minapur Fast Runner"),
        ]
        
        for phone, role, expected_name in personas:
            OTP_STORAGE.pop(phone, None)
            s_res = await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": role})
            assert s_res.status_code == 200
            s_data = s_res.json()
            sess_id = s_data["session_id"]
            
            v_res = await client.post("/api/v1/auth/otp/verify", json={
                "phone": phone,
                "otp": "123456",
                "session_id": sess_id,
                "role": role
            })
            assert v_res.status_code == 200, f"Login failed for {role}: {v_res.text}"
            token_data = v_res.json()
            assert token_data["user"]["role"] == role
            
            # Verify linked store or runner auto-approved in staging
            async with AsyncSessionLocal() as session:
                u_res = await session.execute(select(User).where(User.phone == phone))
                u = u_res.scalars().first()
                assert u is not None
                
                if role == "vendor":
                    st_res = await session.execute(select(Store).where(Store.owner_id == u.id))
                    st = st_res.scalars().first()
                    assert st is not None
                    assert st.is_approved is True, "Staging test vendor must be pre-approved"
                elif role == "runner":
                    rn_res = await session.execute(select(Runner).where(Runner.user_id == u.id))
                    rn = rn_res.scalars().first()
                    assert rn is not None
                    assert rn.is_approved is True, "Staging test runner must be pre-approved"

@pytest.mark.asyncio
async def test_public_user_random_otp_and_sms_status():
    """Verify non-whitelisted public number generates random OTP and marks SMS delivery status."""
    settings.TESTING = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        public_phone = "9822334455"
        OTP_STORAGE.pop(public_phone, None)
        
        s_res = await client.post("/api/v1/auth/otp/send", json={"phone": public_phone, "role": "customer"})
        assert s_res.status_code == 200
        data = s_res.json()
        assert data["delivery_channel"] == "sms"
        assert data["delivery_status"] in ("pending_credentials", "delivered")
        assert data["mock_otp"] is None
        
        # Test bypass '123456' fails for public number
        v_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": public_phone,
            "otp": "123456",
            "session_id": data["session_id"],
            "role": "customer"
        })
        assert v_res.status_code == 400
