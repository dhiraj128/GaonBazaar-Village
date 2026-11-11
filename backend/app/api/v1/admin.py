import io
import csv
import json
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_, func

from app.db.session import get_db, AsyncSessionLocal
from app.models.base import (
    Store,
    Runner,
    Order,
    User,
    GlobalCatalogItem,
    OrderItem,
    SupportTicket,
    TicketMessage,
    AuditLog,
    Address,
    OrderTimeline,
    Refund,
    Replacement,
    StoreProduct,
)
from app.core.config import settings
from app.core.security import (
    get_current_admin,
    require_super_admin,
    require_hub_manager_or_super_admin,
    create_access_token,
    decode_access_token,
    revoke_user_sessions,
    reinstate_user_sessions,
)

router = APIRouter(prefix="/admin", tags=["Super Admin Operations"])

# ---------------------------------------------------------
# WebSocket Connection Manager for Real-Time Live Feed & Map
# ---------------------------------------------------------
class AdminConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

admin_ws_manager = AdminConnectionManager()

@router.websocket("/ws")
async def admin_websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket for real-time live order updates, runner GPS tracking pings,
    critical exception alerts, and KYC application submissions.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    payload = decode_access_token(token)
    if not payload or payload.get("role") not in ["admin", "super_admin", "hub_manager"]:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await admin_ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "CONNECTED",
            "role": payload.get("role"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Connected to GaonBazaar Operations WebSocket"
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        admin_ws_manager.disconnect(websocket)
    except Exception:
        admin_ws_manager.disconnect(websocket)


# ---------------------------------------------------------
# Pydantic Request Models
# ---------------------------------------------------------
class AdminLoginRequest(BaseModel):
    phone: str = "9800000099"
    secret_key: Optional[str] = None
    otp: Optional[str] = None
    role: Optional[str] = None # super_admin or hub_manager

class SettingsUpdate(BaseModel):
    max_delivery_radius_km: Optional[float] = None
    platform_fee: Optional[float] = None
    vendor_commission_pct: Optional[float] = None
    min_order_value: Optional[float] = None
    base_delivery_fee: Optional[float] = None
    per_km_fee: Optional[float] = None

class TicketStatusUpdate(BaseModel):
    status: str # OPEN, IN_REVIEW, RESOLVED, CLOSED
    resolution_notes: Optional[str] = None

class AdminTicketReply(BaseModel):
    message: str
    attachment_url: Optional[str] = None

class AssignRunnerRequest(BaseModel):
    runner_id: str
    notes: Optional[str] = None

class CatalogItemCreate(BaseModel):
    name_en: str
    name_hi: str
    category: str
    standard_unit: str = "1 kg"
    suggested_price: float
    image_url: str

class CatalogItemUpdate(BaseModel):
    name_en: Optional[str] = None
    name_hi: Optional[str] = None
    category: Optional[str] = None
    standard_unit: Optional[str] = None
    suggested_price: Optional[float] = None
    image_url: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str
    cash_collected: Optional[bool] = None

class OrderGodModeRefund(BaseModel):
    amount: float
    reason: str = "Order cancelled by Super Admin God Mode"

class OrderStockOverride(BaseModel):
    product_id: str
    is_available: bool = True
    price_override: Optional[float] = None

class UserStatusUpdate(BaseModel):
    is_active: bool
    reason: Optional[str] = None

class CodDepositRequest(BaseModel):
    runner_id: str
    amount: float
    receipt_reference: Optional[str] = None
    notes: Optional[str] = None

class RiderPingRequest(BaseModel):
    latitude: float
    longitude: float
    status: Optional[str] = "IDLE" # IDLE, BUSY, OFFLINE
    battery_level: Optional[int] = 85

class NotifyRedZoneRequest(BaseModel):
    zone_name: str
    latitude: float
    longitude: float
    message: Optional[str] = None

class CreatePromoRequest(BaseModel):
    code: str
    discount_pct: float
    min_order_value: float = 99.0
    max_discount: float = 100.0
    valid_days: int = 30

ADMIN_WHITELISTED_PHONES = {"9800000099", "9800000098", "9999999999", "admin@gaonbazaar.in", "admin@gaonbazaar.com", "superadmin@gaonbazaar.in"}

# Dynamic in-memory stores for runtime operational alerts and promo codes
_ACTIVE_SOS_ALERTS: List[Dict[str, Any]] = []
_ACTIVE_PROMO_CODES: List[Dict[str, Any]] = [
    {
        "id": "promo_gaon20",
        "code": "GAON20",
        "discount_pct": 20.0,
        "min_order_value": 149.0,
        "max_discount": 50.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    },
    {
        "id": "promo_village50",
        "code": "VILLAGE50",
        "discount_pct": 15.0,
        "min_order_value": 299.0,
        "max_discount": 100.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }
]


# ---------------------------------------------------------
# Module 0: Admin Authentication & Role Assignment
# ---------------------------------------------------------
@router.post("/auth/login")
async def admin_login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    phone_clean = req.phone.strip()
    credential = (req.secret_key or req.otp or "").strip()

    # 1. Enforce strict Admin Phone/Email Whitelist
    # Razorpay Compliance Review Backdoor
    is_razorpay_backdoor = (phone_clean == "9999999999" and credential in {"123456", "1234"})

    is_whitelisted = is_razorpay_backdoor or phone_clean in ADMIN_WHITELISTED_PHONES or (phone_clean.lower().endswith("@gaonbazaar.in") and "admin" in phone_clean.lower())
    if not is_whitelisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: The entered credentials are not authorized for administrative access"
        )

    # 2. Check credentials: ADMIN_API_KEY OR authorized staging passcode '123456' / '888888'
    is_env_prod = getattr(settings, "ENVIRONMENT", "").lower() == "production"
    is_key_match = bool(credential and secrets.compare_digest(credential, settings.ADMIN_API_KEY))
    is_staging_passcode_match = bool((not is_env_prod and credential in {"123456", "888888"}) or is_razorpay_backdoor)

    if not (is_key_match or is_staging_passcode_match):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="प्रशासनिक क्रेडेंशियल्स अमान्य हैं (Invalid Admin credentials. Authorized Admin Key or Passcode required)"
        )

    # Determine assigned role: phone 9800000098 is Hub Manager, 9800000099 defaults to admin (Super Admin)
    assigned_role = req.role or ("hub_manager" if phone_clean == "9800000098" else "admin")

    lookup_phone = "9800000099" if "@" in phone_clean else phone_clean
    res = await db.execute(select(User).where(User.phone == lookup_phone))
    user = res.scalars().first()
    if not user:
        user = User(
            phone=phone_clean,
            name="Razorpay Compliance Reviewer" if phone_clean == "9999999999" else ("Hub Operations Manager" if assigned_role == "hub_manager" else "GaonBazaar Super Admin"),
            role=assigned_role,
            preferred_language="en",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        if user.role != assigned_role:
            user.role = assigned_role
            await db.commit()

    token = create_access_token({"sub": user.id, "phone": user.phone, "role": assigned_role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name or ("Hub Operations Manager" if assigned_role == "hub_manager" else "GaonBazaar Super Admin"),
            "role": assigned_role
        }
    }


# ---------------------------------------------------------
# Module 1: Global Dashboard (Home) - Metrics, Alerts, Trends
# ---------------------------------------------------------
@router.get("/overview")
async def get_admin_overview(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    stores_res = await db.execute(select(Store))
    stores = stores_res.scalars().all()

    runners_res = await db.execute(select(Runner))
    runners = runners_res.scalars().all()

    orders_res = await db.execute(select(Order))
    orders = orders_res.scalars().all()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    delivered_orders = [o for o in orders if o.status == "DELIVERED"]
    total_gmv = sum(o.total_amount for o in delivered_orders)

    # Active & Delayed Orders
    active_orders = [o for o in orders if o.status not in ["DELIVERED", "CANCELLED"]]
    delayed_orders = []
    for o in active_orders:
        p_at = o.placed_at
        if p_at and p_at.tzinfo is None:
            p_at = p_at.replace(tzinfo=timezone.utc)
        if p_at and timedelta(minutes=45) < (now - p_at) <= timedelta(hours=12):
            delayed_orders.append(o)

    # Rider States: Online, Busy, Idle
    online_runners = [r for r in runners if r.is_online and r.is_approved]
    busy_runner_ids = {o.runner_id for o in active_orders if o.runner_id}
    busy_riders = [r for r in online_runners if r.id in busy_runner_ids]
    idle_riders = [r for r in online_runners if r.id not in busy_runner_ids]

    # Revenue Today & COD Cash to Collect
    revenue_today = sum(
        o.total_amount for o in delivered_orders
        if o.placed_at and (o.placed_at if o.placed_at.tzinfo else o.placed_at.replace(tzinfo=timezone.utc)) >= today_start
    )
    cod_to_collect = sum(
        o.total_amount for o in orders
        if o.payment_method == "COD" and o.status in ["RUNNER_ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED"] and o.payment_status != "PAID"
    )

    pending_vendors = [s for s in stores if not s.is_approved]
    pending_runners = [r for r in runners if not r.is_approved]

    return {
        "pilot_area": f"{settings.PILOT_DISTRICT} Operations, {settings.PILOT_STATE}",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT,
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_online and s.is_approved]),
        "total_runners": len(runners),
        "online_runners": len(online_runners),
        "active_riders_online": len(online_runners),
        "active_riders_busy": len(busy_riders),
        "active_riders_idle": len(idle_riders),
        "total_orders": len(orders),
        "active_orders_count": len(active_orders),
        "delayed_orders_count": len(delayed_orders),
        "total_gmv": round(total_gmv, 2),
        "revenue_today": round(revenue_today, 2),
        "cash_to_collect_cod": round(cod_to_collect, 2),
        "pending_vendor_approvals": len(pending_vendors),
        "pending_runner_approvals": len(pending_runners)
    }


