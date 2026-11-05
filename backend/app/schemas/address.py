from pydantic import BaseModel, Field
from typing import Optional

class AddressCreate(BaseModel):
    title: str = "Home"
    recipient_name: str
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    latitude: float
    longitude: float
    village: str
    landmark: Optional[str] = None
    block: str = "Minapur"
    district: str = "Muzaffarpur"
    state: str = "Bihar"
    is_default: bool = False

class AddressUpdate(BaseModel):
    title: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r"^[6-9]\d{9}$")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    village: Optional[str] = None
    landmark: Optional[str] = None
    block: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    is_default: Optional[bool] = None

class AddressResponse(BaseModel):
    id: str
    user_id: str
    title: str
    recipient_name: str
    phone: str
    latitude: float
    longitude: float
    village: str
    landmark: Optional[str]
    block: str
    district: str
    state: str
    is_default: bool

class ServiceabilityCheckRequest(BaseModel):
    latitude: float
    longitude: float
    store_id: Optional[str] = None

class ServiceabilityCheckResponse(BaseModel):
    is_serviceable: bool
    distance_km: float
    max_allowed_km: float
    estimated_delivery_minutes: int
    village_hint: Optional[str] = None
    message: str
