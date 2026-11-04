from pydantic import BaseModel
from typing import Optional, List

class StoreProductResponse(BaseModel):
    id: str
    store_id: str
    global_product_id: Optional[str]
    name_en: str
    name_hi: str
    category: str
    unit: str
    price: float
    mrp: Optional[float]
    image_url: str
    in_stock: bool
    stock_quantity: int

class StoreResponse(BaseModel):
    id: str
    owner_id: str
    shop_name: str
    owner_name: str
    category: str
    latitude: float
    longitude: float
    village: str
    landmark: Optional[str]
    block: str
    district: str
    is_online: bool
    is_approved: bool
    is_featured: bool
    rating: float
    banner_url: Optional[str]
    distance_km: Optional[float] = None

class GlobalCatalogResponse(BaseModel):
    id: str
    name_en: str
    name_hi: str
    category: str
    default_unit: str
    suggested_mrp: float
    image_url: str
    tags: Optional[str]

class AddProductToStoreRequest(BaseModel):
    global_product_id: Optional[str] = None
    custom_name_en: Optional[str] = None
    custom_name_hi: Optional[str] = None
    category: str
    unit: str
    price: float
    mrp: Optional[float] = None
    image_url: Optional[str] = None
    stock_quantity: int = 50
    in_stock: bool = True

class StoreRegistrationRequest(BaseModel):
    shop_name: str
    owner_name: str
    category: str
    latitude: float
    longitude: float
    village: str
    landmark: Optional[str] = None
    block: Optional[str] = "Rural Hub"
    district: Optional[str] = "District"
    banner_url: Optional[str] = None
    upi_id: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    aadhaar_front_url: Optional[str] = None
    aadhaar_back_url: Optional[str] = None
    selfie_url: Optional[str] = None
    fssai_license: Optional[str] = None
    gst_certificate: Optional[str] = None

class StoreStatusUpdate(BaseModel):
    is_online: bool

class ProductStockUpdate(BaseModel):
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    price: Optional[float] = None
    mrp: Optional[float] = None

