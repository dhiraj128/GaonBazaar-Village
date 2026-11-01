from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.base import Store, Runner, Order, User, GlobalCatalogItem, OrderItem, SupportTicket, AuditLog, Address
from app.core.config import settings
from app.core.security import get_current_admin, create_access_token

router = APIRouter(prefix="/admin", tags=["Super Admin Operations"])

class AdminLoginRequest(BaseModel):
    phone: str = "9800000099"
    secret_key: Optional[str] = None
    otp: Optional[str] = None

class SettingsUpdate(BaseModel):
    max_delivery_radius_km: Optional[float] = None
    platform_fee: Optional[float] = None
    vendor_commission_pct: Optional[float] = None

class TicketStatusUpdate(BaseModel):
    status: str # OPEN, RESOLVED, CLOSED

class AssignRunnerRequest(BaseModel):
    runner_id: str
    vendor_commission_pct: Optional[float] = None

class CatalogItemCreate(BaseModel):
    name_en: str
    name_hi: str
    category: str
    standard_unit: str
    suggested_price: float
    image_url: str

class OrderStatusUpdate(BaseModel):
    status: str
    cash_collected: Optional[bool] = None

@router.post("/auth/login")
async def admin_login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    # Strict Admin Security: Must supply matching ADMIN_API_KEY
    is_key_match = bool(req.secret_key and req.secret_key.strip() == settings.ADMIN_API_KEY)
    
    if not is_key_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="प्रशासनिक क्रेडेंशियल्स अमान्य हैं (Invalid Admin credentials. Authorized Admin Key required)"
        )
        
    res = await db.execute(select(User).where(User.phone == req.phone))
    user = res.scalars().first()
    if not user:
        user = User(
            phone=req.phone,
            name="GaonBazaar Super Admin",
            role="admin",
            preferred_language="en",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    token = create_access_token({"sub": user.id, "phone": user.phone, "role": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name or "Super Admin",
            "role": "admin"
        }
    }

@router.get("/overview")
async def get_admin_overview(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    stores_res = await db.execute(select(Store))
    stores = stores_res.scalars().all()
    
    runners_res = await db.execute(select(Runner))
    runners = runners_res.scalars().all()
    
    orders_res = await db.execute(select(Order))
    orders = orders_res.scalars().all()
    
    total_gmv = sum(o.total_amount for o in orders if o.status == "DELIVERED")
    active_orders = [o for o in orders if o.status not in ["DELIVERED", "CANCELLED"]]
    pending_vendors = [s for s in stores if not s.is_approved]
    pending_runners = [r for r in runners if not r.is_approved]
    
    return {
        "pilot_area": f"{settings.PILOT_BLOCK}, {settings.PILOT_DISTRICT}, {settings.PILOT_STATE}",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT,
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_online and s.is_approved]),
        "total_runners": len(runners),
        "online_runners": len([r for r in runners if r.is_online and r.is_approved]),
        "total_orders": len(orders),
        "active_orders_count": len(active_orders),
        "total_gmv": round(total_gmv, 2),
        "pending_vendor_approvals": len(pending_vendors),
        "pending_runner_approvals": len(pending_runners)
    }

@router.get("/vendors")
async def get_all_vendors(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Store))
    return res.scalars().all()

@router.get("/vendors/pending")
async def get_pending_vendors(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Store).where(Store.is_approved == False))
    return res.scalars().all()

@router.post("/vendors/{store_id}/approve")
async def approve_vendor(store_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Store).where(Store.id == store_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
    st.is_approved = True
    await db.commit()
    return {"message": f"Store {st.shop_name} approved successfully", "is_approved": True}

@router.post("/vendors/{store_id}/reject")
async def reject_vendor(store_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Store).where(Store.id == store_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
    st.is_approved = False
    await db.commit()
    return {"message": f"Store {st.shop_name} rejected", "is_approved": False}

@router.get("/runners")
async def get_all_runners(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Runner))
    return res.scalars().all()

@router.get("/runners/pending")
async def get_pending_runners(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Runner).where(Runner.is_approved == False))
    return res.scalars().all()

