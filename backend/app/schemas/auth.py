import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any

class SendOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=10, description="10-digit Indian mobile number", pattern=r"^[6-9]\d{9}$")
    role: str = Field("customer", max_length=16, pattern=r"^(customer|vendor|runner)$", description="customer, vendor, runner")

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> str:
        if isinstance(v, str):
            if len(v) > 32:
                raise ValueError("Phone input exceeds maximum length")
            digits = re.sub(r"\D", "", v.strip())
            if len(digits) == 12 and digits.startswith("91"):
                return digits[2:]
            if len(digits) == 11 and digits.startswith("0"):
                return digits[1:]
            return digits
        return str(v)

class SendOTPResponse(BaseModel):
    status: Optional[str] = "sent"
    message: str
    session_id: str
    expires_in: int = 300
    delivery_status: Optional[str] = "dispatched"
    delivery_channel: Optional[str] = "sms"
    mock_otp: Optional[str] = None # For dev/testing environments

class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=10, pattern=r"^[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    session_id: Optional[str] = Field(default=None, max_length=128)
    role: Optional[str] = Field(default="customer", max_length=16, pattern=r"^(customer|vendor|runner)$")
    name: Optional[str] = Field(default=None, max_length=120)

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, v: Any) -> str:
        if isinstance(v, str):
            if len(v) > 32:
                raise ValueError("Phone input exceeds maximum length")
            digits = re.sub(r"\D", "", v.strip())
            if len(digits) == 12 and digits.startswith("91"):
                return digits[2:]
            if len(digits) == 11 and digits.startswith("0"):
                return digits[1:]
            return digits
        return str(v)

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
    name: Optional[str] = Field(default=None, max_length=120)
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
