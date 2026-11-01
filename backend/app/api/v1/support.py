from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.base import SupportTicket, Order, User
from app.core.security import get_current_user_payload

router = APIRouter(prefix="/support", tags=["Customer Support & Help Desk"])

class TicketCreate(BaseModel):
    order_id: Optional[str] = None
    subject: str
    message: str

class TicketResponse(BaseModel):
    id: str
    order_id: Optional[str] = None
    subject: str
    message: str
    status: str
    created_at: str

class SupportChatRequest(BaseModel):
    query: str
    language: str = "hi" # hi or en
    order_id: Optional[str] = None

class SupportChatResponse(BaseModel):
    reply: str
    intent: str
    order_id: Optional[str] = None
    suggested_actions: List[str] = []

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    req: TicketCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    
    # If order_id provided, verify order belongs to customer
    if req.order_id:
        o_res = await db.execute(select(Order).where(Order.id == req.order_id, Order.customer_id == user_id))
        order = o_res.scalars().first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found for current user")

    ticket = SupportTicket(
        user_id=user_id,
        order_id=req.order_id,
        subject=req.subject,
        message=req.message,
        status="OPEN"
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse(
        id=ticket.id,
        order_id=ticket.order_id,
        subject=ticket.subject,
        message=ticket.message,
        status=ticket.status,
        created_at=ticket.created_at.isoformat() if ticket.created_at else datetime.now(timezone.utc).isoformat()
    )

@router.get("/tickets", response_model=List[TicketResponse])
async def list_customer_tickets(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(
        select(SupportTicket).where(SupportTicket.user_id == user_id).order_by(SupportTicket.created_at.desc())
    )
    tickets = res.scalars().all()
    return [
        TicketResponse(
            id=t.id,
            order_id=t.order_id,
            subject=t.subject,
            message=t.message,
            status=t.status,
            created_at=t.created_at.isoformat() if t.created_at else ""
        )
        for t in tickets
    ]

@router.post("/ai-chat", response_model=SupportChatResponse)
async def ai_support_chat(
    req: SupportChatRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
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
            "हमें असुविधा के लिए खेद है। यदि कोई सामान गायब या क्षतिग्रस्त है, तो कृपया नीचे दिए बटन से तुरंत शिकायत दर्ज करें। हमारी टीम 30 मिनट में सत्यापन करेगी।"
            if is_hi else
            "We apologize for the inconvenience. If an item is missing or damaged, please tap below to report it. Our support team will review within 30 minutes."
        )
        return SupportChatResponse(
            reply=reply,
            intent="REPORT_ISSUE",
            order_id=latest_order.id if latest_order else None,
            suggested_actions=["शिकायत दर्ज करें", "कॉल सहायता"] if is_hi else ["Report Issue", "Call Support"]
        )

    # 3. Cancellation / Refund
    elif any(k in q for k in ["cancel", "refund", "वापस", "रद्द", "पैसे"]):
        reply = (
            "गाँव बाज़ार में ऑर्डर देने के 180 सेकंड के भीतर शून्य शुल्क पर रद्दीकरण संभव है। डिलीवर होने के बाद केवल क्षतिग्रस्त या गलत सामान पर रिफ़ंड दिया जाता है।"
            if is_hi else
            "Orders can be cancelled with 0 fee within 180 seconds of placement. After delivery, refunds apply to damaged or missing items."
        )
        return SupportChatResponse(
            reply=reply,
            intent="POLICY_QUERY",
            suggested_actions=["रद्दीकरण नीति पढ़ें", "सहायता टिकट बनाएं"] if is_hi else ["View Refund Policy", "Create Ticket"]
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
