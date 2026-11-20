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

    # Validate 10-digit Indian mobile number
    if len(digits) != 10 or digits[0] not in "56789":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mobile number '{phone}'. Please provide a valid 10-digit Indian mobile number."
        )

    return digits

async def send_sms_otp(phone: str, otp: str, role: str = "customer") -> Dict[str, Any]:
    """
    Sends transactional SMS OTP using 2Factor.in SMS OTP API:
    https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/+91{ten_digit_phone}/{otp_code}/OTP1

    - Reads TWOFACTOR_API_KEY from environment variables (os.getenv("TWOFACTOR_API_KEY"))
    - Normalizes Indian phone numbers cleanly to 10 digits before formatting +91{ten_digit_phone}
    - Checks HTTP 200 response and JSON {"Status": "Success"}
    - Raises clear HTTP 502 / 400 errors with logged error details if 2Factor.in fails
    - Gracefully marks as pending_credentials in development/test environments when no key is set
    """
    ten_digit_phone = normalize_indian_phone(phone)

    # 1. Read TWOFACTOR_API_KEY from environment or settings
    api_key = (
        os.getenv("TWOFACTOR_API_KEY")
        or os.getenv("TWO_FACTOR_API_KEY")
        or getattr(settings, "RESOLVED_TWOFACTOR_API_KEY", "")
        or getattr(settings, "TWOFACTOR_API_KEY", "")
        or ""
    ).strip()

    masked_phone = f"+91 XXXXX {ten_digit_phone[-4:]}"

    # In development/test environments without SMS gateway credentials, gracefully pend
    if not api_key:
        if getattr(settings, "ENVIRONMENT", "").lower() == "production":
            logger.error("[SMS Gateway] CRITICAL: TWOFACTOR_API_KEY is not configured in production!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SMS gateway service is not configured in production environment."
            )
        logger.info(
            f"[SMS Gateway] TWOFACTOR_API_KEY not configured. "
            f"SMS delivery for {masked_phone} marked as pending."
        )
        return {
            "status": "pending_credentials",
            "provider": "2factor",
            "message": "SMS delivery pending TWOFACTOR_API_KEY configuration"
        }

    # 2. Format 2Factor.in transactional OTP endpoint
    template = getattr(settings, "SMS_TEMPLATE_ID", None) or "OTP1"
    endpoint_url = f"https://2factor.in/API/V1/{api_key}/SMS/+91{ten_digit_phone}/{otp}/{template}"

    logger.info(f"[SMS 2Factor] Dispatching transactional OTP to {masked_phone} via 2Factor.in...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(endpoint_url)
    except httpx.RequestError as exc:
        logger.error(f"[SMS 2Factor] Network error connecting to 2Factor.in for {masked_phone}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach SMS gateway (2Factor.in): {str(exc)}"
        )

    # 3. Check HTTP status 200 and JSON {"Status": "Success"}
    if resp.status_code == 200:
        try:
            res_data = resp.json()
        except Exception:
            res_data = {}

        if isinstance(res_data, dict) and res_data.get("Status") == "Success":
            session_id = res_data.get("Details", "")
            logger.info(f"[SMS 2Factor] OTP successfully delivered to {masked_phone}. Session: {session_id}")
            return {
                "status": "delivered",
                "provider": "2factor",
                "session_id": session_id,
                "message": "OTP delivered successfully via 2Factor.in"
            }
        else:
            err_detail = res_data.get("Details") if isinstance(res_data, dict) else resp.text
            logger.error(f"[SMS 2Factor] 2Factor.in rejected delivery for {masked_phone}: {err_detail}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"SMS OTP delivery failed via 2Factor.in: {err_detail}"
            )
    else:
        err_detail = resp.text
        try:
            err_json = resp.json()
            if isinstance(err_json, dict) and err_json.get("Details"):
                err_detail = err_json.get("Details")
        except Exception:
            pass

        logger.error(f"[SMS 2Factor] 2Factor.in returned HTTP {resp.status_code} for {masked_phone}: {err_detail}")
        err_status = status.HTTP_400_BAD_REQUEST if resp.status_code in (400, 422) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(
            status_code=err_status,
            detail=f"SMS gateway returned error ({resp.status_code}): {err_detail}"
        )
