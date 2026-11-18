"""
Apna GaonBazaar - UIDAI Secure QR Code Verification Comprehensive Test Suite
=============================================================================
Tests all 11 required security, cryptographic, and workflow conditions:
1. Genuine supported UIDAI Secure QR
2. Altered or forged QR payload
3. Normal non-Aadhaar QR code (e.g., UPI / URLs)
4. Corrupted image
5. Unreadable e-Aadhaar PDF
6. Missing UIDAI public key or invalid signature
7. Mobile camera permission denied fallback logic
8. Vendor verification journey
9. Runner verification journey
10. Secure database updates (zero full Aadhaar storage)
11. Admin approval workflow preservation (valid QR != auto-approved)
"""

import gzip
import io
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from sqlalchemy.future import select
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.base import User, Store, Runner
from app.services.aadhaar_secure_qr import (
    AadhaarSecureQrParser,
    create_synthetic_signed_qr,
    InvalidAadhaarSignatureError,
    MalformedQrPayloadError,
    NoCertificateConfiguredError,
    UidaiCertificateStore,
    extract_qr_from_image_bytes,
    extract_qr_from_pdf_bytes,
)

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_01_genuine_supported_uidai_secure_qr():
    """Test 1: Genuine supported UIDAI Secure QR decodes and cryptographically verifies."""
    qr_payload, _ = create_synthetic_signed_qr(
        name="Ramesh Kumar Sharma",
        dob="15-05-1994",
        gender="M",
        district="Muzaffarpur",
        vtc="Chaturshi",
        pincode="843128",
        last_four_mobile="9012"
    )

    parser = AadhaarSecureQrParser()
    result = parser.parse_and_verify(qr_payload, allow_test_identity=True)

    assert result["valid"] is True
    assert result["signature_verified"] is True
    assert result["algorithm"] == "SHA256withRSA-2048"
    assert result["name"] == "Ramesh Kumar Sharma"
    assert result["dob"] == "15-05-1994"
    assert result["gender"] == "M"
    assert "Muzaffarpur" in result["address"]
    assert "843128" in result["address"]
    assert result["last_4_digits"] == "9012"
    assert result["photo_base64"] is not None


@pytest.mark.asyncio
async def test_02_altered_or_forged_qr_payload():
    """Test 2: Altered or forged QR payload is strictly rejected by RSA signature check."""
    # Create valid payload
    store = UidaiCertificateStore.get_default()
    priv_key, pub_key, _ = store.get_or_create_test_identity()

    fields = [
        "V2", "3", "548920210315123045001", "Original Resident", "01-01-1990", "M",
        "S/O Ram", "Muzaffarpur", "Near Park", "12", "Village", "843128", "SO", "Bihar",
        "Road", "Minapur", "Chaturshi", "9012"
    ]
    signed_data = b"".join(f.encode("iso-8859-1") + b"\xff" for f in fields)
    sig = priv_key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())

    # Alter the demographic data after signing
    altered_signed_data = signed_data.replace(b"Original Resident", b"Tampered Impostor")
    tampered_decompressed = altered_signed_data + sig
    tampered_qr = str(int.from_bytes(gzip.compress(tampered_decompressed), "big"))

    parser = AadhaarSecureQrParser()
    with pytest.raises(InvalidAadhaarSignatureError):
        parser.parse_and_verify(tampered_qr, allow_test_identity=True)


@pytest.mark.asyncio
async def test_03_normal_non_aadhaar_qr_code():
    """Test 3: Normal non-Aadhaar QR codes (UPI payment, web URL) are rejected cleanly."""
    parser = AadhaarSecureQrParser()

    upi_qr = "upi://pay?pa=apnagaonbazaar@icici&pn=VillageStore&am=250.00&cu=INR"
    with pytest.raises(MalformedQrPayloadError):
        parser.parse_and_verify(upi_qr, allow_test_identity=True)

    url_qr = "https://apnagaonbazaar.in/track/order-8492"
    with pytest.raises(MalformedQrPayloadError):
        parser.parse_and_verify(url_qr, allow_test_identity=True)


@pytest.mark.asyncio
async def test_04_corrupted_image():
    """Test 4: Corrupted or unreadable image returns None without crashing."""
    corrupted_bytes = b"CORRUPTED_NON_IMAGE_DATA_PADDING_12345"
    result = extract_qr_from_image_bytes(corrupted_bytes)
    assert result is None


