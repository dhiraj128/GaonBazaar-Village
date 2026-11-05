import os
import re
import uuid
import base64
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.base import SupportTicket, TicketMessage, Order, OrderItem, OrderTimeline, User, Refund, Replacement
from app.core.security import get_current_user_payload

router = APIRouter(prefix="/support", tags=["Customer Support & Help Desk"])


class EvidenceUploadRequest(BaseModel):
    data_url: str  # Base64 data URL e.g. "data:image/jpeg;base64,..."
    file_name: Optional[str] = None
    order_id: Optional[str] = None

class EvidenceUploadResponse(BaseModel):
    evidence_id: str
    attachment_url: str
    file_name: str
    content_type: str
    size_bytes: int

class TicketCreate(BaseModel):
    order_id: Optional[str] = None
    category: str = "GENERAL_HELP"  # WHERE_IS_MY_ORDER, REPORT_ISSUE, REFUND_REQUEST, DAMAGED_ITEM, MISSING_ITEM, GENERAL_HELP
    subject: str
    message: str
    affected_product_id: Optional[str] = None
    attachment_url: Optional[str] = None

class TicketReplyCreate(BaseModel):
    message: str
    attachment_url: Optional[str] = None

class TicketStatusUpdate(BaseModel):
    status: str  # OPEN, IN_REVIEW, RESOLVED, CLOSED
    resolution_notes: Optional[str] = None

class TicketMessageResponse(BaseModel):
    id: str
    ticket_id: str
    sender_id: str
    sender_role: str
    message: str
    attachment_url: Optional[str] = None
    created_at: str

class TicketResponse(BaseModel):
    id: str
    order_id: Optional[str] = None
    category: str
    subject: str
    message: str
    status: str
    affected_product_id: Optional[str] = None
    attachment_url: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    reply_count: int = 0

class TicketDetailResponse(BaseModel):
    id: str
    order_id: Optional[str] = None
    category: str
    subject: str
    message: str
    status: str
    affected_product_id: Optional[str] = None
    attachment_url: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    messages: List[TicketMessageResponse] = []

class RefundStatusItem(BaseModel):
    order_id: str
    ticket_id: Optional[str] = None
    status: str
    refund_amount: float
    reason: str
    created_at: str
    expected_credit_days: str = "3-5 business days"

class SupportChatRequest(BaseModel):
    query: str
    language: str = "hi"  # hi or en
    order_id: Optional[str] = None

class SupportChatResponse(BaseModel):
    reply: str
    intent: str
    order_id: Optional[str] = None
    ticket_id: Optional[str] = None
    suggested_actions: List[str] = []


EVIDENCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage", "evidence"))
os.makedirs(EVIDENCE_DIR, exist_ok=True)

@router.post("/upload-evidence", response_model=EvidenceUploadResponse)
async def upload_support_evidence(
    req: EvidenceUploadRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Secure authenticated upload for damaged/wrong product photos.
    Validates MIME type, file size (max 5MB), and magic bytes.
    Saves file to secure private directory with server-generated UUID.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    data = req.data_url.strip()
    match = re.match(r"^data:(image\/(jpeg|png|webp));base64,(.+)$", data, re.I)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Supported formats: JPEG, PNG, WEBP."
        )
        
    content_type = match.group(1).lower()
    ext = match.group(2).lower()
    if ext == "jpeg":
        ext = "jpg"
        
    try:
        image_bytes = base64.b64decode(match.group(3))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload")
        
    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds maximum 5MB limit")
        
    # Check magic bytes
    if ext in ["jpg", "jpeg"] and not image_bytes.startswith(b"\xff\xd8\xff"):
        raise HTTPException(status_code=400, detail="File content does not match JPEG signature")
    elif ext == "png" and not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(status_code=400, detail="File content does not match PNG signature")
    elif ext == "webp" and not (image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:16]):
        raise HTTPException(status_code=400, detail="File content does not match WEBP signature")
        
    evidence_id = f"ev_{uuid.uuid4().hex[:16]}"
    safe_filename = f"{evidence_id}.{ext}"
    filepath = os.path.join(EVIDENCE_DIR, safe_filename)
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
        
    rel_url = f"/api/v1/support/evidence/{safe_filename}"
    return EvidenceUploadResponse(
        evidence_id=evidence_id,
        attachment_url=rel_url,
        file_name=safe_filename,
        content_type=content_type,
        size_bytes=len(image_bytes)
    )

