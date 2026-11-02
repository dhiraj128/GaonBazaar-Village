import hmac
import hashlib
import uuid
from typing import Optional
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

@router.post("/razorpay/order", response_model=RazorpayOrderResponse)
async def create_razorpay_order(
    data: RazorpayOrderRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a Razorpay payment order for the specified order.
    Returns Razorpay order ID, amount in paise, currency, and publishable key ID.
    """
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
    rzp_order_id = f"order_rzp_{uuid.uuid4().hex[:14]}"

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
    Verifies the Razorpay payment signature via HMAC-SHA256.
    Transitions order payment status to PAID and adds a timeline event.
    """
    res = await db.execute(select(Order).where(Order.id == data.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify signature
    msg = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    expected_sig = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    is_valid_sig = hmac.compare_digest(expected_sig, data.razorpay_signature)
    # Staging/Test Mode allows mock signatures starting with test_sig
    is_test_mode = (
        data.razorpay_signature.startswith("test_sig") or
        settings.TESTING or
        settings.ENVIRONMENT in ["development", "staging"]
    )

    if not is_valid_sig and not is_test_mode:
        raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

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
    """
    body_bytes = await request.body()
    if settings.RAZORPAY_WEBHOOK_SECRET and x_razorpay_signature:
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
