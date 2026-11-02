import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from pydantic import BaseModel
from app.models.base import (
    Order, OrderItem, OrderTimeline, Store, StoreProduct, Address, User, Runner, SupportTicket
)

class CreateTicketRequest(BaseModel):
    subject: str
    message: str
    order_id: Optional[str] = None

class RunnerLocationUpdate(BaseModel):
    latitude: float
    longitude: float
from app.schemas.order import (
    CartSyncRequest, CartPriceBreakdown, CreateOrderRequest, OrderResponse,
    OrderItemDetail, OrderTimelineDetail, OrderActionRequest
)
from app.core.security import get_current_user_payload
from app.services.geo_service import calculate_haversine_distance, is_within_service_radius
from app.services.pricing_service import calculate_order_totals
from app.core.config import settings

router = APIRouter(tags=["Orders & Checkout"])

@router.post("/cart/sync", response_model=CartPriceBreakdown)
async def sync_cart(data: CartSyncRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch store
    res = await db.execute(select(Store).where(Store.id == data.store_id))
    store = res.scalars().first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    # 2. Check distance
    distance_km = 2.5 # Default fallback estimate
    is_serv = True
    if data.delivery_latitude and data.delivery_longitude:
        is_serv, distance_km = is_within_service_radius(
            store.latitude, store.longitude, data.delivery_latitude, data.delivery_longitude
        )
        
    # 3. Calculate subtotal from products in store
    subtotal = 0.0
    for itm in data.items:
        pres = await db.execute(
            select(StoreProduct).where(StoreProduct.id == itm.product_id, StoreProduct.store_id == data.store_id)
        )
        prod = pres.scalars().first()
        if prod:
            subtotal += prod.price * itm.quantity
            
    totals = calculate_order_totals(subtotal, distance_km)
    
    warning = None
    if not is_serv:
        warning = f"Delivery address is {distance_km} km away, exceeding maximum 8.0 km policy."
        
    return CartPriceBreakdown(
        subtotal=totals["subtotal"],
        delivery_fee=totals["delivery_fee"],
        platform_fee=totals["platform_fee"], # Strict ₹3.00
        total_amount=totals["total_amount"],
        is_serviceable=is_serv,
        distance_km=distance_km,
        warning=warning
    )

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: CreateOrderRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    customer_id = payload.get("sub")
    
    # Verify Store
    s_res = await db.execute(select(Store).where(Store.id == data.store_id))
    store = s_res.scalars().first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    # Verify Address
    a_res = await db.execute(
        select(Address).where(Address.id == data.delivery_address_id, Address.user_id == customer_id)
    )
    address = a_res.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Delivery address not found")
        
    # Check 8.0 km distance limit
    is_serv, dist_km = is_within_service_radius(store.latitude, store.longitude, address.latitude, address.longitude)
    if not is_serv:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Store is {dist_km} km away. Maximum allowed delivery radius is 8.0 km."
        )
        
    # Calculate prices and items
    subtotal = 0.0
    order_items_to_create = []
    
    for itm in data.items:
        p_res = await db.execute(
            select(StoreProduct).options(selectinload(StoreProduct.global_item)).where(StoreProduct.id == itm.product_id, StoreProduct.store_id == data.store_id)
        )
        prod = p_res.scalars().first()
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product {itm.product_id} unavailable in selected store")
            
        line_total = prod.price * itm.quantity
        subtotal += line_total
        
        name_en = prod.custom_name_en or (prod.global_item.name_en if prod.global_item else "Product")
        name_hi = prod.custom_name_hi or (prod.global_item.name_hi if prod.global_item else "उत्पाद")
        
        order_items_to_create.append(OrderItem(
            product_id=prod.id,
            product_name_en=name_en,
            product_name_hi=name_hi,
            unit=prod.unit,
            unit_price=prod.price,
            quantity=itm.quantity,
            total_price=line_total,
            image_url=prod.image_url
        ))
        
    totals = calculate_order_totals(subtotal, dist_km)
    
    now = datetime.now(timezone.utc)
    cancel_until = now + timedelta(seconds=settings.CUSTOMER_CANCEL_WINDOW_SECONDS)
    delivery_otp = str(random.randint(1000, 9999)) # 4-digit OTP
    
    # Genuine payment methods: COD or ONLINE
    payment_method = data.payment_method.upper() if data.payment_method in ["COD", "ONLINE"] else "COD"

    order = Order(
        customer_id=customer_id,
        store_id=store.id,
        delivery_address_id=address.id,
        status="PLACED",
        subtotal=totals["subtotal"],
        delivery_fee=totals["delivery_fee"],
        platform_fee=totals["platform_fee"], # Strict ₹3.00
        total_amount=totals["total_amount"],
        payment_method=payment_method,
        payment_status="PENDING",
        delivery_otp=delivery_otp,
        placed_at=now,
        cancel_until=cancel_until,
        customer_notes=data.customer_notes
    )
    db.add(order)
    await db.flush()
    
    # Attach order items
    for oi in order_items_to_create:
        oi.order_id = order.id
        db.add(oi)
        
    # Initial timeline entry
    timeline_entry = OrderTimeline(
        order_id=order.id,
        status="PLACED",
        title="ऑर्डर दर्ज हुआ (Order Placed)",
        description=f"Store: {store.shop_name}, Amount: ₹{totals['total_amount']}",
        timestamp=now
    )
    db.add(timeline_entry)
    
    await db.commit()
    await db.refresh(order)
    
    return await _format_order_response(order.id, db, current_user_id=customer_id, role="customer")

