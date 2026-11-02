import hmac
import hashlib
from typing import Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import Order, OrderTimeline
from app.core.security import get_current_user_payload
from app.core.config import settings
from datetime import datetime, timezone

router = APIRouter(prefix="/payments", tags=["Payments & Checkout"])

class RazorpayOrderRequest(BaseModel):
    order_id: str

class RazorpayOrderResponse(BaseModel):
    id: str
    amount: int  # in paise
    currency: str
    key_id: str
    name: str
    description: str

class RazorpayVerifyRequest(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class RazorpayVerifyResponse(BaseModel):
    status: str
    order_id: str
    payment_id: str

def is_razorpay_configured() -> bool:
    """
    Checks if active, genuine Razorpay merchant credentials are configured.
    Returns False for default placeholder/dummy values.
    """
    key_id = (settings.RAZORPAY_KEY_ID or "").strip()
    key_secret = (settings.RAZORPAY_KEY_SECRET or "").strip()
    if not key_id or not key_secret:
        return False
    if "GaonBazaarVillage" in key_id or "placeholder" in key_id.lower() or "test_secret_GaonBazaar" in key_secret:
        return False
    return True

@router.get("/status")
async def get_payment_gateway_status():
    """
    Status endpoint for frontend payment gateway availability check.
    """
    configured = is_razorpay_configured()
    return {
        "online_enabled": configured,
        "cod_enabled": True,
        "default_method": "COD",
        "key_id": settings.RAZORPAY_KEY_ID if configured else None,
        "message": (
            "Online payment gateway active"
            if configured
            else "Online payments unconfigured. Cash on Delivery (COD) is 100% operational."
        )
    }

@router.post("/razorpay/order", response_model=RazorpayOrderResponse)
async def create_razorpay_order(
    data: RazorpayOrderRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a genuine Razorpay payment order via Razorpay API.
    If credentials are unconfigured or absent, cleanly returns 503 prompting Cash on Delivery (COD).
    """
    if not is_razorpay_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Online payment gateway is not configured with active merchant credentials. Please choose Cash on Delivery (COD)."
        )

    user_id = payload.get("sub")
    res = await db.execute(select(Order).where(Order.id == data.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != user_id and payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to pay for this order")

    if order.payment_status == "PAID":
        raise HTTPException(status_code=400, detail="Order is already paid")

    amount_paise = int(round(order.total_amount * 100))

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.razorpay.com/v1/orders",
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                json={
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": f"rcpt_{order.id[:8]}",
                    "notes": {"order_id": order.id}
                }
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Payment gateway communication failed. Please choose Cash on Delivery (COD)."
                )
            rzp_data = resp.json()
            rzp_order_id = rzp_data["id"]
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Online payment gateway unreachable. Please choose Cash on Delivery (COD)."
        )

    order.payment_order_id = rzp_order_id
    order.payment_method = "ONLINE"
    await db.commit()

    return RazorpayOrderResponse(
        id=rzp_order_id,
        amount=amount_paise,
        currency="INR",
        key_id=settings.RAZORPAY_KEY_ID,
        name="GaonBazaar Village",
        description=f"Order #{order.id[:8]} payment"
    )

@router.post("/razorpay/verify", response_model=RazorpayVerifyResponse)
async def verify_razorpay_payment(
    data: RazorpayVerifyRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies the Razorpay payment signature via strict HMAC-SHA256.
    Transitions order payment status to PAID and records a timeline event.
    Mock signatures and bypasses (test_sig) are strictly forbidden.
    """
    res = await db.execute(select(Order).where(Order.id == data.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Strict HMAC-SHA256 signature verification
    msg = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    expected_sig = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, data.razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay payment signature"
        )

    now = datetime.now(timezone.utc)
    order.payment_status = "PAID"
    order.payment_method = "ONLINE"
    order.payment_order_id = data.razorpay_order_id
    order.transaction_id = data.razorpay_payment_id

    timeline_entry = OrderTimeline(
        order_id=order.id,
        status=order.status,
        title="ऑनलाइन भुगतान सफल (Payment Successful)",
        description=f"Razorpay Payment ID: {data.razorpay_payment_id}, Amount: ₹{order.total_amount:.2f}",
        timestamp=now
    )
    db.add(timeline_entry)
    await db.commit()

    return RazorpayVerifyResponse(
        status="SUCCESS",
        order_id=order.id,
        payment_id=data.razorpay_payment_id
    )

@router.post("/razorpay/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Handles Razorpay server-to-server webhooks (e.g. payment.captured).
    Strictly verifies webhook HMAC-SHA256 signature before processing.
    """
    body_bytes = await request.body()
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing webhook signature")

    expected_sig = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        import json
        payload_data = json.loads(body_bytes.decode("utf-8"))
        event = payload_data.get("event")
        if event == "payment.captured":
            payment_entity = payload_data.get("payload", {}).get("payment", {}).get("entity", {})
            rzp_order_id = payment_entity.get("order_id")
            rzp_payment_id = payment_entity.get("id")
            if rzp_order_id:
                res = await db.execute(select(Order).where(Order.payment_order_id == rzp_order_id))
                order = res.scalars().first()
                if order and order.payment_status != "PAID":
                    order.payment_status = "PAID"
                    order.transaction_id = rzp_payment_id
                    order.payment_method = "ONLINE"
                    now = datetime.now(timezone.utc)
                    db.add(OrderTimeline(
                        order_id=order.id,
                        status=order.status,
                        title="ऑनलाइन भुगतान सफल (Payment Captured via Webhook)",
                        description=f"Razorpay Payment ID: {rzp_payment_id}",
                        timestamp=now
                    ))
                    await db.commit()
    except Exception:
        pass

    return {"status": "ok"}
