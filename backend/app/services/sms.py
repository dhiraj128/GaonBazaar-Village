import os
import re
import logging
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from app.core.config import settings

logger = logging.getLogger("gaonbazaar.sms")

def normalize_indian_phone(phone: str) -> str:
    """
    Normalizes any Indian mobile phone number representation cleanly to 10 digits
    before formatting for the 2Factor.in SMS OTP API (+91{ten_digit_phone}).
    
    Handles:
    - Raw 10 digits: "9876543210"
    - +91 country prefix: "+919876543210" or "+91 98765-43210"
    - 91 prefix without plus: "919876543210"
    - Leading 0 trunk prefix: "09876543210"
    - Spaces, hyphens, and parentheses
    
    Validates that the resulting string is strictly a 10-digit number.
    """
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required."
        )

    # Extract all digits
    digits = re.sub(r"\D", "", str(phone).strip())

    # Handle 12-digit format with 91 country code prefix
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    # Handle 11-digit format with leading 0
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    # Validate 10-digit Indian mobile number (strictly starts with 6-9)
    if len(digits) != 10 or digits[0] not in "6789":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mobile number '{phone}'. Please provide a valid 10-digit Indian mobile number."
        )

    return digits

_sms_http_client: Optional[httpx.AsyncClient] = None

def get_sms_http_client() -> httpx.AsyncClient:
    global _sms_http_client
    if _sms_http_client is None or _sms_http_client.is_closed:
        _sms_http_client = httpx.AsyncClient(timeout=5.0)
    return _sms_http_client

async def send_sms_otp(phone: str, otp: Optional[str] = None, role: str = "customer") -> Dict[str, Any]:
    """
    Sends transactional 6-digit SMS OTP using official 2Factor.in SMS OTP API:
    GET https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/+91{ten_digit_phone}/AUTOGEN/{template_name}

    - Reads TWOFACTOR_API_KEY from environment variables (trimmed)
    - Reads TWOFACTOR_OTP_TEMPLATE from environment variable (default "OTP1", URL-encoded)
    - Strictly normalizes Indian numbers to 10 digits starting with 6–9 and sends as +91{phone}
    - ZERO voice fallback endpoints
    - Employs shared pooled httpx.AsyncClient with a tight 5-second timeout
    - Logs HTTP status and sanitized JSON response (Status, Details), never logging the API key
    - Returns 2Factor session_id from response Details
    - Raises clear HTTP 502 / 400 errors with logged error details if 2Factor.in fails
    """
    import urllib.parse

    ten_digit_phone = normalize_indian_phone(phone)

    # 1. Read TWOFACTOR_API_KEY from environment or settings (strictly trimmed)
    api_key = (
        os.getenv("TWOFACTOR_API_KEY")
        or os.getenv("TWO_FACTOR_API_KEY")
        or getattr(settings, "RESOLVED_TWOFACTOR_API_KEY", "")
        or getattr(settings, "TWOFACTOR_API_KEY", "")
        or ""
    ).strip()

    # 2. Read template name from environment or settings (URL-encoded, stripped of whitespace)
    raw_template = (
        os.getenv("TWOFACTOR_OTP_TEMPLATE")
        or getattr(settings, "TWOFACTOR_OTP_TEMPLATE", "")
        or getattr(settings, "SMS_TEMPLATE_ID", "")
        or "OTP1"
    ).strip()
    template = urllib.parse.quote(raw_template)

    masked_phone = f"+91 XXXXX {ten_digit_phone[-4:]}"

    # In development/test environments without SMS gateway credentials, gracefully pend
    if not api_key:
        if getattr(settings, "ENVIRONMENT", "").lower() == "production":
            logger.error("[SMS Gateway] CRITICAL: TWOFACTOR_API_KEY is not configured in production!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SMS gateway service is not configured in production environment (missing TWOFACTOR_API_KEY)."
            )
        logger.info(
            f"[SMS Gateway] TWOFACTOR_API_KEY not configured. "
            f"SMS delivery for {masked_phone} marked as pending."
        )
        return {
            "status": "pending_credentials",
            "provider": "2factor",
            "session_id": f"sess_mock_{ten_digit_phone}",
            "message": "SMS delivery pending TWOFACTOR_API_KEY configuration"
        }

    # 3. Format official 2Factor.in transactional SMS OTP AUTOGEN endpoint
    endpoint_url = f"https://2factor.in/API/V1/{api_key}/SMS/+91{ten_digit_phone}/AUTOGEN/{template}"

    logger.info(f"[SMS 2Factor] Dispatching transactional OTP to {masked_phone} via 2Factor.in (AUTOGEN/{raw_template})...")

    try:
        client = get_sms_http_client()
        resp = await client.get(endpoint_url)
    except httpx.RequestError as exc:
        logger.error(f"[SMS 2Factor] Network error connecting to 2Factor.in for {masked_phone}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach SMS gateway (2Factor.in): {str(exc)}"
        )

    # 4. Check HTTP status and sanitized 2Factor.in JSON response (Status, Details)
    try:
        res_data = resp.json()
    except Exception:
        res_data = {}

    provider_status = res_data.get("Status") if isinstance(res_data, dict) else None
    provider_details = res_data.get("Details") if isinstance(res_data, dict) else (resp.text[:100] if resp.text else None)

    logger.info(
        f"[SMS 2Factor] Response for {masked_phone}: HTTP {resp.status_code}, "
        f"Provider Status={provider_status}, Details={provider_details}"
    )

    if resp.status_code == 200:
        if isinstance(res_data, dict) and res_data.get("Status") == "Success":
            session_id = str(res_data.get("Details", "")).strip()
            logger.info(f"[SMS 2Factor] OTP successfully dispatched to {masked_phone}. Session: {session_id}")
            return {
                "status": "delivered",
                "provider": "2factor",
                "session_id": session_id,
                "message": "OTP dispatched successfully via 2Factor.in (OTP1)"
            }
        else:
            err_detail = res_data.get("Details") if isinstance(res_data, dict) else resp.text
            logger.error(f"[SMS 2Factor] 2Factor.in rejected delivery for {masked_phone}: {err_detail}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"SMS OTP delivery failed via 2Factor.in: {err_detail}"
            )
    else:
        err_detail = provider_details or resp.text
        logger.error(f"[SMS 2Factor] 2Factor.in returned HTTP {resp.status_code} for {masked_phone}: {err_detail}")
        err_status = status.HTTP_400_BAD_REQUEST if resp.status_code in (400, 422) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(
            status_code=err_status,
            detail=f"SMS gateway returned error ({resp.status_code}): {err_detail}"
        )