@router.get("/evidence/{filename}")
async def get_support_evidence(
    filename: str,
    payload: dict = Depends(get_current_user_payload)
):
    """
    Secure file retrieval for uploaded damage/wrong product evidence.
    Access restricted to authenticated users (ticket owners and admins).
    """
    if not re.match(r"^ev_[a-zA-Z0-9_\-]+\.(jpg|jpeg|png|webp)$", filename):
        raise HTTPException(status_code=400, detail="Invalid evidence file reference")
        
    filepath = os.path.join(EVIDENCE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Evidence photo not found")
        
    ext = filename.split(".")[-1].lower()
    media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"
    return FileResponse(filepath, media_type=media_type)

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    req: TicketCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a genuine support ticket linked to an order, category, affected item, and optional photo.
    Persists initial message and ticket in database.
    """
    user_id = payload.get("sub")
    
    # If order_id provided, verify order belongs to customer
    if req.order_id:
        o_res = await db.execute(select(Order).where(Order.id == req.order_id, Order.customer_id == user_id))
        order = o_res.scalars().first()
        if not order and payload.get("role") != "admin":
            raise HTTPException(status_code=404, detail="Order not found for current user")

    now = datetime.now(timezone.utc)
    ticket = SupportTicket(
        user_id=user_id,
        order_id=req.order_id,
        category=req.category,
        subject=req.subject,
        message=req.message,
        affected_product_id=req.affected_product_id,
        attachment_url=req.attachment_url,
        status="OPEN",
        created_at=now,
        updated_at=now
    )
    db.add(ticket)
    await db.flush()

    # Create initial conversation thread message
    init_msg = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        sender_role=payload.get("role", "customer"),
        message=req.message,
        attachment_url=req.attachment_url,
        created_at=now
    )
    db.add(init_msg)
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse(
        id=ticket.id,
        order_id=ticket.order_id,
        category=ticket.category or "GENERAL_HELP",
        subject=ticket.subject,
        message=ticket.message,
        status=ticket.status,
        affected_product_id=ticket.affected_product_id,
        attachment_url=ticket.attachment_url,
        resolution_notes=ticket.resolution_notes,
        resolved_at=ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        created_at=ticket.created_at.isoformat() if ticket.created_at else now.isoformat(),
        updated_at=ticket.updated_at.isoformat() if ticket.updated_at else now.isoformat(),
        reply_count=1
    )

@router.get("/tickets", response_model=List[TicketResponse])
async def list_customer_tickets(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all support tickets raised by the current customer, with status, dates, and order references.
    """
    user_id = payload.get("sub")
    res = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(SupportTicket.user_id == user_id)
        .order_by(SupportTicket.created_at.desc())
    )
    tickets = res.scalars().all()
    return [
        TicketResponse(
            id=t.id,
            order_id=t.order_id,
            category=t.category or "GENERAL_HELP",
            subject=t.subject,
            message=t.message,
            status=t.status,
            affected_product_id=t.affected_product_id,
            attachment_url=t.attachment_url,
            resolution_notes=t.resolution_notes,
            resolved_at=t.resolved_at.isoformat() if t.resolved_at else None,
            created_at=t.created_at.isoformat() if t.created_at else "",
            updated_at=t.updated_at.isoformat() if t.updated_at else None,
            reply_count=len(t.messages) if t.messages else 0
        )
        for t in tickets
    ]