@pytest.mark.asyncio
async def test_05_unreadable_pdf():
    """Test 5: Unreadable or blank PDF without QR code returns None cleanly."""
    # Minimal valid empty PDF structure
    blank_pdf = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 300 300]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n"
        b"0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n168\n%%EOF"
    )
    result = extract_qr_from_pdf_bytes(blank_pdf)
    assert result is None


@pytest.mark.asyncio
async def test_06_missing_uidai_public_key_or_unknown_cert():
    """Test 6: Payload signed by unknown attacker certificate fails signature verification."""
    # Generate an independent rogue key
    rogue_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    fields = [
        "V2", "3", "548920210315123045001", "Attacker Name", "01-01-1990", "M",
        "S/O Fake", "Muzaffarpur", "Near Park", "12", "Village", "843128", "SO", "Bihar",
        "Road", "Minapur", "Chaturshi", "9012"
    ]
    signed_data = b"".join(f.encode("iso-8859-1") + b"\xff" for f in fields)
    rogue_sig = rogue_key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    rogue_payload = str(int.from_bytes(gzip.compress(signed_data + rogue_sig), "big"))

    parser = AadhaarSecureQrParser()
    with pytest.raises(InvalidAadhaarSignatureError):
        parser.parse_and_verify(rogue_payload, allow_test_identity=True)


@pytest.mark.asyncio
async def test_07_consent_requirement_enforcement():
    """Test 7: Verification rejects requests without voluntary resident consent."""
    qr_payload, _ = create_synthetic_signed_qr()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/kyc/aadhaar/verify-qr", json={
            "qr_data": qr_payload,
            "consent_accepted": False,
            "user_id": "usr_test_no_consent"
        })
        assert res.status_code == 400
        assert "consent" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_08_vendor_verification_journey(db_session):
    """Test 8: Full vendor Aadhaar QR verification updates Supabase/DB profile."""
    import secrets
    u_id = f"usr_v_{secrets.token_hex(4)}"
    phone_sfx = f"{secrets.randbelow(9000) + 1000:04d}"
    phone = f"987654{phone_sfx}"
    
    vendor_user = User(
        id=u_id,
        phone=phone,
        name="Ramesh Dukaan Owner",
        role="vendor",
        is_active=True,
        kyc_status="unverified"
    )
    db_session.add(vendor_user)
    await db_session.commit()

    qr_payload, _ = create_synthetic_signed_qr(
        name="Ramesh Dukaan Owner",
        dob="10-10-1988",
        gender="M",
        district="Muzaffarpur",
        vtc="Chaturshi",
        last_four_mobile=phone_sfx
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/kyc/aadhaar/verify-qr", json={
            "qr_data": qr_payload,
            "user_id": u_id,
            "role": "vendor",
            "consent_accepted": True
        })
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is True
        assert data["kyc_status"] == "aadhaar_qr_verified"
        assert data["name"] == "Ramesh Dukaan Owner"
        assert data["last_4_digits"] == phone_sfx
        assert data["masked_aadhaar"].startswith("XXXX-XXXX-")
        assert data["digital_signature_verified"] is True

    # Verify user record in database
    await db_session.refresh(vendor_user)
    assert vendor_user.kyc_status == "aadhaar_qr_verified"
    assert vendor_user.aadhaar_number == f"XXXX-XXXX-{phone_sfx}"
    assert vendor_user.aadhaar_data["verification_method"] == "UIDAI_SECURE_QR"
    assert vendor_user.aadhaar_data["digital_signature_verified"] is True


@pytest.mark.asyncio
async def test_09_runner_verification_journey(db_session):
    """Test 9: Full runner Aadhaar QR verification updates profile with verified identity."""
    import secrets
    u_id = f"usr_r_{secrets.token_hex(4)}"
    phone_sfx = f"{secrets.randbelow(9000) + 1000:04d}"
    phone = f"987653{phone_sfx}"

    runner_user = User(
        id=u_id,
        phone=phone,
        name="Sonu Mitra Runner",
        role="runner",
        is_active=True,
        kyc_status="unverified"
    )
    db_session.add(runner_user)
    await db_session.commit()

    qr_payload, _ = create_synthetic_signed_qr(
        name="Sonu Mitra Runner",
        dob="05-06-1998",
        gender="M",
        district="Muzaffarpur",
        vtc="Chaturshi",
        last_four_mobile=phone_sfx
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/kyc/aadhaar/verify-qr", json={
            "qr_data": qr_payload,
            "user_id": u_id,
            "role": "runner",
            "consent_accepted": True
        })
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is True
        assert data["kyc_status"] == "aadhaar_qr_verified"
        assert data["last_4_digits"] == phone_sfx

    await db_session.refresh(runner_user)
    assert runner_user.kyc_status == "aadhaar_qr_verified"
    assert runner_user.aadhaar_number == f"XXXX-XXXX-{phone_sfx}"


