import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.base import Store, Runner, User
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_scenario_1_vendor_new_applicant_lifecycle():
    """
    Scenario 1: Vendor New Applicant (9800000021)
    - Page 2: Send OTP -> 1234
    - Page 2: Verify OTP -> Authenticated, no store auto-created / unapproved
    - Page 3-7: Wizard Onboard Store
    - Page 8: Store is unapproved (Pending Review)
    - Admin approves store
    """
    # Clean any prior run artifact for 9800000021
    async with AsyncSessionLocal() as session:
        u_res = await session.execute(select(User).where(User.phone == "9800000021"))
        u = u_res.scalars().first()
        if u:
            s_res = await session.execute(select(Store).where(Store.owner_id == u.id))
            st = s_res.scalars().first()
            if st:
                await session.delete(st)
            await session.delete(u)
            await session.commit()

    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Send OTP
        send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000021", "role": "vendor"})
        assert send_res.status_code == 200
        assert send_res.json()["delivery_channel"] in ["staging_sandbox", "test_mock"]

        # Step 2: Verify OTP with 4-digit code '1234'
        ver_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000021",
            "otp": "1234",
            "role": "vendor"
        })
        assert ver_res.status_code == 200
        token = ver_res.json()["access_token"]
        v_headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Check initial profile - store must not exist yet for new applicant
        me_res = await client.get("/api/v1/stores/me", headers=v_headers)
        assert me_res.status_code in [404, 200]
        if me_res.status_code == 200:
            assert me_res.json()["is_approved"] is False

        # Step 4: Submit Store Onboarding (Pages 3-7)
        onboard_res = await client.post("/api/v1/stores/onboard", headers=v_headers, json={
            "shop_name": "Kisan Kirana Store",
            "owner_name": "Raju Prasad",
            "category": "Kirana",
            "latitude": 26.2230,
            "longitude": 85.3520,
            "district": "Muzaffarpur",
            "village": "Chaturshi",
            "landmark": "Opposite Panchayat Bhawan",
            "block": "Minapur",
            "upi_id": "raju.kisan@upi"
        })
        assert onboard_res.status_code == 200
        store = onboard_res.json()
        assert store["is_approved"] is False
        store_id = store["id"]

        # Step 5: Verify store remains unapproved (Page 8 review state)
        profile_res = await client.get("/api/v1/stores/me", headers=v_headers)
        assert profile_res.status_code == 200
        assert profile_res.json()["is_approved"] is False

        # Step 6: Admin approves store
        app_res = await client.post(f"/api/v1/admin/vendors/{store_id}/approve", headers=adm_headers)
        assert app_res.status_code == 200

        # Step 7: Store is now approved
        approved_res = await client.get("/api/v1/stores/me", headers=v_headers)
        assert approved_res.status_code == 200
        assert approved_res.json()["is_approved"] is True

@pytest.mark.asyncio
async def test_scenario_2_runner_new_applicant_lifecycle():
    """
    Scenario 2: Runner New Applicant (9800000031)
    - Page 2: Send OTP -> 1234
    - Page 2: Verify OTP -> Authenticated, no runner profile auto-approved
    - Page 3-5: Wizard Onboard Runner (strictly without forced vehicle registration)
    - Page 6: Profile is unapproved (Pending Review)
    - Admin approves runner
    """
    # Clean any prior run artifact for 9800000031
    async with AsyncSessionLocal() as session:
        u_res = await session.execute(select(User).where(User.phone == "9800000031"))
        u = u_res.scalars().first()
        if u:
            r_res = await session.execute(select(Runner).where(Runner.user_id == u.id))
            rn = r_res.scalars().first()
            if rn:
                await session.delete(rn)
            await session.delete(u)
            await session.commit()

    adm_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Send OTP
        send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000031", "role": "runner"})
        assert send_res.status_code == 200

        # Step 2: Verify OTP with 4-digit code '1234'
        ver_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000031",
            "otp": "1234",
            "role": "runner"
        })
        assert ver_res.status_code == 200
        token = ver_res.json()["access_token"]
        r_headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Check initial profile - runner must not exist or be unapproved
        prof_res = await client.get("/api/v1/runner/profile", headers=r_headers)
        if prof_res.status_code == 200 and prof_res.json():
            assert prof_res.json()["is_approved"] is False

        # Step 4: Submit Runner Onboarding (Pages 3-5)
        onboard_res = await client.post("/api/v1/runner/onboard", headers=r_headers, json={
            "full_name": "Santosh Kumar",
            "vehicle_type": "Motorcycle",
            "vehicle_number": "PENDING_REGISTRATION",
            "driving_licence_no": "PENDING_VERIFICATION",
            "father_name": "Rameshwar Prasad",
            "emergency_contact": "9800000099",
            "account_holder_name": "Santosh Kumar",
            "account_number": "123456789012",
            "ifsc_code": "SBIN0001234",
            "aadhaar_front_url": "test_aadhaar_front.jpg",
            "aadhaar_back_url": "test_aadhaar_back.jpg",
            "selfie_url": "test_runner_selfie.jpg",
            "upi_id": "A/C:9012:SBIN0001234"
        })
        assert onboard_res.status_code in [200, 201]

        # Step 5: Check profile - must be unapproved (Page 6 review state)
        pending_res = await client.get("/api/v1/runner/profile", headers=r_headers)
        assert pending_res.status_code == 200
        runner_data = pending_res.json()
        assert runner_data["is_approved"] is False
        runner_id = runner_data["id"]

        # Step 6: Admin approves runner
        app_res = await client.post(f"/api/v1/admin/runners/{runner_id}/approve", headers=adm_headers)
        assert app_res.status_code == 200

        # Step 7: Runner is now approved
        active_res = await client.get("/api/v1/runner/profile", headers=r_headers)
        assert active_res.status_code == 200
        assert active_res.json()["is_approved"] is True