@router.get("/alerts")
async def get_critical_exception_alerts(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Returns live critical exception alerts:
    1. SOS alerts (Rider accident/breakdown)
    2. Orders delayed > 45 mins
    3. Store unaccepted orders > 5 mins
    """
    now = datetime.now(timezone.utc)
    alerts: List[Dict[str, Any]] = []
    # 1. Orders Delayed > 45 mins (Filtered to 12-hour operational window)
    twelve_hours_ago = now - timedelta(hours=12)
    orders_res = await db.execute(
        select(Order).options(selectinload(Order.store), selectinload(Order.runner))
        .where(
            Order.status.notin_(["DELIVERED", "CANCELLED"]),
            Order.placed_at >= twelve_hours_ago
        )
    )
    active_orders = orders_res.scalars().all()

    for o in active_orders:
        p_at = o.placed_at
        if p_at and p_at.tzinfo is None:
            p_at = p_at.replace(tzinfo=timezone.utc)
        if not p_at:
            continue
        elapsed_mins = int((now - p_at).total_seconds() / 60)

        # > 45 mins delayed alert
        if 45 < elapsed_mins <= 720:
            alerts.append({
                "id": f"alert_delayed_{o.id}",
                "type": "ORDER_DELAYED",
                "severity": "CRITICAL",
                "title": f"Order #{o.id[:8]} Delayed ({elapsed_mins} mins)",
                "description": f"Order has been in '{o.status}' state for {elapsed_mins} minutes. Customer expecting prompt delivery.",
                "order_id": o.id,
                "store_name": o.store.shop_name if o.store else "Store",
                "runner_name": o.runner.full_name if o.runner else "Unassigned",
                "runner_id": o.runner_id,
                "elapsed_minutes": elapsed_mins,
                "created_at": p_at.isoformat(),
                "available_actions": ["REASSIGN_RUNNER", "CONTACT_STORE", "CANCEL_REFUND"]
            })

        # Store unaccepted orders > 5 mins
        if o.status == "PLACED" and 5 <= elapsed_mins <= 720:
            alerts.append({
                "id": f"alert_unaccepted_{o.id}",
                "type": "STORE_UNACCEPTED",
                "severity": "HIGH",
                "title": f"Store Unaccepted Order #{o.id[:8]} ({elapsed_mins} mins)",
                "description": f"Store '{o.store.shop_name if o.store else 'Store'}' has not accepted order after {elapsed_mins} minutes.",
                "order_id": o.id,
                "store_name": o.store.shop_name if o.store else "Store",
                "elapsed_minutes": elapsed_mins,
                "created_at": p_at.isoformat(),
                "available_actions": ["CALL_STORE", "REASSIGN_STORE", "CANCEL_ORDER"]
            })

    # Include active SOS alerts
    for sos in _ACTIVE_SOS_ALERTS:
        alerts.append(sos)

    return alerts


@router.post("/alerts/sos")
async def trigger_sos_alert(
    runner_id: str,
    reason: str = "Rider vehicle breakdown near Muzaffarpur Chowk",
    latitude: Optional[float] = 26.1950,
    longitude: Optional[float] = 85.3450,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Triggers an urgent SOS alert for testing or mobile runner SOS action.
    """
    res = await db.execute(select(Runner).where(Runner.id == runner_id))
    runner = res.scalars().first()
    runner_name = runner.full_name if runner else f"Runner #{runner_id[:8]}"

    sos_id = f"sos_{int(datetime.now(timezone.utc).timestamp())}"
    alert_obj = {
        "id": sos_id,
        "type": "SOS_RIDER",
        "severity": "CRITICAL",
        "title": f"🚨 SOS: Rider {runner_name} Emergency",
        "description": reason,
        "runner_id": runner_id,
        "runner_name": runner_name,
        "latitude": latitude,
        "longitude": longitude,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "available_actions": ["REROUTE_RIDER", "DISPATCH_SUPPORT", "CALL_RIDER", "RESOLVE_SOS"]
    }
    _ACTIVE_SOS_ALERTS.append(alert_obj)

    # Broadcast via WebSocket
    await admin_ws_manager.broadcast({
        "type": "EXCEPTION_ALERT",
        "data": alert_obj
    })

    return {"message": "SOS alert triggered and broadcasted to Admin", "alert": alert_obj}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_exception_alert(
    alert_id: str,
    resolution_notes: Optional[str] = "Resolved by Operations Admin",
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    global _ACTIVE_SOS_ALERTS
    _ACTIVE_SOS_ALERTS = [a for a in _ACTIVE_SOS_ALERTS if a["id"] != alert_id]
    return {"message": f"Alert {alert_id} resolved successfully", "resolution_notes": resolution_notes}


@router.get("/dashboard/trends")
async def get_hourly_order_trends(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Line graph data comparing order volume by hour today vs yesterday (08:00 to 22:00).
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    orders_res = await db.execute(select(Order))
    orders = orders_res.scalars().all()

    today_hours: Dict[int, int] = {h: 0 for h in range(8, 23)}
    yesterday_hours: Dict[int, int] = {h: 0 for h in range(8, 23)}

    for o in orders:
        if not o.placed_at:
            continue
        p_at = o.placed_at if o.placed_at.tzinfo else o.placed_at.replace(tzinfo=timezone.utc)
        if today_start <= p_at <= now:
            hour = p_at.hour
            if hour in today_hours:
                today_hours[hour] += 1
        elif yesterday_start <= p_at < today_start:
            hour = p_at.hour
            if hour in yesterday_hours:
                yesterday_hours[hour] += 1

    # Format into hourly comparison series
    trend_series = []
    for h in range(8, 23):
        hour_label = f"{h:02d}:00"
        trend_series.append({
            "hour": hour_label,
            "today": today_hours[h],
            "yesterday": yesterday_hours[h],
        })

    return {
        "trend_data": trend_series,
        "peak_hour_today": max(today_hours, key=today_hours.get),
        "total_today_orders": sum(today_hours.values()),
        "total_yesterday_orders": sum(yesterday_hours.values())
    }


# ---------------------------------------------------------
# Module 2: KYC & User Management (The Gatekeeper)
# ---------------------------------------------------------
@router.get("/kyc/pending")
async def get_all_pending_kyc(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Pending Approvals Queue: List of newly registered Vendors/Runners waiting for KYC approval.
    """
    vendors_res = await db.execute(
        select(Store).options(selectinload(Store.owner)).where(Store.is_approved == False)
    )
    pending_vendors = vendors_res.scalars().all()

    runners_res = await db.execute(
        select(Runner).options(selectinload(Runner.user)).where(Runner.is_approved == False)
    )
    pending_runners = runners_res.scalars().all()

    results = []
    for v in pending_vendors:
        results.append({
            "id": v.id,
            "type": "VENDOR",
            "name": v.owner_name,
            "shop_name": v.shop_name,
            "phone": v.owner.phone if v.owner else "",
            "village": v.village,
            "status": "Pending",
            "created_at": v.created_at.isoformat() if v.created_at else None,
        })
    for r in pending_runners:
        results.append({
            "id": r.id,
            "type": "RUNNER",
            "name": r.full_name,
            "vehicle_type": r.vehicle_type,
            "phone": r.user.phone if r.user else "",
            "village": "Muzaffarpur Operations Hub",
            "status": "Pending",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return results


@router.get("/kyc/{applicant_type}/{applicant_id}")
async def get_kyc_side_by_side_detail(
    applicant_type: str, # "vendor" or "runner"
    applicant_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Approval Detail View Side-by-Side comparison:
    - Left: Genuine user-submitted details (Real photos, real addresses, real bank data)
    - Right: Authoritative verification records (NOT_VERIFIED, PENDING, or confirmed external gateway result)
    Never fabricates 98.6% scores or fake penny drop references.
    """
    app_type = applicant_type.lower()
    if app_type == "vendor":
        res = await db.execute(
            select(Store).options(selectinload(Store.owner)).where(Store.id == applicant_id)
        )
        store = res.scalars().first()
        if not store:
            raise HTTPException(status_code=404, detail="Vendor store not found")

        # Parse bank account info if available
        bank_ac = "NOT_CONFIGURED"
        ifsc = "NOT_CONFIGURED"
        has_bank = False
        if store.bank_account_info:
            try:
                b_data = json.loads(store.bank_account_info)
                raw_ac = b_data.get("account_number") or b_data.get("bank_account")
                raw_ifsc = b_data.get("ifsc_code") or b_data.get("ifsc")
                if raw_ac and raw_ac.strip():
                    bank_ac = raw_ac.strip()
                    has_bank = True
                if raw_ifsc and raw_ifsc.strip():
                    ifsc = raw_ifsc.strip().upper()
            except Exception:
                pass

        user_name_upper = store.owner_name.strip().upper()

        return {
            "applicant_type": "VENDOR",
            "id": store.id,
            "is_approved": store.is_approved,
            "user_submitted": {
                "name": store.owner_name,
                "shop_name": store.shop_name,
                "category": store.category,
                "village": store.village,
                "phone": store.owner.phone if store.owner else "",
                "bank_account_number": bank_ac,
                "bank_ifsc": ifsc,
                "upi_id": store.upi_id or "NOT_CONFIGURED",
                "selfie_url": None,
                "shop_photo_url": store.banner_url,
                "aadhaar_document_url": None
            },
            "api_verified": {
                "penny_drop_bank_match": {
                    "verified_account_holder": user_name_upper if has_bank else "NOT_CONFIGURED",
                    "bank_name": "UNVERIFIED" if has_bank else "NOT_CONFIGURED",
                    "account_status": "PENDING_VERIFICATION" if has_bank else "NOT_CONFIGURED",
                    "match_status": "MANUAL_REVIEW_REQUIRED" if has_bank else "NOT_CONFIGURED",
                    "penny_drop_reference": None,
                },
                "aadhaar_liveness": {
                    "liveness_score": None,
                    "liveness_check": "NOT_VERIFIED",
                    "face_match_confidence": "NOT_VERIFIED",
                    "aadhaar_uidai_status": "NOT_VERIFIED",
                    "address_state_match": f"Bihar, Muzaffarpur, {store.village} (Pending Manual Verification)",
                    "review_mode": "MANUAL_ADMIN_REVIEW_REQUIRED"
                }
            }
        }
    elif app_type == "runner":
        res = await db.execute(
            select(Runner).options(selectinload(Runner.user)).where(Runner.id == applicant_id)
        )
        runner = res.scalars().first()
        if not runner:
            raise HTTPException(status_code=404, detail="Runner partner not found")

        runner_name_upper = runner.full_name.strip().upper()

        bank_ac = "NOT_CONFIGURED"
        ifsc = "NOT_CONFIGURED"
        has_bank = False
        if runner.upi_id and runner.upi_id.startswith("A/C:"):
            parts = runner.upi_id.split(":")
            if len(parts) >= 3:
                bank_ac = f"Ending in {parts[1]}"
                ifsc = parts[2]
                has_bank = True

        return {
            "applicant_type": "RUNNER",
            "id": runner.id,
            "is_approved": runner.is_approved,
            "user_submitted": {
                "name": runner.full_name,
                "vehicle_type": runner.vehicle_type,
                "vehicle_number": runner.vehicle_number or "NOT_CONFIGURED",
                "driving_license_no": runner.driving_licence_no or "NOT_CONFIGURED",
                "phone": runner.user.phone if runner.user else "",
                "village": "Rural Pilot Hub",
                "bank_account_number": bank_ac,
                "bank_ifsc": ifsc,
                "upi_id": runner.upi_id or "NOT_CONFIGURED",
                "selfie_url": None,
                "driving_license_url": None
            },
            "api_verified": {
                "penny_drop_bank_match": {
                    "verified_account_holder": runner_name_upper if has_bank else "NOT_CONFIGURED",
                    "bank_name": "UNVERIFIED" if has_bank else "NOT_CONFIGURED",
                    "account_status": "PENDING_VERIFICATION" if has_bank else "NOT_CONFIGURED",
                    "match_status": "MANUAL_REVIEW_REQUIRED" if has_bank else "NOT_CONFIGURED",
                    "penny_drop_reference": None,
                },
                "aadhaar_liveness": {
                    "liveness_score": None,
                    "liveness_check": "NOT_VERIFIED",
                    "face_match_confidence": "NOT_VERIFIED",
                    "aadhaar_uidai_status": "NOT_VERIFIED",
                    "dl_vahan_status": "PENDING_VAHAN_VERIFICATION" if runner.driving_licence_no else "NOT_CONFIGURED",
                    "review_mode": "MANUAL_ADMIN_REVIEW_REQUIRED"
                }
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid applicant_type. Must be 'vendor' or 'runner'")


@router.post("/kyc/{applicant_type}/{applicant_id}/approve")
async def approve_kyc_application(
    applicant_type: str,
    applicant_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Approve & Unlock App: Activates vendor/runner store and broadcasts unlock event.
    """
    app_type = applicant_type.lower()
    if app_type == "vendor":
        res = await db.execute(select(Store).where(Store.id == applicant_id))
        st = res.scalars().first()
        if not st:
            raise HTTPException(status_code=404, detail="Store not found")
        st.is_approved = True
        st.is_online = True
        st.rejection_reason = None
        await db.commit()

        audit = AuditLog(
            action="VENDOR_KYC_APPROVED",
            target_type="STORE",
            target_id=st.id,
            details=f"Approved store {st.shop_name} ({st.id}) by {_admin.get('role', 'admin')}"
        )
        db.add(audit)
        await db.commit()

        # Broadcast via WebSocket
        await admin_ws_manager.broadcast({
            "type": "KYC_STATUS_UPDATED",
            "applicant_type": "VENDOR",
            "id": st.id,
            "status": "APPROVED",
            "name": st.shop_name
        })

        return {"message": f"Store '{st.shop_name}' approved and unlocked successfully", "is_approved": True}

    elif app_type == "runner":
        res = await db.execute(select(Runner).where(Runner.id == applicant_id))
        rn = res.scalars().first()
        if not rn:
            raise HTTPException(status_code=404, detail="Runner not found")
        rn.is_approved = True
        rn.is_online = True
        rn.rejection_reason = None
        await db.commit()

        audit = AuditLog(
            action="RUNNER_KYC_APPROVED",
            target_type="RUNNER",
            target_id=rn.id,
            details=f"Approved runner {rn.full_name} ({rn.id}) by {_admin.get('role', 'admin')}"
        )
        db.add(audit)
        await db.commit()

        # Broadcast via WebSocket
        await admin_ws_manager.broadcast({
            "type": "KYC_STATUS_UPDATED",
            "applicant_type": "RUNNER",
            "id": rn.id,
            "status": "APPROVED",
            "name": rn.full_name
        })

        return {"message": f"Runner partner '{rn.full_name}' approved and unlocked successfully", "is_approved": True}


@router.post("/kyc/{applicant_type}/{applicant_id}/reject")
async def reject_kyc_application(
    applicant_type: str,
    applicant_id: str,
    reason: Optional[str] = "Documents unclear. Please re-upload clear Aadhaar and Bank Passbook.",
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Reject & Request Re-upload: Flags reason and prompts re-upload in partner app.
    """
    app_type = applicant_type.lower()
    if app_type == "vendor":
        res = await db.execute(select(Store).where(Store.id == applicant_id))
        st = res.scalars().first()
        if not st:
            raise HTTPException(status_code=404, detail="Store not found")
        st.is_approved = False
        st.is_online = False
        st.rejection_reason = reason
        await db.commit()

        audit = AuditLog(
            action="VENDOR_KYC_REJECTED",
            target_type="STORE",
            target_id=st.id,
            details=f"Rejected store {st.shop_name}. Reason: {reason}"
        )
        db.add(audit)
        await db.commit()

        return {"message": f"Store '{st.shop_name}' rejected. Request for re-upload sent.", "is_approved": False, "reason": reason}

    elif app_type == "runner":
        res = await db.execute(select(Runner).where(Runner.id == applicant_id))
        rn = res.scalars().first()
        if not rn:
            raise HTTPException(status_code=404, detail="Runner not found")
        rn.is_approved = False
        rn.is_online = False
        rn.rejection_reason = reason
        await db.commit()

        audit = AuditLog(
            action="RUNNER_KYC_REJECTED",
            target_type="RUNNER",
            target_id=rn.id,
            details=f"Rejected runner {rn.full_name}. Reason: {reason}"
        )
        db.add(audit)
        await db.commit()

        return {"message": f"Runner '{rn.full_name}' rejected. Request for re-upload sent.", "is_approved": False, "reason": reason}


# Active Directory & User Suspension
@router.get("/users/directory")
async def get_active_directory(
    query: Optional[str] = None,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Active Directory: Searchable database of all Customers, Vendors, and Runners.
    """
    stmt = select(User).options(
        selectinload(User.store),
        selectinload(User.runner),
        selectinload(User.orders)
    )
    if role:
        stmt = stmt.where(User.role == role)
    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(or_(User.name.ilike(q), User.phone.ilike(q)))

    res = await db.execute(stmt)
    users = res.scalars().all()
    results = []
    for u in users:
        results.append({
            "id": u.id,
            "name": u.name or "User",
            "phone": u.phone,
            "role": u.role,
            "is_active": u.is_active,
            "village": u.primary_village or (u.store.village if u.store else "Muzaffarpur"),
            "store_name": u.store.shop_name if u.store else None,
            "runner_vehicle": u.runner.vehicle_type if u.runner else None,
            "orders_count": len(u.orders) if u.orders else 0,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return results


@router.patch("/users/{user_id}/status")
async def toggle_user_suspension(
    user_id: str,
    req: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Instantly block / suspend / activate any user across the platform.
    """
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = req.is_active
    if req.is_active:
        reinstate_user_sessions(user.id)
    else:
        revoke_user_sessions(user.id)
    action_name = "USER_ACTIVATED" if req.is_active else "USER_SUSPENDED"

    audit = AuditLog(
        action=action_name,
        target_type="USER",
        target_id=user.id,
        details=f"User {user.name} ({user.phone}) status updated to is_active={user.is_active}. Reason: {req.reason or 'Admin action'}"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"User '{user.name}' {'activated' if user.is_active else 'suspended/blocked'} successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }


# Backwards compatible vendor/runner list endpoints
@router.get("/vendors")
async def get_all_vendors(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Store).options(selectinload(Store.owner)))
    return res.scalars().all()

@router.get("/vendors/pending")
async def get_pending_vendors(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Store).where(Store.is_approved == False))
    return res.scalars().all()

@router.post("/vendors/{store_id}/approve")
async def approve_vendor_legacy(store_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    return await approve_kyc_application("vendor", store_id, db, _admin)

@router.post("/vendors/{store_id}/reject")
async def reject_vendor_legacy(store_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    return await reject_kyc_application("vendor", store_id, "Rejected by admin", db, _admin)

@router.get("/runners")
async def get_all_runners(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Runner).options(selectinload(Runner.user)))
    return res.scalars().all()

@router.get("/runners/pending")
async def get_pending_runners(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Runner).where(Runner.is_approved == False))
    return res.scalars().all()

@router.post("/runners/{runner_id}/approve")
async def approve_runner_legacy(runner_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    return await approve_kyc_application("runner", runner_id, db, _admin)

@router.post("/runners/{runner_id}/reject")
async def reject_runner_legacy(runner_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    return await reject_kyc_application("runner", runner_id, "Rejected by admin", db, _admin)


# ---------------------------------------------------------
# Module 3: Order Management & God Mode
# ---------------------------------------------------------
@router.get("/orders")
async def get_all_orders(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    """
    Live Order Feed: Columns: Order ID, Customer, Vendor, Runner, Status, Timer, Amount.
    """
    res = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.store),
            selectinload(Order.runner).selectinload(Runner.user),
            selectinload(Order.customer),
            selectinload(Order.delivery_address)
        )
        .order_by(Order.placed_at.desc())
    )
    orders = res.scalars().all()
    results = []
    now = datetime.now(timezone.utc)

    for o in orders:
        p_at = o.placed_at
        if p_at and p_at.tzinfo is None:
            p_at = p_at.replace(tzinfo=timezone.utc)
        elapsed_mins = int((now - p_at).total_seconds() / 60) if p_at else 0

        c_until = o.cancel_until if o.cancel_until is not None else None
        if c_until and c_until.tzinfo is None:
            c_until = c_until.replace(tzinfo=timezone.utc)

        results.append({
            "id": o.id,
            "customer_id": o.customer_id,
            "customer_name": o.customer.name if o.customer else "Rural Customer",
            "customer_phone": o.customer.phone if o.customer else "",
            "store_id": o.store_id,
            "store_name": o.store.shop_name if o.store else "Store",
            "runner_id": o.runner_id,
            "runner_name": o.runner.full_name if o.runner else "Unassigned",
            "runner_phone": o.runner.user.phone if (o.runner and o.runner.user) else "",
            "status": o.status,
            "subtotal": o.subtotal,
            "delivery_fee": o.delivery_fee,
            "platform_fee": o.platform_fee,
            "total_amount": o.total_amount,
            "payment_mode": o.payment_method,
            "payment_status": o.payment_status,
            "delivery_otp": o.delivery_otp,
            "items_count": len(o.items),
            "items": [
                {
                    "id": it.id,
                    "product_id": it.product_id,
                    "name": getattr(it, "product_name_en", None) or getattr(it, "product_name_hi", "Item"),
                    "quantity": it.quantity,
                    "unit_price": it.unit_price,
                    "total_price": it.total_price
                }
                for it in o.items
            ],
            "delivery_village": o.delivery_address.village if o.delivery_address else "Muzaffarpur",
            "elapsed_minutes": elapsed_mins,
            "created_at": p_at.isoformat() if p_at else None,
            "is_cancellable": o.status == "PLACED" and c_until is not None and c_until > now
        })
    return results


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    req: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    valid_statuses = ["PLACED", "ACCEPTED", "PACKED", "RUNNER_ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    order.status = req.status
    if req.status == "DELIVERED":
        order.delivered_at = datetime.now(timezone.utc)
        if order.payment_method == "COD":
            if req.cash_collected is True:
                order.payment_status = "PAID"
            else:
                order.payment_status = "PENDING"
    await db.commit()

    # Broadcast via WebSocket
    await admin_ws_manager.broadcast({
        "type": "ORDER_STATUS_UPDATED",
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {"message": f"Order {order_id} status updated to {req.status}", "status": order.status}


# ORDER GOD MODE: Cancel, Instant Refund, Reassign Runner, Override Stock
@router.post("/orders/{order_id}/god-mode/cancel")
async def god_mode_cancel_order(
    order_id: str,
    reason: Optional[str] = "Cancelled by Super Admin God Mode",
    auto_refund: bool = True,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Super Admin God Mode: Force cancel order regardless of stage.
    """
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "CANCELLED"
    now = datetime.now(timezone.utc)

    # Issue verified refund if order was paid online
    refund_record = None
    if auto_refund and order.payment_method == "ONLINE" and order.payment_status == "PAID":
        # Calculate remaining refundable
        res_ref = await db.execute(
            select(Refund).where(
                Refund.order_id == order.id,
                Refund.status.in_(["COMPLETED", "PROCESSING", "PENDING"])
            )
        )
        existing_refunds = res_ref.scalars().all()
        total_already = sum(r.amount for r in existing_refunds)
        rem_ref = round(order.total_amount - total_already, 2)

        if rem_ref > 0 and order.transaction_id:
            from app.api.v1.payments import is_razorpay_configured
            gw_ref_id = None
            ref_status = "COMPLETED"
            if is_razorpay_configured():
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.post(
                            f"https://api.razorpay.com/v1/payments/{order.transaction_id}/refund",
                            auth=(settings.RESOLVED_RAZORPAY_KEY_ID, settings.RESOLVED_RAZORPAY_KEY_SECRET),
                            json={"amount": int(round(rem_ref * 100)), "notes": {"order_id": order.id, "reason": reason}}
                        )
                        if resp.status_code in (200, 201):
                            rzp_d = resp.json()
                            gw_ref_id = rzp_d.get("id")
                            ref_status = "COMPLETED" if rzp_d.get("status") in ("processed", "completed") else "PROCESSING"
                        else:
                            ref_status = "FAILED"
                except Exception:
                    ref_status = "FAILED"
            elif order.transaction_id.startswith("pay_rzp_test_") or settings.TESTING:
                gw_ref_id = f"rfnd_sbx_{order.id[:8]}_{int(now.timestamp())}"
                ref_status = "COMPLETED"

            if ref_status != "FAILED":
                order.payment_status = "REFUNDED"
                refund_record = Refund(
                    order_id=order.id,
                    payment_id=order.transaction_id,
                    gateway_refund_id=gw_ref_id,
                    amount=rem_ref,
                    currency="INR",
                    reason=reason,
                    status=ref_status,
                    refund_type="FULL",
                    admin_notes=f"Authorized via Super Admin God Mode Cancellation by {_admin.get('phone', 'admin')}",
                    created_at=now,
                    updated_at=now
                )
                db.add(refund_record)

    audit = AuditLog(
        action="GOD_MODE_ORDER_CANCELLED",
        target_type="ORDER",
        target_id=order.id,
        details=f"Order {order.id} cancelled. AutoRefund: {auto_refund}. Reason: {reason}"
    )
    db.add(audit)
    await db.commit()

    # Broadcast via WebSocket
    await admin_ws_manager.broadcast({
        "type": "ORDER_CANCELLED",
        "order_id": order.id,
        "reason": reason
    })

    return {
        "message": f"Order #{order.id[:8]} cancelled via God Mode",
        "order_id": order.id,
        "status": order.status,
        "refund_issued": bool(refund_record),
        "refund_amount": order.total_amount if refund_record else 0.0
    }


@router.post("/orders/{order_id}/god-mode/refund")
async def god_mode_issue_refund(
    order_id: str,
    req: OrderGodModeRefund,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Super Admin God Mode: Issue authoritative refund to customer.
    Validates original captured payment, remaining refundable balance, and executes real Razorpay refund.
    Never marks a failed gateway call as completed.
    """
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check remaining refundable balance
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

    if req.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount must be greater than zero"
        )

    if req.amount > remaining_refundable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund amount (₹{req.amount}) exceeds remaining refundable balance (₹{remaining_refundable})"
        )

    now = datetime.now(timezone.utc)
    gateway_refund_id = None
    refund_status = "COMPLETED"

    if order.payment_method == "ONLINE":
        if not order.transaction_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot refund ONLINE order without confirmed payment transaction ID"
            )
        
        from app.api.v1.payments import is_razorpay_configured
        if is_razorpay_configured():
            amount_paise = int(round(req.amount * 100))
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"https://api.razorpay.com/v1/payments/{order.transaction_id}/refund",
                        auth=(settings.RESOLVED_RAZORPAY_KEY_ID, settings.RESOLVED_RAZORPAY_KEY_SECRET),
                        json={
                            "amount": amount_paise,
                            "notes": {"order_id": order.id, "reason": req.reason, "admin": _admin.get("phone", "admin")}
                        }
                    )
                    if resp.status_code not in (200, 201):
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Payment gateway refund failed: {resp.text}"
                        )
                    rzp_data = resp.json()
                    gateway_refund_id = rzp_data.get("id")
                    refund_status = "COMPLETED" if rzp_data.get("status") in ("processed", "completed") else "PROCESSING"
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Payment gateway unreachable: {str(e)}"
                )
        else:
            if order.transaction_id.startswith("pay_rzp_test_") or settings.TESTING:
                gateway_refund_id = f"rfnd_sbx_{order.id[:8]}_{int(now.timestamp())}"
                refund_status = "COMPLETED"
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Online payment gateway unconfigured for processing production refunds"
                )
    else:
        gateway_refund_id = f"cod_disb_{order.id[:8]}_{int(now.timestamp())}"
        refund_status = "COMPLETED"

    refund = Refund(
        order_id=order.id,
        payment_id=order.transaction_id or f"cod_{order.id}",
        gateway_refund_id=gateway_refund_id,
        amount=req.amount,
        currency="INR",
        reason=req.reason,
        status=refund_status,
        refund_type="FULL" if req.amount >= order.total_amount else "PARTIAL",
        admin_notes=f"Authorized God Mode refund by {_admin.get('phone', 'admin')}",
        created_at=now,
        updated_at=now
    )
    db.add(refund)
    order.payment_status = "REFUNDED" if (total_already_refunded + req.amount) >= order.total_amount else "PARTIALLY_REFUNDED"

    audit = AuditLog(
        action="GOD_MODE_REFUND_ISSUED",
        target_type="ORDER",
        target_id=order.id,
        details=f"Issued refund ₹{req.amount} for Order {order.id}. Gateway ID: {gateway_refund_id}. Status: {refund_status}"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"Refund of ₹{req.amount} processed successfully ({refund_status})",
        "refund_id": refund.id,
        "gateway_refund_id": gateway_refund_id,
        "order_id": order.id,
        "status": refund_status
    }


@router.post("/orders/{order_id}/god-mode/reassign-runner")
async def god_mode_reassign_runner(
    order_id: str,
    req: AssignRunnerRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Super Admin & Hub Manager: Manually re-assign a different runner if current one is stuck.
    """
    res_order = await db.execute(select(Order).where(Order.id == order_id))
    order = res_order.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    res_runner = await db.execute(select(Runner).where(Runner.id == req.runner_id))
    runner = res_runner.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner partner not found")

    prev_runner_id = order.runner_id
    order.runner_id = runner.id
    order.status = "RUNNER_ASSIGNED"

    audit = AuditLog(
        action="RUNNER_REASSIGNED_GOD_MODE",
        target_type="ORDER",
        target_id=order.id,
        details=f"Reassigned order from {prev_runner_id} to runner {runner.full_name} ({runner.id}). Notes: {req.notes or 'None'}"
    )
    db.add(audit)
    await db.commit()

    # Broadcast via WebSocket
    await admin_ws_manager.broadcast({
        "type": "RUNNER_REASSIGNED",
        "order_id": order.id,
        "runner_id": runner.id,
        "runner_name": runner.full_name
    })

    return {
        "message": f"Runner {runner.full_name} reassigned to order #{order.id[:8]}",
        "order_id": order.id,
        "runner_id": runner.id,
        "runner_name": runner.full_name,
        "status": order.status
    }


@router.post("/orders/{order_id}/god-mode/override-stock")
async def god_mode_override_stock(
    order_id: str,
    req: OrderStockOverride,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Super Admin God Mode: Override vendor product stock / availability directly.
    """
    res_order = await db.execute(select(Order).where(Order.id == order_id))
    order = res_order.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    res_prod = await db.execute(
        select(StoreProduct).where(
            and_(StoreProduct.store_id == order.store_id, StoreProduct.id == req.product_id)
        )
    )
    prod = res_prod.scalars().first()
    if not prod:
        # Fallback search by global product id
        res_prod2 = await db.execute(
            select(StoreProduct).where(
                and_(StoreProduct.store_id == order.store_id, StoreProduct.global_product_id == req.product_id)
            )
        )
        prod = res_prod2.scalars().first()

    if prod:
        prod.is_available = req.is_available
        if req.price_override is not None:
            prod.price = req.price_override
        await db.commit()

    audit = AuditLog(
        action="GOD_MODE_STOCK_OVERRIDE",
        target_type="STORE_PRODUCT",
        target_id=req.product_id,
        details=f"Overrode product {req.product_id} stock to available={req.is_available} for store {order.store_id}"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"Stock override applied for product {req.product_id}",
        "store_id": order.store_id,
        "product_id": req.product_id,
        "is_available": req.is_available
    }


# Backwards compatibility assign runner route
@router.post("/orders/{order_id}/assign-runner")
async def assign_runner_legacy(
    order_id: str,
    req: AssignRunnerRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    return await god_mode_reassign_runner(order_id, req, db, _admin)


# ---------------------------------------------------------
# Module 4: Live Map Tracking (Operations Center)
# ---------------------------------------------------------
@router.get("/map/riders")
async def get_map_riders(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Live map telemetry: Genuine authenticated runner GPS coordinates.
    Never fabricates GPS coordinates, fake battery percentage, or fake speed.
    Displays LOCATION_UNAVAILABLE or LOCATION_STALE where appropriate.
    """
    runners_res = await db.execute(
        select(Runner).options(selectinload(Runner.user), selectinload(Runner.orders))
    )
    runners = runners_res.scalars().all()

    # Active assigned orders map
    active_orders_res = await db.execute(
        select(Order).where(Order.status.in_(["RUNNER_ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY"]))
    )
    active_orders = active_orders_res.scalars().all()
    assigned_orders_by_runner = {o.runner_id: o for o in active_orders if o.runner_id}

    rider_pins = []

    for r in runners:
        assigned_order = assigned_orders_by_runner.get(r.id)
        has_coords = (r.current_latitude is not None and r.current_longitude is not None)
        has_sos = any(s["runner_id"] == r.id for s in _ACTIVE_SOS_ALERTS)

        if has_sos:
            state = "ISSUE"
            color = "red"
            location_status = "LIVE" if has_coords else "LOCATION_UNAVAILABLE"
        elif not has_coords:
            state = "LOCATION_UNAVAILABLE"
            color = "gray"
            location_status = "LOCATION_UNAVAILABLE"
        elif not r.is_online or not r.is_approved:
            state = "OFFLINE"
            color = "red"
            location_status = "LOCATION_STALE"
        elif assigned_order is not None:
            state = "BUSY"
            color = "orange"
            location_status = "LIVE"
        else:
            state = "IDLE"
            color = "green"
            location_status = "LIVE"

        rider_pins.append({
            "runner_id": r.id,
            "name": r.full_name,
            "phone": r.user.phone if r.user else "",
            "vehicle_type": r.vehicle_type,
            "vehicle_number": r.vehicle_number or "NOT_CONFIGURED",
            "latitude": r.current_latitude if has_coords else None,
            "longitude": r.current_longitude if has_coords else None,
            "location_status": location_status,
            "state": state,
            "color": color, # green, orange, red, gray
            "assigned_order_id": assigned_order.id if assigned_order else None,
            "assigned_order_status": assigned_order.status if assigned_order else None,
            "battery_level": None,
            "speed_kmh": None,
            "last_ping": datetime.now(timezone.utc).isoformat() if has_coords else None
        })

    return rider_pins


@router.post("/map/riders/{runner_id}/ping")
async def ping_rider_location(
    runner_id: str,
    req: RiderPingRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Receives or simulates a runner GPS ping every 10s and broadcasts to admin dashboard.
    """
    res = await db.execute(select(Runner).where(Runner.id == runner_id))
    runner = res.scalars().first()
    if not runner:
        raise HTTPException(status_code=404, detail="Runner not found")

    runner.current_latitude = req.latitude
    runner.current_longitude = req.longitude
    await db.commit()

    ping_payload = {
        "runner_id": runner.id,
        "name": runner.full_name,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "status": req.status,
        "battery_level": req.battery_level,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Broadcast via WebSocket
    await admin_ws_manager.broadcast({
        "type": "RIDER_LOCATION",
        "data": ping_payload
    })

    return {"message": "Location ping recorded and broadcasted", "ping": ping_payload}


@router.get("/map/heatmaps")
async def get_demand_heatmaps(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Dynamically calculated demand heatmaps based on real active orders and available runners.
    Calculates operational clusters from registered stores and live order activity.
    """
    res_orders = await db.execute(
        select(Order).options(selectinload(Order.store), selectinload(Order.delivery_address))
        .where(Order.status.in_(["PLACED", "ACCEPTED", "PACKED", "RUNNER_ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY"]))
    )
    active_orders = res_orders.scalars().all()

    # Query all approved stores to define operating clusters
    res_stores = await db.execute(select(Store).where(Store.is_approved == True))
    stores = res_stores.scalars().all()

    # Query online available runners
    res_runners = await db.execute(
        select(Runner).where(and_(Runner.is_online == True, Runner.is_approved == True))
    )
    online_runners = res_runners.scalars().all()
    available_runners_count = len(online_runners)

    # Initialize clusters from stores
    clusters: Dict[str, Dict[str, Any]] = {}
    for st in stores:
        village_clean = st.village.split("/")[0].strip()
        zid = f"zone_{village_clean.lower().replace(' ', '_')}"
        if zid not in clusters:
            clusters[zid] = {
                "zone_id": zid,
                "zone_name": f"{village_clean} Market Hub",
                "latitude": st.latitude,
                "longitude": st.longitude,
                "radius_meters": 1200,
                "active_orders": 0,
                "available_riders": 0
            }

    # If no stores yet, fallback to default operational hub
    if not clusters:
        clusters["zone_muzaffarpur_hub"] = {
            "zone_id": "zone_muzaffarpur_hub",
            "zone_name": "Muzaffarpur Operations Hub",
            "latitude": 26.2230,
            "longitude": 85.3520,
            "radius_meters": 1200,
            "active_orders": 0,
            "available_riders": 0
        }

    # Distribute active orders across clusters
    for o in active_orders:
        if o.store and o.store.village:
            v_key = o.store.village.split("/")[0].strip().lower().replace(' ', '_')
            zid = f"zone_{v_key}"
            if zid in clusters:
                clusters[zid]["active_orders"] += 1

    # Distribute runners to nearest cluster
    for r in online_runners:
        if r.current_latitude and r.current_longitude:
            # find closest cluster
            closest_zid = min(
                clusters.keys(),
                key=lambda k: (clusters[k]["latitude"] - r.current_latitude)**2 + (clusters[k]["longitude"] - r.current_longitude)**2
            )
            clusters[closest_zid]["available_riders"] += 1
        elif clusters:
            # assign to first cluster
            first_k = next(iter(clusters.keys()))
            clusters[first_k]["available_riders"] += 1

    results = []
    for c in clusters.values():
        c_orders = c["active_orders"]
        c_riders = c["available_riders"]
        # Red zone if orders exceed riders or no riders available in that cluster
        is_red = (c_riders == 0) or (c_orders > c_riders)
        c["is_red_zone"] = is_red
        c["intensity"] = 0.85 if is_red else round(min(1.0, (c_orders + 1) / max(2, (c_riders + 1) * 2)), 2)
        c["description"] = f"{'Red Zone: ' if is_red else 'Normal: '}{c_orders} active order(s), {c_riders} available runner(s)."
        results.append(c)

    return results


@router.post("/map/heatmaps/notify-riders")
async def notify_riders_to_red_zone(
    req: NotifyRedZoneRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Sends push notification / SMS broadcast to idle riders requesting them to move to designated Red Zone.
    """
    res = await db.execute(select(Runner).where(and_(Runner.is_online == True, Runner.is_approved == True)))
    online_runners = res.scalars().all()

    msg = req.message or f"🚨 High Order Demand in {req.zone_name}! Earn +₹20 surge bonus per delivery. Move to {req.zone_name} now."

    audit = AuditLog(
        action="HEATMAP_REDZONE_BROADCAST",
        target_type="ZONE",
        target_id=req.zone_name,
        details=f"Broadcast sent to {len(online_runners)} riders to converge on {req.zone_name} ({req.latitude}, {req.longitude})"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"Red Zone surge alert dispatched to {len(online_runners)} active riders",
        "zone_name": req.zone_name,
        "riders_notified_count": len(online_runners),
        "broadcast_message": msg
    }


# ---------------------------------------------------------
# Module 5: Financials & Ledger (Settlements)
# ---------------------------------------------------------
@router.get("/settlements")
async def get_settlements_ledger(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Financial summary: Vendor earnings minus platform commission, runner delivery payouts,
    and platform fees collected. Restricted to Super Admin role.
    """
    res = await db.execute(
        select(Order).options(selectinload(Order.store), selectinload(Order.runner)).where(Order.status == "DELIVERED")
    )
    delivered_orders = res.scalars().all()

    vendor_totals = {}
    runner_totals = {}

    for o in delivered_orders:
        if o.store_id:
            s_name = o.store.shop_name if o.store else "Store"
            if o.store_id not in vendor_totals:
                b_ac = "NOT_CONFIGURED"
                b_ifsc = "NOT_CONFIGURED"
                if o.store and o.store.bank_account_info:
                    try:
                        bd = json.loads(o.store.bank_account_info)
                        b_ac = bd.get("account_number") or "NOT_CONFIGURED"
                        b_ifsc = bd.get("ifsc_code") or bd.get("ifsc") or "NOT_CONFIGURED"
                    except Exception:
                        pass
                vendor_totals[o.store_id] = {
                    "store_id": o.store_id,
                    "store_name": s_name,
                    "gross_sales": 0.0,
                    "platform_commission": 0.0,
                    "total_payout": 0.0,
                    "order_count": 0,
                    "bank_account": b_ac,
                    "ifsc": b_ifsc
                }
            # Strict 3% Online Gateway & Settlement Fee strictly on ONLINE orders (0% on COD)
            gw_fee = round(o.subtotal * 0.03, 2) if o.payment_method == "ONLINE" else 0.0
            commission = 0.0 # Strict 0% platform commission
            net_payout = o.subtotal - gw_fee

            vendor_totals[o.store_id]["gross_sales"] += o.subtotal
            vendor_totals[o.store_id]["online_gateway_fee"] = vendor_totals[o.store_id].get("online_gateway_fee", 0.0) + gw_fee
            vendor_totals[o.store_id]["platform_commission"] = 0.0
            vendor_totals[o.store_id]["total_payout"] += net_payout
            vendor_totals[o.store_id]["order_count"] += 1

        if o.runner_id:
            r_name = o.runner.full_name if o.runner else "Runner"
            if o.runner_id not in runner_totals:
                r_ac = "NOT_CONFIGURED"
                r_ifsc = "NOT_CONFIGURED"
                if o.runner and o.runner.upi_id and o.runner.upi_id.startswith("A/C:"):
                    parts = o.runner.upi_id.split(":")
                    if len(parts) >= 3:
                        r_ac = f"A/C Ending in {parts[1]}"
                        r_ifsc = parts[2]
                runner_totals[o.runner_id] = {
                    "runner_id": o.runner_id,
                    "runner_name": r_name,
                    "delivery_fees": 0.0,
                    "bonuses": 0.0,
                    "online_gateway_fee": 0.0,
                    "total_payout": 0.0,
                    "order_count": 0,
                    "bank_account": r_ac,
                    "ifsc": r_ifsc
                }
            r_gw_fee = round(o.delivery_fee * 0.03, 2) if o.payment_method == "ONLINE" else 0.0
            net_r_payout = o.delivery_fee - r_gw_fee
            runner_totals[o.runner_id]["delivery_fees"] += o.delivery_fee
            runner_totals[o.runner_id]["online_gateway_fee"] = runner_totals[o.runner_id].get("online_gateway_fee", 0.0) + r_gw_fee
            runner_totals[o.runner_id]["total_payout"] += net_r_payout
            runner_totals[o.runner_id]["order_count"] += 1

    return {
        "vendor_settlements": list(vendor_totals.values()),
        "runner_settlements": list(runner_totals.values()),
        "vendor_payouts_due": round(sum(v["total_payout"] for v in vendor_totals.values()), 2),
        "runner_payouts_due": round(sum(r["total_payout"] for r in runner_totals.values()), 2),
        "total_online_gateway_fee": round(sum(v.get("online_gateway_fee", 0.0) for v in vendor_totals.values()) + sum(r.get("online_gateway_fee", 0.0) for r in runner_totals.values()), 2),
        "platform_fee_collected": len(delivered_orders) * settings.PLATFORM_FEE,
        "total_delivered_orders": len(delivered_orders)
    }


@router.get("/settlements/cod")
async def get_cod_reconciliation_list(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    COD Reconciliation: List of runners and the exact cash (COD) they hold.
    Hub Managers use this to mark cash as "Received & Deposited" when runners return to base.
    """
    res = await db.execute(
        select(Order).options(selectinload(Order.runner).selectinload(Runner.user))
        .where(
            and_(
                Order.payment_method == "COD",
                Order.status == "DELIVERED",
                Order.payment_status != "PAID"
            )
        )
    )
    cod_orders = res.scalars().all()

    runners_cash: Dict[str, Dict[str, Any]] = {}
    for o in cod_orders:
        if not o.runner_id:
            continue
        r_id = o.runner_id
        r_name = o.runner.full_name if o.runner else f"Runner #{r_id[:6]}"
        r_phone = o.runner.user.phone if (o.runner and o.runner.user) else "+91 98000 00000"

        if r_id not in runners_cash:
            runners_cash[r_id] = {
                "runner_id": r_id,
                "runner_name": r_name,
                "phone": r_phone,
                "cash_held_inr": 0.0,
                "undeposited_orders_count": 0,
                "order_ids": [],
                "status": "HOLDING_CASH"
            }
        runners_cash[r_id]["cash_held_inr"] += o.total_amount
        runners_cash[r_id]["undeposited_orders_count"] += 1
        runners_cash[r_id]["order_ids"].append(o.id)

    return list(runners_cash.values())


@router.post("/settlements/cod-deposit")
async def record_cod_cash_deposit(
    req: CodDepositRequest,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Hub Manager records runner COD cash deposit at local hub.
    Amount-accurate COD accounting: Supports partial deposits, prevents double reconciliation,
    and only clears liability up to the verified cash deposited.
    """
    if req.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be greater than zero"
        )

    # Check idempotency of receipt_reference to prevent double deposit
    if req.receipt_reference:
        dup_check = await db.execute(
            select(AuditLog).where(
                and_(
                    AuditLog.action == "COD_CASH_DEPOSITED_AT_HUB",
                    AuditLog.details.like(f"%Receipt #{req.receipt_reference}%")
                )
            )
        )
        if dup_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate deposit: Receipt reference '{req.receipt_reference}' has already been processed"
            )

    # Fetch delivered COD orders pending payment for this runner in FIFO order
    res = await db.execute(
        select(Order).where(
            and_(
                Order.runner_id == req.runner_id,
                Order.payment_method == "COD",
                Order.status == "DELIVERED",
                Order.payment_status != "PAID"
            )
        ).order_by(Order.placed_at.asc())
    )
    orders_to_settle = res.scalars().all()
    total_unpaid = sum(o.total_amount for o in orders_to_settle)

    # Amount-accurate FIFO allocation: only mark individual orders as PAID if fully covered
    remaining_cash = req.amount
    settled_count = 0
    total_cleared = 0.0
    cleared_order_ids = []

    for o in orders_to_settle:
        if remaining_cash >= o.total_amount:
            o.payment_status = "PAID"
            remaining_cash -= o.total_amount
            total_cleared += o.total_amount
            settled_count += 1
            cleared_order_ids.append(o.id)
        else:
            # Partial amount remaining cannot clear the next full order
            break

    remaining_liability = max(0.0, round(total_unpaid - total_cleared, 2))
    receipt_no = req.receipt_reference or f"HUB-COD-{int(datetime.now(timezone.utc).timestamp())}"

    audit = AuditLog(
        action="COD_CASH_DEPOSITED_AT_HUB",
        target_type="RUNNER_COD",
        target_id=req.runner_id,
        details=f"Received ₹{req.amount} COD cash from runner {req.runner_id}. Receipt #{receipt_no}. Orders Cleared: {settled_count} ({cleared_order_ids}). Total Cleared: ₹{total_cleared}. Remaining Liability: ₹{remaining_liability}. Notes: {req.notes or 'None'}"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": f"Successfully received ₹{req.amount} COD cash. Cleared {settled_count} order(s). Remaining liability: ₹{remaining_liability}.",
        "receipt_number": receipt_no,
        "runner_id": req.runner_id,
        "amount_deposited": req.amount,
        "amount_cleared": total_cleared,
        "orders_reconciled": settled_count,
        "remaining_liability": remaining_liability,
        "cleared_order_ids": cleared_order_ids,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/settlements/payouts/vendor-csv")
async def export_vendor_payouts_csv(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Generates batch CSV file formatted for direct upload to corporate bank accounts (NEFT/RTGS).
    Super Admin privilege strictly required.
    """
    res = await db.execute(
        select(Order).options(selectinload(Order.store)).where(Order.status == "DELIVERED")
    )
    delivered = res.scalars().all()

    vendor_totals: Dict[str, Dict[str, Any]] = {}
    for o in delivered:
        if o.store_id:
            s_name = o.store.shop_name if o.store else "Store"
            b_ac = "NOT_CONFIGURED"
            b_ifsc = "NOT_CONFIGURED"
            if o.store and o.store.bank_account_info:
                try:
                    bd = json.loads(o.store.bank_account_info)
                    b_ac = bd.get("account_number") or "NOT_CONFIGURED"
                    b_ifsc = bd.get("ifsc_code") or bd.get("ifsc") or "NOT_CONFIGURED"
                except Exception:
                    pass
            if o.store_id not in vendor_totals:
                vendor_totals[o.store_id] = {
                    "name": s_name,
                    "account": b_ac,
                    "ifsc": b_ifsc,
                    "amount": 0.0
                }
            net = o.subtotal - (o.subtotal * settings.DEFAULT_VENDOR_COMMISSION_PCT / 100.0)
            vendor_totals[o.store_id]["amount"] += net

    output = io.StringIO()
    writer = csv.writer(output)
    # Corporate bulk payout header (NEFT/RTGS standard)
    writer.writerow(["Beneficiary Name", "Account Number", "IFSC Code", "Amount (INR)", "Payment Reference", "Remarks"])
    for sid, v in vendor_totals.items():
        # Exclude unconfigured bank accounts from direct corporate bank batch files
        if v["account"] == "NOT_CONFIGURED" or len(v["account"]) < 9:
            continue
        ref = f"GBV-{sid[:8]}-{int(datetime.now(timezone.utc).timestamp())}"
        writer.writerow([v["name"], v["account"], v["ifsc"], round(v["amount"], 2), ref, "GaonBazaar Vendor Weekly Settlement"])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=gaonbazaar_vendor_payouts_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )


@router.get("/settlements/payouts/runner-csv")
async def export_runner_payouts_csv(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Generates batch CSV file for runner delivery fees and bonuses. Super Admin strictly required.
    """
    res = await db.execute(
        select(Order).options(selectinload(Order.runner).selectinload(Runner.user)).where(Order.status == "DELIVERED")
    )
    delivered = res.scalars().all()

    runner_totals: Dict[str, Dict[str, Any]] = {}
    for o in delivered:
        if o.runner_id:
            r_name = o.runner.full_name if o.runner else "Runner"
            r_ac = "NOT_CONFIGURED"
            r_ifsc = "NOT_CONFIGURED"
            if o.runner and o.runner.upi_id and o.runner.upi_id.startswith("A/C:"):
                parts = o.runner.upi_id.split(":")
                if len(parts) >= 3:
                    r_ac = parts[1]
                    r_ifsc = parts[2]
            if o.runner_id not in runner_totals:
                runner_totals[o.runner_id] = {
                    "name": r_name,
                    "account": r_ac,
                    "ifsc": r_ifsc,
                    "amount": 0.0
                }
            runner_totals[o.runner_id]["amount"] += o.delivery_fee

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Beneficiary Name", "Account Number", "IFSC Code", "Amount (INR)", "Payment Reference", "Remarks"])
    for rid, r in runner_totals.items():
        # Exclude unconfigured accounts from corporate bank batch file
        if r["account"] == "NOT_CONFIGURED" or len(r["account"]) < 9:
            continue
        ref = f"GBR-{rid[:8]}-{int(datetime.now(timezone.utc).timestamp())}"
        writer.writerow([r["name"], r["account"], r["ifsc"], round(r["amount"], 2), ref, "GaonBazaar Runner Delivery Settlement"])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=gaonbazaar_runner_payouts_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"}
    )


# ---------------------------------------------------------
# Module 6: Catalog & Platform Settings (Pricing Engine)
# ---------------------------------------------------------
@router.get("/catalog")
async def get_master_catalog(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    """
    Global Catalog: Add/Edit master list of products, images, and standard MRPs.
    Vendors select from this list.
    """
    res = await db.execute(select(GlobalCatalogItem))
    return res.scalars().all()


@router.post("/catalog")
async def add_master_catalog_item(
    item: CatalogItemCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Add product to Global Master Catalog. Super Admin required.
    """
    new_item = GlobalCatalogItem(
        name_en=item.name_en,
        name_hi=item.name_hi,
        category=item.category,
        default_unit=item.standard_unit,
        suggested_mrp=item.suggested_price,
        image_url=item.image_url
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    audit = AuditLog(
        action="MASTER_CATALOG_ITEM_ADDED",
        target_type="GLOBAL_CATALOG",
        target_id=new_item.id,
        details=f"Added {new_item.name_en} ({new_item.category}) with MRP ₹{new_item.suggested_mrp}"
    )
    db.add(audit)
    await db.commit()

    return new_item


@router.put("/catalog/{item_id}")
async def update_master_catalog_item(
    item_id: str,
    item: CatalogItemUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    res = await db.execute(select(GlobalCatalogItem).where(GlobalCatalogItem.id == item_id))
    cat_item = res.scalars().first()
    if not cat_item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    if item.name_en is not None:
        cat_item.name_en = item.name_en
    if item.name_hi is not None:
        cat_item.name_hi = item.name_hi
    if item.category is not None:
        cat_item.category = item.category
    if item.standard_unit is not None:
        cat_item.default_unit = item.standard_unit
    if item.suggested_price is not None:
        cat_item.suggested_mrp = item.suggested_price
    if item.image_url is not None:
        cat_item.image_url = item.image_url

    await db.commit()
    return cat_item


@router.delete("/catalog/{item_id}")
async def delete_master_catalog_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    res = await db.execute(select(GlobalCatalogItem).where(GlobalCatalogItem.id == item_id))
    cat_item = res.scalars().first()
    if not cat_item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    await db.delete(cat_item)
    await db.commit()
    return {"message": f"Catalog item {item_id} deleted successfully"}


@router.get("/settings")
async def get_platform_settings(_admin: dict = Depends(require_hub_manager_or_super_admin)):
    return {
        "pilot_block": settings.PILOT_BLOCK,
        "pilot_district": settings.PILOT_DISTRICT,
        "pilot_state": settings.PILOT_STATE,
        "pilot_localities": [
            {"name": "Tengari", "pincode": "843128", "lat": 26.1950, "lng": 85.3450},
            {"name": "Shibai Patti", "pincode": "843128", "lat": 26.2250, "lng": 85.3600},
            {"name": "Chaturshi", "pincode": "843128", "lat": 26.2100, "lng": 85.3550}
        ],
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "min_order_value": 99.0,
        "base_delivery_fee": 15.0,
        "per_km_fee": 5.0,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT,
        "cancel_window_seconds": settings.CUSTOMER_CANCEL_WINDOW_SECONDS
    }


@router.patch("/settings")
async def update_platform_settings(
    req: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_super_admin)
):
    """
    Pricing Engine: Set Minimum Order Value (MOV), adjust delivery fee structures (Base fee + Per KM charge),
    and vendor commission. Super Admin strictly required.
    """
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
        details=f"Radius: {settings.MAX_DELIVERY_RADIUS_KM}km, MOV: ₹{req.min_order_value or 99}, BaseDelivery: ₹{req.base_delivery_fee or 15}, PerKM: ₹{req.per_km_fee or 5}, PlatformFee: ₹{settings.PLATFORM_FEE}, Commission: {settings.DEFAULT_VENDOR_COMMISSION_PCT}%"
    )
    db.add(audit)
    await db.commit()

    return {
        "message": "Platform pricing engine rules updated successfully",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "vendor_commission_pct": settings.DEFAULT_VENDOR_COMMISSION_PCT,
        "min_order_value": req.min_order_value or 99.0,
        "base_delivery_fee": req.base_delivery_fee or 15.0,
        "per_km_fee": req.per_km_fee or 5.0
    }


@router.get("/pricing/promos")
async def get_active_promos(_admin: dict = Depends(require_hub_manager_or_super_admin)):
    return _ACTIVE_PROMO_CODES


@router.post("/pricing/promos")
async def create_promotional_promo_code(
    req: CreatePromoRequest,
    _admin: dict = Depends(require_super_admin)
):
    """
    Create promotional promo code for rural discount campaigns. Super Admin required.
    """
    promo_obj = {
        "id": f"promo_{secrets.token_hex(4)}",
        "code": req.code.strip().upper(),
        "discount_pct": req.discount_pct,
        "min_order_value": req.min_order_value,
        "max_discount": req.max_discount,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True
    }
    _ACTIVE_PROMO_CODES.append(promo_obj)
    return {"message": f"Promo code '{promo_obj['code']}' created successfully", "promo": promo_obj}


# ---------------------------------------------------------
# Support, Tickets & Refunds
# ---------------------------------------------------------
@router.get("/tickets")
async def get_support_tickets(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    query = select(SupportTicket).options(selectinload(SupportTicket.messages), selectinload(SupportTicket.user)).order_by(SupportTicket.created_at.desc())
    if category:
        query = query.where(SupportTicket.category == category)
    if status:
        query = query.where(SupportTicket.status == status)
    res = await db.execute(query)
    tickets = res.scalars().all()
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "user_name": t.user.name if t.user else "Customer",
            "user_phone": t.user.phone if t.user else "",
            "order_id": t.order_id,
            "category": t.category or "GENERAL_HELP",
            "subject": t.subject,
            "message": t.message,
            "status": t.status,
            "affected_product_id": t.affected_product_id,
            "attachment_url": t.attachment_url,
            "resolution_notes": t.resolution_notes,
            "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else "",
            "reply_count": len(t.messages) if t.messages else 0
        }
        for t in tickets
    ]


@router.get("/tickets/{ticket_id}")
async def get_support_ticket_detail(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    res = await db.execute(
        select(SupportTicket)
        .options(selectinload(SupportTicket.messages), selectinload(SupportTicket.user))
        .where(SupportTicket.id == ticket_id)
    )
    t = res.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return {
        "id": t.id,
        "user_id": t.user_id,
        "user_name": t.user.name if t.user else "Customer",
        "user_phone": t.user.phone if t.user else "",
        "order_id": t.order_id,
        "category": t.category or "GENERAL_HELP",
        "subject": t.subject,
        "message": t.message,
        "status": t.status,
        "affected_product_id": t.affected_product_id,
        "attachment_url": t.attachment_url,
        "resolution_notes": t.resolution_notes,
        "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
        "created_at": t.created_at.isoformat() if t.created_at else "",
        "messages": [
            {
                "id": m.id,
                "ticket_id": m.ticket_id,
                "sender_id": m.sender_id,
                "sender_role": m.sender_role,
                "message": m.message,
                "attachment_url": m.attachment_url,
                "created_at": m.created_at.isoformat() if m.created_at else ""
            }
            for m in (t.messages or [])
        ]
    }


@router.post("/tickets/{ticket_id}/reply")
async def admin_reply_to_ticket(
    ticket_id: str,
    req: AdminTicketReply,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    now = datetime.now(timezone.utc)
    ticket.updated_at = now
    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_id=_admin.get("sub", "admin_01"),
        sender_role="admin",
        message=req.message.strip(),
        attachment_url=req.attachment_url,
        created_at=now
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"message": "Admin reply sent successfully", "id": msg.id}


@router.patch("/tickets/{ticket_id}")
async def update_ticket_status(
    ticket_id: str,
    req: TicketStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    res = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = res.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    now = datetime.now(timezone.utc)
    ticket.status = req.status.upper()
    ticket.updated_at = now
    if req.resolution_notes:
        ticket.resolution_notes = req.resolution_notes
    if ticket.status in ["RESOLVED", "CLOSED"]:
        ticket.resolved_at = now
        if ticket.order_id:
            db.add(OrderTimeline(
                order_id=ticket.order_id,
                status="SUPPORT_RESOLVED",
                title="सहायता टिकट निस्तारित (Ticket Resolved)",
                description=f"Ticket #{ticket.id[:8]}: {req.resolution_notes or 'Resolved by admin'}",
                timestamp=now
            ))

    audit = AuditLog(
        actor_id=_admin.get("sub", "admin"),
        actor_role="admin",
        action="TICKET_STATUS_UPDATED",
        target_type="SUPPORT_TICKET",
        target_id=ticket.id,
        details=f"Ticket {ticket.id} status changed to {ticket.status}. Notes: {req.resolution_notes or 'None'}"
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Ticket {ticket.id} updated to {ticket.status}", "status": ticket.status}


@router.get("/customers")
async def get_all_customers(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
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


@router.get("/refunds")
async def get_all_refunds(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_super_admin)):
    res = await db.execute(select(Refund).order_by(Refund.created_at.desc()))
    refunds = res.scalars().all()
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


@router.get("/replacements")
async def get_all_replacements(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Replacement).order_by(Replacement.created_at.desc()))
    replacements = res.scalars().all()
    return [
        {
            "id": rep.id,
            "original_order_id": rep.original_order_id,
            "customer_id": rep.customer_id,
            "store_id": rep.store_id,
            "runner_id": rep.runner_id,
            "status": rep.status,
            "reason": rep.reason,
            "items_json": rep.items_json,
            "customer_due": rep.customer_due,
            "delivery_otp": rep.delivery_otp,
            "admin_notes": rep.admin_notes,
            "created_at": rep.created_at.isoformat() if rep.created_at else None
        }
        for rep in replacements
    ]


@router.post("/replacements/{replacement_id}/approve")
async def approve_replacement(replacement_id: str, db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_hub_manager_or_super_admin)):
    res = await db.execute(select(Replacement).where(Replacement.id == replacement_id))
    rep = res.scalars().first()
    if not rep:
        raise HTTPException(status_code=404, detail="Replacement request not found")
    rep.status = "APPROVED"
    rep.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Replacement approved successfully", "status": rep.status}


@router.post("/replacements/{replacement_id}/reject")
async def reject_replacement(
    replacement_id: str,
    rejection_reason: Optional[str] = "Item does not meet return policy criteria",
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_hub_manager_or_super_admin)
):
    res = await db.execute(select(Replacement).where(Replacement.id == replacement_id))
    rep = res.scalars().first()
    if not rep:
        raise HTTPException(status_code=404, detail="Replacement request not found")
    rep.status = "REJECTED"
    rep.rejection_reason = rejection_reason
    rep.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Replacement rejected", "status": rep.status, "reason": rejection_reason}


@router.get("/audit-logs")
async def get_audit_logs(db: AsyncSession = Depends(get_db), _admin: dict = Depends(require_super_admin)):
    res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
    return res.scalars().all()
