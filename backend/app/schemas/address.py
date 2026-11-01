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