@router.post("/runners/{runner_id}/approve")
async def approve_runner(runner_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Runner).where(Runner.id == runner_id))
    rn = res.scalars().first()
    if not rn:
        raise HTTPException(status_code=404, detail="Runner not found")
    rn.is_approved = True
    await db.commit()
    return {"message": f"Runner {rn.full_name} approved successfully", "is_approved": True}

@router.post("/runners/{runner_id}/reject")
async def reject_runner(runner_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Runner).where(Runner.id == runner_id))
    rn = res.scalars().first()
    if not rn:
        raise HTTPException(status_code=404, detail="Runner not found")
    rn.is_approved = False
    await db.commit()
    return {"message": f"Runner {rn.full_name} rejected", "is_approved": False}

@router.get("/orders")
async def get_all_orders(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(
        select(Order).options(selectinload(Order.items), selectinload(Order.store)).order_by(Order.placed_at.desc())
    )
    orders = res.scalars().all()
    results = []
    now = datetime.now(timezone.utc)
    for o in orders:
        c_until = o.cancel_until if o.cancel_until is not None else None
        if c_until and c_until.tzinfo is None:
            c_until = c_until.replace(tzinfo=timezone.utc)
        results.append({
            "id": o.id,
            "customer_id": o.customer_id,
            "store_id": o.store_id,
            "store_name": o.store.shop_name if o.store else "Store",
            "runner_id": o.runner_id,
            "status": o.status,
            "subtotal": o.subtotal,
            "delivery_fee": o.delivery_fee,
            "platform_fee": o.platform_fee,
            "total_amount": o.total_amount,
            "payment_mode": o.payment_method,
            "payment_status": o.payment_status,
            "delivery_otp": o.delivery_otp,
            "items_count": len(o.items),
            "created_at": o.placed_at.isoformat() if o.placed_at else None,
            "is_cancellable": o.status == "PLACED" and c_until is not None and c_until > now
        })
    return results

@router.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, req: OrderStatusUpdate, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    valid_statuses = ["PLACED", "ACCEPTED", "PACKED", "RUNNER_ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    order.status = req.status
    if req.status == "DELIVERED":
        if order.payment_method == "COD":
            if req.cash_collected is True:
                order.payment_status = "PAID"
            else:
                order.payment_status = "PENDING"
        elif order.payment_method == "ONLINE_SIMULATED":
            order.payment_status = "SIMULATED"
    await db.commit()
    return {"message": f"Order {order_id} status updated to {req.status}", "status": order.status}

@router.get("/catalog")
async def get_master_catalog(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(GlobalCatalogItem))
    return res.scalars().all()

@router.post("/catalog")
async def add_master_catalog_item(item: CatalogItemCreate, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    new_item = GlobalCatalogItem(
        name_en=item.name_en,
        name_hi=item.name_hi,
        category=item.category,
        standard_unit=item.standard_unit,
        suggested_price=item.suggested_price,
        image_url=item.image_url
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.get("/settings")
async def get_platform_settings(_admin: dict = Depends(get_current_admin)):
    return {
        "pilot_block": settings.PILOT_BLOCK,
        "pilot_district": settings.PILOT_DISTRICT,
        "pilot_state": settings.PILOT_STATE,
        "pilot_localities": [
            {"name": "Chaturshi / Chatursi", "lat": 26.1950, "lng": 85.3450},
            {"name": "Tubanaghara / Benaghara", "lat": 26.2100, "lng": 85.3550},
            {"name": "Sivay Patti", "lat": 26.2250, "lng": 85.3600},
            {"name": "Tulsi Ganj / Bangaon", "lat": 26.1880, "lng": 85.3320}
        ],
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT,
        "cancel_window_seconds": settings.CUSTOMER_CANCEL_WINDOW_SECONDS
    }

@router.get("/settlements")
async def get_settlements_ledger(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(
        select(Order).options(selectinload(Order.store)).where(Order.status == "DELIVERED")
    )
    delivered_orders = res.scalars().all()
    
    vendor_totals = {}
    runner_totals = {}
    
    for o in delivered_orders:
        if o.store_id:
            s_name = o.store.shop_name if o.store else "Store"
            if o.store_id not in vendor_totals:
                vendor_totals[o.store_id] = {"store_id": o.store_id, "store_name": s_name, "total_payout": 0.0, "order_count": 0}
            vendor_totals[o.store_id]["total_payout"] += o.subtotal
            vendor_totals[o.store_id]["order_count"] += 1
            
        if o.runner_id:
            if o.runner_id not in runner_totals:
                runner_totals[o.runner_id] = {"runner_id": o.runner_id, "total_payout": 0.0, "order_count": 0}
            runner_totals[o.runner_id]["total_payout"] += o.delivery_fee
            runner_totals[o.runner_id]["order_count"] += 1

    return {
        "vendor_settlements": list(vendor_totals.values()),
        "runner_settlements": list(runner_totals.values()),
        "vendor_payouts_due": sum(v["total_payout"] for v in vendor_totals.values()),
        "runner_payouts_due": sum(r["total_payout"] for r in runner_totals.values()),
        "platform_fee_collected": len(delivered_orders) * settings.PLATFORM_FEE,
        "total_delivered_orders": len(delivered_orders)
    }

@router.get("/customers")
async def get_all_customers(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(
        select(User).options(selectinload(User.addresses), selectinload(User.orders)).where(User.role == "customer")
    )
    users = res.scalars().all()
    results = []
    for u in users:
        results.append({
            "id": u.id,
            "phone": u.phone,
            "name": u.name or "Rural Customer",
            "preferred_language": u.preferred_language,
            "is_active": u.is_active,
            "addresses_count": len(u.addresses),
            "orders_count": len(u.orders),
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return results

@router.patch("/settings")
async def update_platform_settings(req: SettingsUpdate, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    if req.max_delivery_radius_km is not None:
        settings.MAX_DELIVERY_RADIUS_KM = req.max_delivery_radius_km
    if req.platform_fee is not None:
        settings.PLATFORM_FEE = req.platform_fee
    if req.vendor_commission_pct is not None:
        settings.DEFAULT_VENDOR_COMMISSION_PCT = req.vendor_commission_pct

    audit = AuditLog(
        action="SETTINGS_UPDATED",
        target_type="PLATFORM_SETTINGS",
        target_id="global",
        details=f"Radius: {settings.MAX_DELIVERY_RADIUS_KM}km, PlatformFee: ₹{settings.PLATFORM_FEE}, Commission: {settings.DEFAULT_VENDOR_COMMISSION_PCT}%"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": "Platform settings updated successfully",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT
    }

@router.post("/orders/{order_id}/assign-runner")
async def assign_runner_to_order(order_id: str, req: AssignRunnerRequest, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res_order = await db.execute(select(Order).where(Order.id == order_id))
    order = res_order.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    res_runner = await db.execute(select(Runner).where(Runner.id == req.runner_id))
    runner = res_runner.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner not found")

    order.runner_id = runner.id
    order.status = "RUNNER_ASSIGNED"

    audit = AuditLog(
        action="RUNNER_ASSIGNED",
        target_type="ORDER",
        target_id=order.id,
        details=f"Assigned runner {runner.full_name} ({runner.id}) to order {order.id}"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"Runner {runner.full_name} assigned to order {order.id}",
        "order_id": order.id,
        "runner_id": runner.id,
        "status": order.status
    }

@router.get("/tickets")
async def get_support_tickets(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(SupportTicket).order_by(SupportTicket.created_at.desc()))
    return res.scalars().all()

@router.patch("/tickets/{ticket_id}")
async def update_ticket_status(ticket_id: str, req: TicketStatusUpdate, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    ticket.status = req.status

    audit = AuditLog(
        action="TICKET_STATUS_UPDATED",
        target_type="SUPPORT_TICKET",
        target_id=ticket.id,
        details=f"Ticket {ticket.id} status changed to {req.status}"
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Ticket {ticket.id} updated to {req.status}", "status": ticket.status}

@router.get("/audit-logs")
async def get_audit_logs(db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
    return res.scalars().all()