@router.get("/orders", response_model=List[OrderResponse])
async def list_customer_orders(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(
        select(Order.id).where(Order.customer_id == user_id).order_by(Order.placed_at.desc())
    )
    order_ids = res.scalars().all()
    
    out = []
    for oid in order_ids:
        resp = await _format_order_response(oid, db, current_user_id=user_id, role="customer")
        if resp:
            out.append(resp)
    return out

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    role = payload.get("role")

    res = await db.execute(
        select(Order)
        .options(selectinload(Order.store), selectinload(Order.runner))
        .where(Order.id == order_id)
    )
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_cust = order.customer_id == user_id
    is_owner = order.store and order.store.owner_id == user_id
    is_runner = order.runner and order.runner.user_id == user_id
    is_admin = role == "admin"

    if not (is_cust or is_owner or is_runner or is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to access this order")

    resp = await _format_order_response(order_id, db, current_user_id=user_id, role=role)
    return resp

@router.get("/orders/{order_id}/tracking")
async def track_order_delivery(
    order_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticated live tracking endpoint.
    Only the customer who placed the order or an admin can access tracking.
    Runner live coordinates are only shared during active transit (PICKED_UP / OUT_FOR_DELIVERY).
    """
    user_id = payload.get("sub")
    role = payload.get("role")

    res = await db.execute(
        select(Order)
        .options(selectinload(Order.runner), selectinload(Order.store), selectinload(Order.delivery_address))
        .where(Order.id == order_id)
    )
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != user_id and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to track this order")

    runner = order.runner
    is_live = order.status in ["PICKED_UP", "OUT_FOR_DELIVERY"] and runner is not None

    return {
        "order_id": order.id,
        "status": order.status,
        "is_live_tracking_active": is_live,
        "runner_name": runner.full_name if runner else None,
        "runner_phone": "9876543210" if runner else None,
        "runner_latitude": runner.current_latitude if is_live else None,
        "runner_longitude": runner.current_longitude if is_live else None,
        "destination_latitude": order.delivery_address.latitude if order.delivery_address else None,
        "destination_longitude": order.delivery_address.longitude if order.delivery_address else None,
        "store_latitude": order.store.latitude if order.store else None,
        "store_longitude": order.store.longitude if order.store else None,
    }

@router.post("/orders/tickets")
async def create_support_ticket(
    req: CreateTicketRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
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
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None
    }


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.customer_id != user_id and payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    now = datetime.now(timezone.utc)
    # Ensure cancel_until is timezone-aware
    cancel_deadline = order.cancel_until.replace(tzinfo=timezone.utc) if order.cancel_until.tzinfo is None else order.cancel_until
    
    if now > cancel_deadline:
        diff = int((now - cancel_deadline).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"रद्द करने की 180 सेकंड की समय सीमा समाप्त हो चुकी है ({diff}s ago). दुकान तैयारी शुरू कर चुकी है।"
        )
        
    order.status = "CANCELLED"
    if order.payment_status == "PAID":
        order.payment_status = "REFUNDED"
    db.add(OrderTimeline(
        order_id=order.id,
        status="CANCELLED",
        title="ऑर्डर रद्द किया गया (Cancelled)",
        description="Customer requested cancellation within 180-second window" + (" - Refund initiated" if order.payment_status == "REFUNDED" else ""),
        timestamp=now
    ))
    await db.commit()
    return {"message": "Order successfully cancelled within 180s window", "status": "CANCELLED"}

@router.get("/vendor/orders", response_model=List[OrderResponse])
async def list_vendor_orders(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == user_id))
    store = res.scalars().first()
    if not store:
        return []
    
    orders_res = await db.execute(
        select(Order.id).where(Order.store_id == store.id).order_by(Order.placed_at.desc())
    )
    order_ids = orders_res.scalars().all()
    out = []
    for oid in order_ids:
        resp = await _format_order_response(oid, db, current_user_id=user_id, role="vendor")
        if resp:
            out.append(resp)
    return out

@router.get("/vendor/finances")
async def get_vendor_finances(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == user_id))
    store = res.scalars().first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    orders_res = await db.execute(
        select(Order).where(Order.store_id == store.id, Order.status == "DELIVERED")
    )
    delivered_orders = orders_res.scalars().all()
    total_sales = sum(o.subtotal for o in delivered_orders)
    
    recent_settlements = [
        {
            "order_id": o.id,
            "date": o.delivered_at.strftime("%d %b %Y, %I:%M %p") if o.delivered_at else o.placed_at.strftime("%d %b %Y"),
            "amount": f"₹{o.subtotal:.2f}",
            "status": "Settled (UPI)" if o.payment_status == "PAID" else "Processing (Tonight)",
            "payment_method": o.payment_method
        }
        for o in delivered_orders[:10]
    ]
    
    return {
        "store_id": store.id,
        "total_sales": total_sales,
        "commission_rate": store.commission_rate,
        "commission_deducted": round(total_sales * (store.commission_rate / 100.0), 2),
        "net_payout_due": total_sales - round(total_sales * (store.commission_rate / 100.0), 2),
        "total_delivered_orders": len(delivered_orders),
        "upi_id": store.upi_id or "Not configured",
        "recent_settlements": recent_settlements
    }

@router.get("/runner/jobs", response_model=List[OrderResponse])
async def list_runner_jobs(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    
    # Available jobs (PACKED or assigned to this runner)
    if runner:
        query = select(Order.id).where(
            (Order.status == "PACKED") | (Order.runner_id == runner.id)
        ).order_by(Order.placed_at.desc())
    else:
        query = select(Order.id).where(Order.status == "PACKED").order_by(Order.placed_at.desc())
        
    orders_res = await db.execute(query)
    order_ids = orders_res.scalars().all()
    out = []
    for oid in order_ids:
        resp = await _format_order_response(oid, db, current_user_id=user_id, role="runner")
        if resp:
            out.append(resp)
    return out

@router.get("/runner/finances")
async def get_runner_finances(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner profile not found")
        
    orders_res = await db.execute(
        select(Order).where(Order.runner_id == runner.id, Order.status == "DELIVERED")
    )
    delivered_orders = orders_res.scalars().all()
    total_delivery_fees = sum(o.delivery_fee for o in delivered_orders)
    
    return {
        "runner_id": runner.id,
        "total_delivery_earnings": total_delivery_fees,
        "total_deliveries_count": len(delivered_orders),
        "cash_collected_to_remit": sum(o.total_amount for o in delivered_orders if o.payment_method == "COD"),
        "upi_id": runner.upi_id
    }

class RunnerStatusUpdate(BaseModel):
    is_online: bool

class RunnerOnboardRequest(BaseModel):
    full_name: str
    vehicle_type: str = "Motorcycle"
    vehicle_number: Optional[str] = None
    driving_licence_no: Optional[str] = None
    upi_id: Optional[str] = None

@router.post("/runner/onboard")
async def onboard_runner(
    data: RunnerOnboardRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    
    if runner:
        runner.full_name = data.full_name
        runner.vehicle_type = data.vehicle_type
        runner.vehicle_number = data.vehicle_number
        runner.driving_licence_no = data.driving_licence_no
        runner.upi_id = data.upi_id
        runner.is_approved = False # Under Admin review
    else:
        runner = Runner(
            user_id=user_id,
            full_name=data.full_name,
            vehicle_type=data.vehicle_type,
            vehicle_number=data.vehicle_number,
            driving_licence_no=data.driving_licence_no,
            upi_id=data.upi_id,
            is_approved=False,
            is_online=False,
            current_latitude=26.2230,
            current_longitude=85.3520
        )
        db.add(runner)

    await db.commit()
    await db.refresh(runner)

    return {
        "id": runner.id,
        "user_id": runner.user_id,
        "full_name": runner.full_name,
        "vehicle_type": runner.vehicle_type,
        "vehicle_number": runner.vehicle_number,
        "dl_number": runner.driving_licence_no,
        "is_online": runner.is_online,
        "is_approved": runner.is_approved,
        "rating": 4.9,
        "upi_id": runner.upi_id,
        "today_earnings": 0.0,
        "completed_trips": 0
    }

@router.get("/runner/me")
async def get_runner_profile(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner profile not found")
    
    orders_res = await db.execute(
        select(Order).where(Order.runner_id == runner.id, Order.status == "DELIVERED")
    )
    delivered_orders = orders_res.scalars().all()
    total_delivery_fees = sum(o.delivery_fee for o in delivered_orders)
    cash_to_remit = sum(o.total_amount for o in delivered_orders if o.payment_method == "COD" and o.payment_status == "PAID")

    return {
        "id": runner.id,
        "user_id": runner.user_id,
        "full_name": runner.full_name,
        "vehicle_type": runner.vehicle_type,
        "vehicle_number": runner.vehicle_number,
        "dl_number": runner.driving_licence_no,
        "is_online": runner.is_online,
        "is_approved": runner.is_approved,
        "rating": 4.9,
        "upi_id": runner.upi_id,
        "today_earnings": total_delivery_fees,
        "cash_to_remit": cash_to_remit,
        "completed_trips": len(delivered_orders)
    }

@router.patch("/runner/status")
async def update_runner_status(
    data: RunnerStatusUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner profile not found")
    if not runner.is_approved and data.is_online:
        raise HTTPException(status_code=400, detail="Runner must be approved by admin before going on duty")
    runner.is_online = data.is_online
    await db.commit()
    return {"message": f"Runner duty is now {'online' if runner.is_online else 'offline'}", "is_online": runner.is_online}

@router.put("/runner/location")
async def update_runner_location(
    data: RunnerLocationUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Live location update endpoint called by the Runner app.
    Updates runner's current GPS coordinates for active order tracking.
    """
    user_id = payload.get("sub")
    r_res = await db.execute(select(Runner).where(Runner.user_id == user_id))
    runner = r_res.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner profile not found")
    runner.current_latitude = data.latitude
    runner.current_longitude = data.longitude
    await db.commit()
    return {"status": "ok", "latitude": runner.current_latitude, "longitude": runner.current_longitude}

@router.post("/vendor/orders/{order_id}/action")
async def vendor_order_action(
    order_id: str,
    action_data: OrderActionRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    vendor_user_id = payload.get("sub")
    is_admin = payload.get("role") == "admin"
    if not is_admin:
        s_res = await db.execute(select(Store).where(Store.owner_id == vendor_user_id))
        store = s_res.scalars().first()
        if not store:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No store associated with this vendor account")
        if not store.is_approved:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store is pending administrative approval")
        if not store.is_online:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store is currently offline")
        if order.store_id != store.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You cannot modify orders belonging to another vendor's store")
        
    act = action_data.action.upper()
    now = datetime.now(timezone.utc)
    
    if act == "ACCEPT":
        if order.status != "PLACED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot ACCEPT order in status '{order.status}'. Order must be 'PLACED'.")
        order.status = "ACCEPTED"
        title = "दुकानदार ने स्वीकार किया (Accepted)"
    elif act in ["PACK", "PACKED"]:
        if order.status not in ["ACCEPTED", "PLACED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot PACK order in status '{order.status}'. Order must be 'ACCEPTED' or 'PLACED'.")
        order.status = "PACKED"
        title = "सामान पैक हो गया (Packed & Ready)"
    elif act in ["HANDOFF", "HANDED_OFF"]:
        if order.status not in ["PACKED", "RUNNER_ASSIGNED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot hand off order from status '{order.status}'. Order must be 'PACKED' or 'RUNNER_ASSIGNED'.")
        order.status = "PICKED_UP"
        title = "डिलीवरी साथी को सौंपा (Handed off to Runner)"
    elif act == "REJECT":
        if order.status not in ["PLACED", "ACCEPTED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot REJECT order in status '{order.status}'. Order must be 'PLACED' or 'ACCEPTED'.")
        order.status = "CANCELLED"
        title = "दुकानदार द्वारा अस्वीकृत (Rejected)"
    else:
        raise HTTPException(status_code=400, detail="Invalid vendor action")
        
    db.add(OrderTimeline(order_id=order.id, status=order.status, title=title, timestamp=now))
    await db.commit()
    return {"message": f"Order status updated to {order.status}", "status": order.status}

@router.post("/runner/jobs/{order_id}/action")
async def runner_job_action(
    order_id: str,
    action_data: OrderActionRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    runner_user_id = payload.get("sub")
    is_admin = payload.get("role") == "admin"
    runner = None
    if not is_admin:
        r_res = await db.execute(select(Runner).where(Runner.user_id == runner_user_id))
        runner = r_res.scalars().first()
        if not runner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Runner profile required to accept delivery jobs")
        if not runner.is_approved:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Runner account is pending administrative approval")
    
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    act = action_data.action.upper()
    now = datetime.now(timezone.utc)
    
    if act == "ACCEPT":
        if order.status not in ["PACKED", "ACCEPTED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot ACCEPT job in status '{order.status}'. Order must be 'PACKED' or 'ACCEPTED'.")
        if order.runner_id and runner and order.runner_id != runner.id and not is_admin:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order has already been assigned to another delivery runner")
        if runner:
            order.runner_id = runner.id
        order.status = "RUNNER_ASSIGNED"
        title = "डिलीवरी साथी तय हुआ (Runner Assigned)"
    elif act in ["PICKUP", "PICKED_UP"]:
        if not is_admin and runner and order.runner_id != runner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Order is assigned to another delivery runner")
        if order.status not in ["RUNNER_ASSIGNED", "PACKED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot PICKUP order from status '{order.status}'. Order must be 'RUNNER_ASSIGNED' or 'PACKED'.")
        order.status = "PICKED_UP"
        title = "सामान दुकान से उठाया (Picked Up)"
    elif act in ["OUT_FOR_DELIVERY", "OUT"]:
        if not is_admin and runner and order.runner_id != runner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Order is assigned to another delivery runner")
        if order.status != "PICKED_UP":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot transition to OUT_FOR_DELIVERY from status '{order.status}'. Order must be 'PICKED_UP'.")
        order.status = "OUT_FOR_DELIVERY"
        title = "डिलीवरी के लिए निकल चुके हैं (Out for Delivery)"
    elif act in ["DELIVER", "DELIVERED"]:
        if not is_admin and runner and order.runner_id != runner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Order is assigned to another delivery runner")
        if order.status != "OUT_FOR_DELIVERY":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot DELIVER order from status '{order.status}'. Prerequisites not met: order must be 'OUT_FOR_DELIVERY'.")
        # Strict OTP verification
        if not action_data.delivery_otp or action_data.delivery_otp.strip() != order.delivery_otp.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="गलत डिलीवरी ओटीपी (Invalid Customer Delivery OTP)"
            )
        order.status = "DELIVERED"
        order.delivered_at = now
        
        # Payment State Machine Handling: require verified cash collection for COD
        if order.payment_method == "COD":
            if action_data.cash_collected is True:
                order.payment_status = "PAID"
            else:
                order.payment_status = "PENDING"
            
        title = "सफलतापूर्वक डिलीवर हुआ (Delivered)"
    else:
        raise HTTPException(status_code=400, detail="Invalid runner action")
        
    db.add(OrderTimeline(order_id=order.id, status=order.status, title=title, timestamp=now))
    await db.commit()
    return {"message": f"Order status updated to {order.status}", "status": order.status}

async def _format_order_response(
    order_id: str,
    db: AsyncSession,
    current_user_id: Optional[str] = None,
    role: Optional[str] = None
) -> Optional[OrderResponse]:
    res = await db.execute(
        select(Order)
        .options(
            selectinload(Order.store),
            selectinload(Order.runner),
            selectinload(Order.delivery_address),
            selectinload(Order.items),
            selectinload(Order.timeline)
        )
        .where(Order.id == order_id)
    )
    order = res.scalars().first()
    if not order:
        return None
        
    now = datetime.now(timezone.utc)
    cancel_deadline = order.cancel_until.replace(tzinfo=timezone.utc) if order.cancel_until.tzinfo is None else order.cancel_until
    
    seconds_remaining = max(0, int((cancel_deadline - now).total_seconds()))
    can_cancel = (order.status == "PLACED" and seconds_remaining > 0)
    
    items_out = [
        OrderItemDetail(
            id=i.id,
            product_id=i.product_id,
            name_en=i.product_name_en,
            name_hi=i.product_name_hi,
            unit=i.unit,
            unit_price=i.unit_price,
            quantity=i.quantity,
            total_price=i.total_price,
            image_url=i.image_url
        )
        for i in order.items
    ]
    
    timeline_out = [
        OrderTimelineDetail(
            status=t.status,
            title=t.title,
            description=t.description,
            timestamp=t.timestamp
        )
        for t in order.timeline
    ]

    # Security: Delivery PIN is strictly customer-only. Never expose to Vendor or Runner.
    is_cust = (current_user_id and order.customer_id == current_user_id)
    is_admin = (role == "admin")
    exposed_otp = order.delivery_otp if (is_cust or is_admin) else None
    
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        store_id=order.store_id,
        store_name=order.store.shop_name if order.store else "GaonBazaar Store",
        runner_id=order.runner_id,
        runner_name=order.runner.full_name if order.runner else None,
        runner_phone="9876543210" if order.runner else None,
        delivery_address=(
            f"{order.delivery_address.village}, {order.delivery_address.landmark + ', ' if order.delivery_address.landmark else ''}{order.delivery_address.block}, {order.delivery_address.district}"
            if order.delivery_address else "Minapur, Muzaffarpur"
        ),
        status=order.status,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        platform_fee=order.platform_fee,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        payment_order_id=getattr(order, "payment_order_id", None),
        transaction_id=getattr(order, "transaction_id", None),
        delivery_otp=exposed_otp,
        placed_at=order.placed_at,
        cancel_until=order.cancel_until,
        can_cancel=can_cancel,
        cancel_seconds_remaining=seconds_remaining,
        items=items_out,
        timeline=timeline_out
    )