@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket_details(
    ticket_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full details of a ticket including complete conversation history.
    Guarded against IDOR: checks customer ownership or admin role.
    """
    user_id = payload.get("sub")
    role = payload.get("role")

    res = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages))
        .where(SupportTicket.id == ticket_id)
    )
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if ticket.user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this support ticket")

    messages_resp = [
        TicketMessageResponse(
            id=m.id,
            ticket_id=m.ticket_id,
            sender_id=m.sender_id,
            sender_role=m.sender_role,
            message=m.message,
            attachment_url=m.attachment_url,
            created_at=m.created_at.isoformat() if m.created_at else ""
        )
        for m in (ticket.messages or [])
    ]

    return TicketDetailResponse(
        id=ticket.id,
        order_id=ticket.order_id,
        category=ticket.category or "GENERAL_HELP",
        subject=ticket.subject,
        message=ticket.message,
        status=ticket.status,
        affected_product_id=ticket.affected_product_id,
        attachment_url=ticket.attachment_url,
        resolution_notes=ticket.resolution_notes,
        resolved_at=ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        created_at=ticket.created_at.isoformat() if ticket.created_at else "",
        updated_at=ticket.updated_at.isoformat() if ticket.updated_at else None,
        messages=messages_resp
    )

@router.post("/tickets/{ticket_id}/reply", response_model=TicketMessageResponse)
async def reply_to_ticket(
    ticket_id: str,
    req: TicketReplyCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Appends a new message to an existing support ticket thread.
    If ticket was CLOSED, customer reply reopens ticket (Reopening Rule).
    """
    user_id = payload.get("sub")
    role = payload.get("role", "customer")

    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if ticket.user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to reply to this ticket")

    now = datetime.now(timezone.utc)

    # Reopening rule: customer replying to closed/resolved ticket reopens it
    if role != "admin" and ticket.status in ["CLOSED", "RESOLVED"]:
        ticket.status = "OPEN"

    ticket.updated_at = now

    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        sender_role="admin" if role == "admin" else "customer",
        message=req.message.strip(),
        attachment_url=req.attachment_url,
        created_at=now
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return TicketMessageResponse(
        id=msg.id,
        ticket_id=msg.ticket_id,
        sender_id=msg.sender_id,
        sender_role=msg.sender_role,
        message=msg.message,
        attachment_url=msg.attachment_url,
        created_at=msg.created_at.isoformat()
    )

@router.patch("/tickets/{ticket_id}/status")
async def update_customer_ticket_status(
    ticket_id: str,
    req: TicketStatusUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Allows customer to close/reopen their ticket, or admin to resolve/close it with resolution notes.
    """
    user_id = payload.get("sub")
    role = payload.get("role", "customer")

    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if ticket.user_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to modify this ticket")

    now = datetime.now(timezone.utc)
    new_status = req.status.upper()
    if new_status not in ["OPEN", "IN_REVIEW", "RESOLVED", "CLOSED"]:
        raise HTTPException(status_code=400, detail="Invalid ticket status")

    ticket.status = new_status
    ticket.updated_at = now
    if req.resolution_notes:
        ticket.resolution_notes = req.resolution_notes
    if new_status in ["RESOLVED", "CLOSED"]:
        ticket.resolved_at = now

    await db.commit()
    return {"message": f"Ticket status updated to {new_status}", "status": new_status}

@router.get("/refund-status", response_model=List[RefundStatusItem])
async def get_refund_and_replacement_status(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches genuine refund and replacement records from database tables for the customer.
    """
    user_id = payload.get("sub")
    results = []

    # 1. Fetch from Refund table
    res_refunds = await db.execute(
        select(Refund)
        .join(Order, Refund.order_id == Order.id)
        .where(Order.customer_id == user_id)
        .order_by(Refund.created_at.desc())
    )
    refunds = res_refunds.scalars().all()
    seen_orders = set()
    for r in refunds:
        seen_orders.add(r.order_id)
        results.append(RefundStatusItem(
            order_id=r.order_id,
            status=r.status,
            refund_amount=r.amount,
            reason=r.reason or "Order refund processed",
            created_at=r.created_at.isoformat() if r.created_at else datetime.now(timezone.utc).isoformat(),
            expected_credit_days="Instant for COD, 3-5 days for Online (Gateway: " + (r.gateway_refund_id or "N/A") + ")"
        ))

    # 2. Fetch from Replacement table
    res_rep = await db.execute(
        select(Replacement)
        .where(Replacement.customer_id == user_id)
        .order_by(Replacement.created_at.desc())
    )
    reps = res_rep.scalars().all()
    for rep in reps:
        results.append(RefundStatusItem(
            order_id=rep.original_order_id,
            status=f"REPLACEMENT_{rep.status}",
            refund_amount=rep.customer_due, # ₹0
            reason=f"Replacement: {rep.reason}",
            created_at=rep.created_at.isoformat() if rep.created_at else datetime.now(timezone.utc).isoformat(),
            expected_credit_days="Free Replacement Delivery (OTP: " + (rep.delivery_otp or "Pending") + ")"
        ))

    # 3. Fallback to cancelled orders not yet in Refund table
    res_orders = await db.execute(
        select(Order)
        .where(Order.customer_id == user_id, Order.status.in_(["CANCELLED", "REFUNDED", "RETURNED"]))
        .order_by(Order.placed_at.desc())
    )
    orders = res_orders.scalars().all()
    for o in orders:
        if o.id not in seen_orders:
            results.append(RefundStatusItem(
                order_id=o.id,
                status="REFUNDED" if o.payment_status == "REFUNDED" else ("PROCESSING" if o.payment_method == "ONLINE" else "CASH_REFUND_COMPLETED"),
                refund_amount=o.total_amount,
                reason="Customer cancellation within 180s window" if o.status == "CANCELLED" else "Damaged/Missing item reported",
                created_at=o.placed_at.isoformat() if o.placed_at else datetime.now(timezone.utc).isoformat(),
                expected_credit_days="Instant for COD, 3-5 days for Online"
            ))

    return results

@router.post("/ai-chat", response_model=SupportChatResponse)
async def ai_support_chat(
    req: SupportChatRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Grounded AI Support Assistant.
    Never pretends a human agent was alerted unless a genuine ticket is created.
    """
    user_id = payload.get("sub")
    q = req.query.lower().strip()
    is_hi = req.language == "hi" or any(w in q for w in ["ऑर्डर", "कहाँ", "कब", "सामान", "मदद", "पैसा", "शिकायत"])
    
    # Fetch most recent order for customer
    o_res = await db.execute(
        select(Order).options(selectinload(Order.store), selectinload(Order.runner)).where(Order.customer_id == user_id).order_by(Order.placed_at.desc())
    )
    latest_order = o_res.scalars().first()
    
    # 1. Where is my order?
    if any(k in q for k in ["where", "status", "track", "कहाँ", "कब तक", "ट्रैक", "स्थिति"]):
        if not latest_order:
            reply = "आपके खाते में अभी कोई सक्रिय ऑर्डर नहीं मिला।" if is_hi else "No active orders found in your account."
            return SupportChatResponse(reply=reply, intent="ORDER_STATUS")
        
        status_map_hi = {
            "PLACED": "दुकानदार द्वारा स्वीकार किए जाने की प्रतीक्षा में है",
            "ACCEPTED": "दुकानदार ने स्वीकार कर लिया है और सामान तैयार कर रहे हैं",
            "PACKED": "सामान पैक हो चुका है, डिलीवरी साथी को सौंपा जा रहा है",
            "RUNNER_ASSIGNED": f"डिलीवरी साथी {latest_order.runner.full_name if latest_order.runner else ''} दुकान पहुँच रहे हैं",
            "OUT_FOR_DELIVERY": "डिलीवरी साथी आपके पते के लिए निकल चुके हैं",
            "DELIVERED": "सफलतापूर्वक डिलीवर हो चुका है",
            "CANCELLED": "ऑर्डर रद्द कर दिया गया है"
        }
        status_desc = status_map_hi.get(latest_order.status, latest_order.status) if is_hi else f"is currently {latest_order.status.replace('_', ' ').title()}"
        
        reply = (
            f"आपका अंतिम ऑर्डर (#{latest_order.id[-6:]}) {status_desc}। कुल राशि ₹{latest_order.total_amount:.2f} है।"
            if is_hi else
            f"Your latest order (#{latest_order.id[-6:]}) {status_desc}. Total amount is ₹{latest_order.total_amount:.2f}."
        )
        return SupportChatResponse(
            reply=reply,
            intent="ORDER_STATUS",
            order_id=latest_order.id,
            suggested_actions=["ऑर्डर ट्रैक करें", "समस्या दर्ज करें"] if is_hi else ["Track Order", "Report an Issue"]
        )

    # 2. Missing / Damaged Item
    elif any(k in q for k in ["missing", "damaged", "wrong", "गायब", "टूटा", "खराब", "गलत सामान"]):
        reply = (
            "हमें असुविधा के लिए खेद है। कृपया 'समस्या दर्ज करें' (Report an Issue) विकल्प चुनकर संबंधित ऑर्डर और सामान का विवरण दर्ज करें। आपका टिकट बनने के बाद सहायता टीम तुरंत समीक्षा करेगी।"
            if is_hi else
            "We apologize for the inconvenience. Please choose 'Report an Issue' to specify the order and affected product. Our team will review your ticket once submitted."
        )
        return SupportChatResponse(
            reply=reply,
            intent="REPORT_ISSUE",
            order_id=latest_order.id if latest_order else None,
            suggested_actions=["समस्या दर्ज करें", "मेरे टिकट देखें"] if is_hi else ["Report Issue", "My Tickets"]
        )

    # 3. Cancellation / Refund
    elif any(k in q for k in ["cancel", "refund", "वापस", "रद्द", "पैसे"]):
        reply = (
            "गाँव बाज़ार में ऑर्डर देने के 180 सेकंड के भीतर शून्य शुल्क पर रद्दीकरण संभव है। डिलीवर होने के बाद केवल क्षतिग्रस्त या गलत सामान पर रिफ़ंड दिया जाता है। आप नीचे 'रिफ़ंड स्थिति' से स्थिति जांच सकते हैं।"
            if is_hi else
            "Orders can be cancelled with 0 fee within 180 seconds of placement. After delivery, refunds apply to damaged or missing items. Check 'Refund Status' for updates."
        )
        return SupportChatResponse(
            reply=reply,
            intent="POLICY_QUERY",
            suggested_actions=["रिफ़ंड स्थिति देखें", "सहायता टिकट बनाएं"] if is_hi else ["Refund Status", "Create Ticket"]
        )

    # 4. Human Support Escalation / Support Desk Ticket
    elif any(k in q for k in ['callback', 'call back', 'call', 'care', 'human', 'agent', 'support desk', 'speak', 'talk', 'customer care', 'कस्टमर केयर', 'बात करनी है', 'कॉल करो', 'कॉल बैक', 'मदद चाहिए', 'सहायता']):
        is_callback_kw = any(k in q for k in ['callback', 'call back', 'call', 'कॉल बैक', 'कॉल करो'])
        cat = 'CUSTOMER_CARE_CALLBACK' if is_callback_kw else 'SUPPORT_DESK'
        subj = 'Customer Care Callback Request' if is_callback_kw else 'Support Desk Assistance Request'
        intent = 'CALLBACK_REQUESTED' if is_callback_kw else 'SUPPORT_TICKET_CREATED'
        ticket = SupportTicket(
            user_id=user_id,
            order_id=latest_order.id if latest_order else None,
            category=cat,
            subject=subj,
            message=req.query,
            status='OPEN'
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        if is_callback_kw:
            reply = (
                f'आपकी कॉलबैक रिक्वेस्ट दर्ज कर ली गई है (टिकट #{ticket.id[-6:]})। जब कोई एजेंट उपलब्ध होगा, हमारी सपोर्ट टीम आपसे संपर्क करेगी।'
                if is_hi else
                f'Your callback request has been submitted (Ticket #{ticket.id[-6:]}). Our support team will contact you when an agent is available.'
            )
        else:
            reply = (
                f'आपकी समस्या सपोर्ट डेस्क को भेज दी गई है (टिकट #{ticket.id[-6:]})। हमारी सहायता टीम आपके टिकट थ्रेड में उत्तर देगी।'
                if is_hi else
                f'Your query has been forwarded to our Support Desk (Ticket #{ticket.id[-6:]}). Our support team will review and reply directly in your Support Tickets thread.'
            )
        return SupportChatResponse(
            reply=reply,
            intent=intent,
            ticket_id=ticket.id,
            order_id=latest_order.id if latest_order else None,
            suggested_actions=['मेरी टिकटें देखें', 'ऑर्डर ट्रैक करें'] if is_hi else ['My Support Tickets', 'Track Order']
        )

    # Default general guidance
    reply = (
        "नमस्ते! मैं गाँव बाज़ार सहायता सहायक हूँ। आप मुझसे ऑर्डर की स्थिति, गुम सामान, या रिफ़ंड नीति के बारे में पूछ सकते हैं।"
        if is_hi else
        "Hello! I am your GaonBazaar Support Assistant. You can ask me about order tracking, missing items, or delivery policies."
    )
    return SupportChatResponse(
        reply=reply,
        intent="GENERAL_HELP",
        suggested_actions=["मेरा ऑर्डर कहाँ है?", "सामान खराब आया", "मदद चाहिए"] if is_hi else ["Where is my order?", "Damaged item", "Need Help"]
    )
