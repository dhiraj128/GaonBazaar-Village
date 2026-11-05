from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime

class MonthlyRationItemCreate(BaseModel):
    product_id: Optional[str] = None
    global_product_id: Optional[str] = None
    product_name_en: Optional[str] = None
    product_name: Optional[str] = None
    product_name_hi: Optional[str] = None
    unit: str = "1 kg"
    quantity: int = 1
    unit_price: Optional[float] = None
    notes: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def reconcile_names(cls, data):
        if isinstance(data, dict):
            if not data.get("product_name_en") and data.get("product_name"):
                data["product_name_en"] = data["product_name"]
            if not data.get("product_id") and data.get("global_product_id"):
                data["product_id"] = data["global_product_id"]
        return data

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
    name: Optional[str] = "My Monthly Ration"
    title: Optional[str] = None
    items: Optional[List[MonthlyRationItemCreate]] = []

    @model_validator(mode='before')
    @classmethod
    def reconcile_title(cls, data):
        if isinstance(data, dict):
            if not data.get("name") and data.get("title"):
                data["name"] = data["title"]
        return data

class MonthlyRationListUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    items: Optional[List[MonthlyRationItemCreate]] = None

    @model_validator(mode='before')
    @classmethod
    def reconcile_title(cls, data):
        if isinstance(data, dict):
            if not data.get("name") and data.get("title"):
                data["name"] = data["title"]
        return data

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
    global_product_id: Optional[str] = None
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
    serviceable_items: Optional[List[RationValidateCartItem]] = []
    unserviceable_items: Optional[List[RationValidateCartItem]] = []
    estimated_subtotal: Optional[float] = 0.0
    all_available: bool = True

    @model_validator(mode='before')
    @classmethod
    def reconcile_response(cls, data):
        if isinstance(data, dict):
            items = data.get("items", [])
            if not data.get("serviceable_items"):
                data["serviceable_items"] = [it for it in items if (isinstance(it, dict) and it.get("available", True)) or getattr(it, "available", True)]
            if not data.get("unserviceable_items"):
                data["unserviceable_items"] = [it for it in items if (isinstance(it, dict) and not it.get("available", True)) or not getattr(it, "available", True)]
            if "estimated_subtotal" not in data or data.get("estimated_subtotal") == 0.0:
                data["estimated_subtotal"] = data.get("total_estimated_amount", 0.0)
        return data
