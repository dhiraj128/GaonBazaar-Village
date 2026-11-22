"""Source-level regression checks for previously discovered security bypasses.

These tests intentionally do not invoke live endpoints, modify financial data, or
need production secrets. They are supplementary to full integration tests.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_admin_login_has_no_compliance_backdoor_or_client_selected_role():
    code = source("backend/app/api/v1/admin.py")
    assert "is_razorpay_backdoor" not in code
    assert "assigned_role = req.role" not in code
    assert "phone: str = \"9800000099\"" not in code
    assert "and credential in {\"123456\", \"1234\"}" not in code


def test_public_otp_never_auto_grants_privileged_roles():
    backend = source("backend/app/api/v1/auth.py")
    assert "is_razorpay_backdoor" not in backend
    assert 'matched_role not in {"customer", "vendor", "runner"}' in backend
    assert "is_non_prod and clean_phone in PRE_APPROVED_PERSONAS" in backend


def test_vercel_otp_has_no_static_personas_and_requires_single_consumption():
    send = source("api/send-otp.ts")
    verify = source("api/verify-otp.ts")
    assert "otpCode = '123456'" not in send
    assert "isTestPersona" not in send
    assert "enteredOtp === '123456'" not in verify
    assert "is_used=eq.false&expires_at=gt." in verify
    assert "auth/code-already-used" in verify


def test_payout_requires_verified_caller_and_owner_role():
    code = source("api/save-payout.ts")
    assert "Authentication is required to save payout details." in code
    assert "targetUserId = String(caller.sub)" in code
    assert "targetRole = caller.role" in code
    assert "user_id || 'usr_party'" not in code


def test_backend_production_rejects_insecure_defaults_and_testing_mode():
    code = source("backend/app/main.py")
    assert 'settings.SECRET_KEY.startswith("dev-insecure-")' in code
    assert 'settings.ADMIN_API_KEY.startswith("dev-insecure-")' in code
    assert '"TESTING mode must not be enabled in production"' in code


def test_admin_authorization_checks_authoritative_user():
    code = source("backend/app/core/security.py")
    assert "Administrative account not found" in code
    assert "Revoked admin token" in code
    assert "secrets.compare_digest(api_key, settings.ADMIN_API_KEY)" in code
