from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MonthlyRationItemCreate(BaseModel):
    product_id: Optional[str] = None
    product_name_en: str
    product_name_hi: Optional[str] = None
    unit: str = "1 kg"
    quantity: int = 1
    notes: Optional[str] = None

class MonthlyRationItemResponse(BaseModel):
    id: str
    list_id: str
    product_id: Optional[str] = None
    product_name_en: str
    product_name_hi: Optional[str] = None
    unit: str
    quantity: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class MonthlyRationListCreate(BaseModel):
    name: str = "My Monthly Ration"
    items: Optional[List[MonthlyRationItemCreate]] = []

class MonthlyRationListUpdate(BaseModel):
    name: Optional[str] = None
    items: Optional[List[MonthlyRationItemCreate]] = None

class MonthlyRationListResponse(BaseModel):
    id: str
    user_id: str
    name: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[MonthlyRationItemResponse] = []

class RationValidateCartItem(BaseModel):
    product_id: Optional[str] = None
    product_name_en: str
    product_name_hi: Optional[str] = None
    unit: str
    quantity: int
    available: bool = True
    current_price: float = 0.0
    stock_status: str = "IN_STOCK"
    price_changed: bool = False

class RationValidateCartResponse(BaseModel):
    list_id: str
    list_name: str
    store_id: Optional[str] = None
    store_name: Optional[str] = None
    total_estimated_amount: float
    items: List[RationValidateCartItem]
    all_available: bool
