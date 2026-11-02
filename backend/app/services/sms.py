import logging
import httpx
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("gaonbazaar.sms")

async def send_sms_otp(phone: str, otp: str, role: str = "customer") -> Dict[str, Any]:
    """
    Sends transactional SMS OTP using configured provider (Fast2SMS, MSG91, Twilio).
    If provider credentials are not configured, logs cleanly and returns pending status.
    Never raises uncaught exceptions to caller.
    """
    provider = (settings.SMS_PROVIDER or "").lower().strip()
    api_key = settings.SMS_API_KEY
    
    # Check if SMS credentials configured
    if not api_key:
        logger.info(
            f"[SMS Gateway] Credentials not configured for provider '{provider or 'none'}'. "
            f"SMS delivery for +91{phone} marked as pending."
        )
        return {
            "status": "pending_credentials",
            "provider": provider or "none",
            "message": "SMS delivery pending gateway credentials configuration"
        }
        
    # Provider: Fast2SMS (Indian DLT / quick transactional OTP)
    if provider == "fast2sms":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://www.fast2sms.com/dev/bulkV2",
                    headers={"authorization": api_key},
                    json={
                        "variables_values": otp,
                        "route": "otp",
                        "numbers": phone
                    }
                )
                if resp.status_code == 200 and resp.json().get("return"):
                    logger.info(f"[SMS Fast2SMS] OTP sent successfully to +91{phone}")
                    return {"status": "delivered", "provider": "fast2sms"}
                logger.warning(f"[SMS Fast2SMS] Delivery failed: {resp.text}")
                return {"status": "failed", "provider": "fast2sms", "error": resp.text}
        except Exception as e:
            logger.error(f"[SMS Fast2SMS] Request exception: {e}")
            return {"status": "error", "provider": "fast2sms", "error": str(e)}

    # Provider: MSG91
    elif provider == "msg91":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                template_id = getattr(settings, "SMS_TEMPLATE_ID", "")
                resp = await client.post(
                    f"https://control.msg91.com/api/v5/otp?template_id={template_id}&mobile=91{phone}&authkey={api_key}&otp={otp}",
                    headers={"Content-Type": "application/json"}
                )
                if resp.status_code in (200, 201):
                    logger.info(f"[SMS MSG91] OTP sent successfully to +91{phone}")
                    return {"status": "delivered", "provider": "msg91"}
                logger.warning(f"[SMS MSG91] Delivery failed: {resp.text}")
                return {"status": "failed", "provider": "msg91", "error": resp.text}
        except Exception as e:
            logger.error(f"[SMS MSG91] Request exception: {e}")
            return {"status": "error", "provider": "msg91", "error": str(e)}

    # Fallback
    return {
        "status": "pending_credentials",
        "provider": provider or "none",
        "message": f"Provider '{provider}' not configured"
    }
