from pydantic import BaseModel, Field
from typing import Optional

class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="10-digit Indian mobile number", pattern=r"^[6-9]\d{9}$")
    role: str = Field("customer", description="customer, vendor, runner, admin")

class SendOTPResponse(BaseModel):
    message: str
    session_id: str
    expires_in: int = 300
    delivery_status: Optional[str] = "delivered"
    delivery_channel: Optional[str] = "sms"
    mock_otp: Optional[str] = None # For dev/testing environments

class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., min_length=4, max_length=6)
    session_id: Optional[str] = None
    role: Optional[str] = "customer"
    name: Optional[str] = None

class UserInfo(BaseModel):
    id: str
    phone: str
    name: Optional[str]
    email: Optional[str] = None
    role: str
    preferred_language: str
    avatar_url: Optional[str] = None
    primary_village: Optional[str] = None
    primary_panchayat: Optional[str] = None
    is_active: bool

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Optional[str] = None
    avatar_url: Optional[str] = None
    primary_village: Optional[str] = None
    primary_panchayat: Optional[str] = None

class UploadAvatarRequest(BaseModel):
    avatar_data: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