async def verify_sms_otp(session_id: str, otp: str) -> Dict[str, Any]:
    """
    Verifies a 6-digit SMS OTP against 2Factor.in verification API:
    GET https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/VERIFY/{session_id}/{otp_code}

    - Validates matching status: 'OTP Matched'
    - Detects expired OTP: 'OTP Expired'
    - Detects mismatch: 'OTP Mismatch'
    """
    if not session_id or not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID and 6-digit OTP code are required for verification."
        )

    api_key = (
        os.getenv("TWOFACTOR_API_KEY")
        or os.getenv("TWO_FACTOR_API_KEY")
        or getattr(settings, "RESOLVED_TWOFACTOR_API_KEY", "")
        or getattr(settings, "TWOFACTOR_API_KEY", "")
        or ""
    ).strip()

    if not api_key:
        logger.error("[SMS Gateway] TWOFACTOR_API_KEY is not configured for OTP verification.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMS gateway verification service is not configured (missing TWOFACTOR_API_KEY)."
        )

    verify_url = f"https://2factor.in/API/V1/{api_key}/SMS/VERIFY/{session_id}/{otp}"
    logger.info(f"[SMS 2Factor] Verifying OTP against session {session_id[:8]}... via 2Factor.in")

    try:
        client = get_sms_http_client()
        resp = await client.get(verify_url)
    except httpx.RequestError as exc:
        logger.error(f"[SMS 2Factor] Network error verifying OTP: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach SMS gateway verification service: {str(exc)}"
        )

    try:
        res_data = resp.json()
    except Exception:
        res_data = {}

    provider_status = res_data.get("Status") if isinstance(res_data, dict) else None
    provider_details = str(res_data.get("Details", "") if isinstance(res_data, dict) else resp.text)

    logger.info(f"[SMS 2Factor] Verify response: HTTP {resp.status_code}, Status={provider_status}, Details={provider_details}")

    if resp.status_code == 200 and provider_status == "Success":
        if "matched" in provider_details.lower():
            return {
                "status": "matched",
                "session_id": session_id,
                "message": "OTP verified successfully via 2Factor.in"
            }

    if "expired" in provider_details.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new OTP."
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect verification code. Please check your SMS and try again."
    )

