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
    """Returns True if the phone is an authorized test persona or running under test mode."""
    if phone in TEST_PHONE_WHITELIST:
        return True
    if phone.startswith("98000000"):
        return True
    if getattr(settings, "TESTING", False):
        return True
    return False

# In-memory OTP storage for rapid verification in dev/staging
OTP_STORAGE = {}

@router.post("/otp/send", response_model=SendOTPResponse)
async def send_otp(payload: SendOTPRequest):
    session_id = f"sess_{payload.phone}_{int(datetime.now(timezone.utc).timestamp())}"
    now_ts = datetime.now(timezone.utc).timestamp()
    
    # Restrict test OTP to whitelisted test phones only
    if is_whitelisted_test_phone(payload.phone):
        otp_code = "123456"
        mock_otp_return = "123456"
    else:
        # Secure cryptographically strong 6-digit random code for public numbers
        otp_code = f"{secrets.SystemRandom().randint(100000, 999999)}"
        mock_otp_return = None # NEVER leak OTP in API response for real public numbers
    
    OTP_STORAGE[payload.phone] = {
        "otp": otp_code,
        "role": payload.role,
        "expires_at": now_ts + 300
    }
    
    return SendOTPResponse(
        message=f"OTP sent to +91 {payload.phone}",
        session_id=session_id,
        expires_in=300,
        mock_otp=mock_otp_return
    )

@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    now_ts = datetime.now(timezone.utc).timestamp()
    stored = OTP_STORAGE.get(payload.phone)
    
    # 1. Enforce 5-minute expiry
    if stored and stored.get("expires_at", 0) < now_ts:
        OTP_STORAGE.pop(payload.phone, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ओटीपी की समय सीमा समाप्त हो गई है (OTP has expired. Please request a new OTP)"
        )
        
    # 2. Strict OTP validation
    is_test = is_whitelisted_test_phone(payload.phone)
    if is_test and payload.otp == "123456":
        is_valid = True
    elif stored and stored.get("otp") == payload.otp:
        is_valid = True
    else:
        is_valid = False
        
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="गलत ओटीपी दर्ज किया गया है (Invalid OTP code)"
        )
        
    # Prevent replay attacks: invalidate once verified
    if payload.phone in OTP_STORAGE:
        OTP_STORAGE.pop(payload.phone, None)
            
    role = stored.get("role", payload.role or "customer") if stored else (payload.role or "customer")
    
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
