from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.db.session import get_db
from app.models.base import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

REVOKED_TOKENS: set = set()
REVOKED_USER_IDS: set = set()

def revoke_token(token: str) -> None:
    REVOKED_TOKENS.add(token)

def is_token_revoked(token: str) -> bool:
    return token in REVOKED_TOKENS

def revoke_user_sessions(user_id: str) -> None:
    REVOKED_USER_IDS.add(user_id)

def reinstate_user_sessions(user_id: str) -> None:
    REVOKED_USER_IDS.discard(user_id)

def is_user_suspended(user_id: str) -> bool:
    return user_id in REVOKED_USER_IDS

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user_payload(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    if is_token_revoked(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="सत्र समाप्त हो गया है। कृपया पुनः लॉगिन करें (Token has been revoked. Please log in again)"
        )
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    user_id = payload.get("sub")
    if user_id and is_user_suspended(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="खाता निलंबित है (Account has been suspended by administration)"
        )
    return payload

async def get_current_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    api_key: Optional[str] = Depends(admin_key_header),
    db: AsyncSession = Depends(get_db)
) -> dict:
    # 1. API Key check
    if api_key and api_key == settings.ADMIN_API_KEY:
        return {"sub": "admin_key_user", "role": "super_admin", "phone": "9800000099", "is_active": True}
    
    # 2. JWT Bearer Token check with authoritative database validation
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and payload.get("role") in ["admin", "super_admin", "hub_manager"]:
            user_id = payload.get("sub")
            phone = payload.get("phone")
            res = await db.execute(select(User).where((User.id == user_id) | (User.phone == phone)))
            user = res.scalars().first()
            if user:
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="प्रशासनिक खाता निलंबित है (Admin account has been suspended)"
                    )
                if user.role not in ["admin", "super_admin", "hub_manager"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="अपर्याप्त अनुमति (Insufficient privileges: User role revoked)"
                    )
                return {
                    "sub": user.id,
                    "phone": user.phone,
                    "role": user.role,
                    "name": user.name or payload.get("name", "Admin"),
                    "is_active": user.is_active
                }
            return payload

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="प्रशासनिक अनुमति आवश्यक है (Administrative privileges required)"
    )

async def require_super_admin(admin_payload: dict = Depends(get_current_admin)) -> dict:
    role = admin_payload.get("role")
    if role in ["admin", "super_admin"]:
        return admin_payload
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Role-Based Access Control: 'Hub Manager' is restricted from accessing Financials/Batch Payouts, Master Catalog Pricing Settings, and System Audit Logs. Super Admin privilege required."
    )

require_hub_manager_or_super_admin = get_current_admin
