import hmac
import hashlib
from typing import Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import Order, OrderTimeline, Refund
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
    Enforces user authorization (IDOR prevention), order state checks, and idempotency.
    """
    res = await db.execute(select(Order).where(Order.id == data.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user_id = payload.get("sub")
    role = payload.get("role")

    # 1. Authorization check: customer must own order, or must be admin
    if order.customer_id != user_id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify payment for this order"
        )

    # 2. State validation: Cannot verify payment for CANCELLED order
    if order.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay for a cancelled order"
        )

    # 3. Idempotency: If already marked PAID, return existing transaction status
    if order.payment_status == "PAID":
        return RazorpayVerifyResponse(
            status="SUCCESS",
            order_id=order.id,
            payment_id=order.transaction_id or data.razorpay_payment_id
        )

    # 4. Consistency: If order was bound to a specific razorpay order id, verify match
    if order.payment_order_id and order.payment_order_id != data.razorpay_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mismatched Razorpay order ID"
        )

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
    Validates currency is INR and amount matches expected order paise.
    """
    body_bytes = await request.body()
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing webhook signature")

    if not settings.RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

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
            currency = payment_entity.get("currency")
            amount = payment_entity.get("amount")

            if currency != "INR":
                raise HTTPException(status_code=400, detail=f"Invalid currency: {currency}")

            if rzp_order_id:
                res = await db.execute(select(Order).where(Order.payment_order_id == rzp_order_id))
                order = res.scalars().first()
                if order:
                    expected_paise = int(round(order.total_amount * 100))
                    if amount != expected_paise:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Amount mismatch: received {amount} paise, expected {expected_paise} paise"
                        )

                    if order.payment_status != "PAID":
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing error: {str(e)}")

    return {"status": "ok"}


class CreateRefundRequest(BaseModel):
    order_id: str
    amount: Optional[float] = None
    reason: Optional[str] = "Customer refund request"
    refund_type: Optional[str] = "FULL"
    admin_notes: Optional[str] = None

class RefundDetailResponse(BaseModel):
    id: str
    order_id: str
    payment_id: Optional[str]
    gateway_refund_id: Optional[str]
    amount: float
    currency: str
    reason: Optional[str]
    status: str
    refund_type: str
    created_at: str

@router.post("/refund", response_model=RefundDetailResponse)
async def process_refund(
    data: CreateRefundRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Processes authoritative order refund.
    Validates ownership, remaining refundable balance, and idempotency.
    Interacts with real Razorpay refund API if configured.
    Updates order payment status and timeline.
    """
    user_id = payload.get("sub")
    role = payload.get("role")

    res = await db.execute(select(Order).where(Order.id == data.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != user_id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request refund for this order"
        )

    # Calculate existing valid refunds for this order
    res_ref = await db.execute(
        select(Refund).where(
            Refund.order_id == order.id,
            Refund.status.in_(["COMPLETED", "PROCESSING", "PENDING"])
        )
    )
    existing_refunds = res_ref.scalars().all()
    total_already_refunded = sum(r.amount for r in existing_refunds)
    remaining_refundable = round(order.total_amount - total_already_refunded, 2)

    if remaining_refundable <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been fully refunded"
        )

    refund_amount = round(data.amount if data.amount is not None else remaining_refundable, 2)
    if refund_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount must be greater than zero"
        )
    if refund_amount > remaining_refundable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund amount (₹{refund_amount}) exceeds remaining refundable balance (₹{remaining_refundable})"
        )

    gateway_refund_id = None
    refund_status = "COMPLETED"

    if order.payment_method == "ONLINE" and order.transaction_id:
        if is_razorpay_configured():
            amount_paise = int(round(refund_amount * 100))
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"https://api.razorpay.com/v1/payments/{order.transaction_id}/refund",
                        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                        json={
                            "amount": amount_paise,
                            "notes": {"order_id": order.id, "reason": data.reason or "Customer refund"}
                        }
                    )
                    if resp.status_code not in (200, 201):
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Payment gateway refund failed: {resp.text}"
                        )
                    rzp_refund = resp.json()
                    gateway_refund_id = rzp_refund.get("id")
                    refund_status = "COMPLETED" if rzp_refund.get("status") in ("processed", "completed") else "PROCESSING"
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Payment gateway unreachable: {str(e)}"
                )
        else:
            import secrets
            gateway_refund_id = f"rfnd_test_{secrets.token_hex(6)}"
            refund_status = "COMPLETED"
    else:
        # COD Refund: Record as direct cash/UPI disbursement
        gateway_refund_id = f"cod_disb_{order.id[:8]}"
        refund_status = "COMPLETED"

    now = datetime.now(timezone.utc)
    new_refund = Refund(
        order_id=order.id,
        payment_id=order.transaction_id or f"cod_{order.id}",
        gateway_refund_id=gateway_refund_id,
        amount=refund_amount,
        currency="INR",
        reason=data.reason,
        status=refund_status,
        refund_type=data.refund_type or ("FULL" if refund_amount == order.total_amount else "PARTIAL"),
        created_by=user_id,
        admin_notes=data.admin_notes,
        created_at=now,
        updated_at=now
    )
    db.add(new_refund)

    if (total_already_refunded + refund_amount) >= order.total_amount:
        order.payment_status = "REFUNDED"
    else:
        order.payment_status = "PARTIALLY_REFUNDED"

    timeline_entry = OrderTimeline(
        order_id=order.id,
        status=order.status,
        title="रिफ़ंड सफल (Refund Processed)",
        description=f"Refund of ₹{refund_amount:.2f} processed. Reference: {gateway_refund_id}",
        timestamp=now
    )
    db.add(timeline_entry)
    await db.commit()
    await db.refresh(new_refund)

    return RefundDetailResponse(
        id=new_refund.id,
        order_id=new_refund.order_id,
        payment_id=new_refund.payment_id,
        gateway_refund_id=new_refund.gateway_refund_id,
        amount=new_refund.amount,
        currency=new_refund.currency,
        reason=new_refund.reason,
        status=new_refund.status,
        refund_type=new_refund.refund_type,
        created_at=new_refund.created_at.isoformat()
    )

@router.get("/refunds/{order_id}")
async def get_order_refunds(
    order_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches all refunds for a specific order with IDOR verification.
    """
    user_id = payload.get("sub")
    role = payload.get("role")

    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != user_id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view refunds for this order"
        )

    res_ref = await db.execute(select(Refund).where(Refund.order_id == order_id).order_by(Refund.created_at.desc()))
    refunds = res_ref.scalars().all()
    return [
        {
            "id": r.id,
            "order_id": r.order_id,
            "payment_id": r.payment_id,
            "gateway_refund_id": r.gateway_refund_id,
            "amount": r.amount,
            "currency": r.currency,
            "reason": r.reason,
            "status": r.status,
            "refund_type": r.refund_type,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in refunds
    ]