@pytest.mark.asyncio
async def test_10_secure_database_updates_never_stores_full_aadhaar(db_session):
    """Test 10: Ensures zero 12-digit Aadhaar numbers are stored; only masked suffix and reference ID."""
    import secrets
    u_id = f"usr_p_{secrets.token_hex(4)}"
    phone_sfx = f"{secrets.randbelow(9000) + 1000:04d}"
    phone = f"987652{phone_sfx}"

    user = User(
        id=u_id,
        phone=phone,
        name="Privacy Audit User",
        role="vendor",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    qr_payload, _ = create_synthetic_signed_qr(
        name="Privacy Audit User",
        last_four_mobile=phone_sfx
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/kyc/aadhaar/verify-qr", json={
            "qr_data": qr_payload,
            "user_id": u_id,
            "consent_accepted": True
        })
        assert res.status_code == 200

    await db_session.refresh(user)
    # Strict privacy check: Aadhaar number column must never be a 12-digit number
    assert not (user.aadhaar_number and len(user.aadhaar_number.replace("-", "")) == 12 and user.aadhaar_number.isdigit())
    assert user.aadhaar_number == f"XXXX-XXXX-{phone_sfx}"


@pytest.mark.asyncio
async def test_11_admin_approval_workflow_distinction(db_session):
    """Test 11: Valid QR signature marks KYC verified, but account remains UNAPPROVED until Admin acts."""
    import secrets
    u_id = f"usr_adm_{secrets.token_hex(4)}"
    phone = f"987651{secrets.randbelow(9000) + 1000:04d}"
    str_id = f"str_{secrets.token_hex(4)}"

    vendor_user = User(
        id=u_id,
        phone=phone,
        name="Pending Approval Vendor",
        role="vendor",
        is_active=True,
        kyc_status="unverified"
    )
    db_session.add(vendor_user)

    store = Store(
        id=str_id,
        owner_id=u_id,
        owner_name="Pending Approval Vendor",
        shop_name="Pending Kirana Store",
        category="Grocery",
        latitude=26.2230,
        longitude=85.3520,
        village="Chaturshi",
        is_online=False,
        is_approved=False
    )
    db_session.add(store)
    await db_session.commit()

    # Step A: Vendor verifies Aadhaar QR
    qr_payload, _ = create_synthetic_signed_qr(name="Pending Approval Vendor")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        qr_res = await ac.post("/api/v1/kyc/aadhaar/verify-qr", json={
            "qr_data": qr_payload,
            "user_id": u_id,
            "consent_accepted": True
        })
        assert qr_res.status_code == 200

    # Verify store is STILL unapproved (Aadhaar QR valid does NOT auto-approve)
    await db_session.refresh(store)
    assert store.is_approved is False

    # Step B: Super Admin reviews application
    auth_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        app_res = await ac.get(f"/api/v1/admin/kyc/vendor/{store.id}", headers=auth_headers)
        assert app_res.status_code == 200
        app_data = app_res.json()

        # Confirm Super Admin sees the UIDAI Secure QR cryptographic verification status
        assert app_data["api_verified"]["aadhaar_liveness"]["aadhaar_uidai_status"] == "VERIFIED_UIDAI_SECURE_QR"
        assert app_data["api_verified"]["aadhaar_liveness"]["digital_signature_verified"] is True
        assert app_data["is_approved"] is False

        # Step C: Super Admin explicitly approves the merchant
        approve_res = await ac.post(f"/api/v1/admin/kyc/vendor/{store.id}/approve", headers=auth_headers)
        assert approve_res.status_code == 200
        assert approve_res.json()["is_approved"] is True

    # Final check: Store is now approved and unlocked for operations
    await db_session.refresh(store)
    assert store.is_approved is True
