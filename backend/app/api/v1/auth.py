import random
import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.db.session import get_db
from app.models.base import User, Store, Runner
from app.schemas.auth import (
    SendOTPRequest, SendOTPResponse, VerifyOTPRequest, TokenResponse, UserInfo, UpdateProfileRequest
)
from app.core.security import create_access_token, get_current_user_payload

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Designated test phone personas whitelist
TEST_PHONE_WHITELIST = {
    "9800000000", # Customer
    "9800000001", # Vendor 1
    "9800000002", # Vendor 2
    "9800000003", # Runner 1
    "9800000099", # Super Admin
}

def is_whitelisted_test_phone(phone: str) -> bool:
    """Returns True if the phone is an authorized test persona in non-production environment."""
    if getattr(settings, "ENVIRONMENT", "").lower() == "production":
        return False
    return phone in TEST_PHONE_WHITELIST

# In-memory OTP storage for rapid verification in dev/staging
OTP_STORAGE = {}

@router.post("/otp/send", response_model=SendOTPResponse)
async def send_otp(payload: SendOTPRequest):
    now_ts = datetime.now(timezone.utc).timestamp()
    stored = OTP_STORAGE.get(payload.phone)

    # Rate limiting: minimum 15 seconds between OTP requests per phone (bypassed in pytest if testing)
    if not getattr(settings, "TESTING", False) and stored and (now_ts - stored.get("last_sent_at", 0)) < 15:
        wait_sec = int(15 - (now_ts - stored["last_sent_at"]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"कृपया पुनः प्रयास करने से पहले {wait_sec} सेकंड प्रतीक्षा करें (Please wait before requesting another OTP)"
        )

    # Generate challenge: fixed challenge for 5 pilot test personas in dev/staging, crypto-random for public
    if is_whitelisted_test_phone(payload.phone):
        otp_code = "123456"
    else:
        otp_code = f"{secrets.SystemRandom().randint(100000, 999999)}"

    session_id = f"sess_{payload.phone}_{int(now_ts)}"
    OTP_STORAGE[payload.phone] = {
        "otp": otp_code,
        "role": payload.role,
        "expires_at": now_ts + 300,
        "attempts": 0,
        "last_sent_at": now_ts
    }

    # CRITICAL: Never return usable authentication codes in public response
    return SendOTPResponse(
        message=f"OTP challenge issued to +91 {payload.phone}",
        session_id=session_id,
        expires_in=300,
        mock_otp=None
    )

@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    now_ts = datetime.now(timezone.utc).timestamp()
    stored = OTP_STORAGE.get(payload.phone)

    # 1. Challenge issuance check: Must have requested an OTP first
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="कोई सक्रिय ओटीपी अनुरोध नहीं मिला। कृपया पहले ओटीपी भेजें (No active OTP challenge found. Please request an OTP first)"
        )

    # 2. Enforce 5-minute expiry
    if stored.get("expires_at", 0) < now_ts:
        OTP_STORAGE.pop(payload.phone, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ओटीपी की समय सीमा समाप्त हो गई है (OTP has expired. Please request a new OTP)"
        )

    # 3. Rate-limit invalid attempts (max 3 before lockout)
    stored["attempts"] = stored.get("attempts", 0) + 1
    if stored["attempts"] > 3:
        OTP_STORAGE.pop(payload.phone, None)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="अधिकतम प्रयास सीमा समाप्त। कृपया नया ओटीपी अनुरोध करें (Maximum OTP verification attempts exceeded)"
        )

    # 4. Strict constant-time OTP validation
    if not secrets.compare_digest(str(stored.get("otp")), str(payload.otp)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="गलत ओटीपी दर्ज किया गया है (Invalid OTP code)"
        )

    # 5. Prevent replay attacks: invalidate challenge immediately upon success
    role = stored.get("role", payload.role or "customer")
    OTP_STORAGE.pop(payload.phone, None)
    
    # Query or create user in DB
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalars().first()
    
    if not user:
        user = User(
            phone=payload.phone,
            name=payload.name or f"User {payload.phone[-4:]}",
            role=role,
            preferred_language="hi"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # If Vendor, create linked Store entry (Pending Admin Approval)
        if role == "vendor":
            store = Store(
                owner_id=user.id,
                shop_name=f"{user.name}'s Kirana",
                owner_name=user.name or "Shopkeeper",
                category="Grocery",
                latitude=26.2230,
                longitude=85.3520,
                village="Chaturshi",
                is_approved=False # Strict Admin Approval Required
            )
            db.add(store)
            await db.commit()
            
        # If Runner, create linked Runner entry (Pending Admin Approval)
        elif role == "runner":
            runner = Runner(
                user_id=user.id,
                full_name=user.name or "Runner Partner",
                vehicle_type="Motorcycle",
                is_approved=False, # Strict Admin Approval Required
                is_online=False,
                current_latitude=26.2230,
                current_longitude=85.3520
            )
            db.add(runner)
            await db.commit()
            
    # Generate JWT
    token_data = {
        "sub": user.id,
        "phone": user.phone,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            phone=user.phone,
            name=user.name,
            role=user.role,
            preferred_language=user.preferred_language,
            is_active=user.is_active
        )
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserInfo(
        id=user.id,
        phone=user.phone,
        name=user.name,
        email=user.email,
        role=user.role,
        preferred_language=user.preferred_language,
        is_active=user.is_active
    )

@router.patch("/me", response_model=UserInfo)
async def update_current_user(
    req: UpdateProfileRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if req.name is not None:
        user.name = req.name.strip()
    if req.email is not None:
        user.email = req.email.strip()
    if req.preferred_language is not None:
        user.preferred_language = req.preferred_language.strip()
        
    await db.commit()
    await db.refresh(user)
    
    return UserInfo(
        id=user.id,
        phone=user.phone,
        name=user.name,
        email=user.email,
        role=user.role,
        preferred_language=user.preferred_language,
        is_active=user.is_active
    )
