from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderItemInput(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)

class CartSyncRequest(BaseModel):
    store_id: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    items: List[OrderItemInput]

class CartPriceBreakdown(BaseModel):
    subtotal: float
    delivery_fee: float
    platform_fee: float # ₹3.00
    total_amount: float
    is_serviceable: bool
    distance_km: Optional[float]
    warning: Optional[str] = None

class CreateOrderRequest(BaseModel):
    store_id: str
    delivery_address_id: str
    payment_method: str = "COD" # COD or ONLINE
    items: List[OrderItemInput]
    customer_notes: Optional[str] = None

class OrderItemDetail(BaseModel):
    id: str
    product_id: str
    name_en: str
    name_hi: str
    unit: str
    unit_price: float
    quantity: int
    total_price: float
    image_url: Optional[str]

class OrderTimelineDetail(BaseModel):
    status: str
    title: str
    description: Optional[str]
    timestamp: datetime

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    store_id: str
    store_name: str
    runner_id: Optional[str]
    runner_name: Optional[str]
    runner_phone: Optional[str]
    delivery_address: str
    status: str
    subtotal: float
    delivery_fee: float
    platform_fee: float
    total_amount: float
    payment_method: str
    payment_status: str
    delivery_otp: str
    placed_at: datetime
    cancel_until: datetime
    can_cancel: bool
    cancel_seconds_remaining: int
    items: List[OrderItemDetail]
    timeline: List[OrderTimelineDetail]

class OrderActionRequest(BaseModel):
    action: str # ACCEPT, REJECT, PACKED, PICKUP, DELIVER
    delivery_otp: Optional[str] = None
    cash_collected: Optional[bool] = None
    reason: Optional[str] = None
