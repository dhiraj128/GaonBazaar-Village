from pydantic import BaseModel
from typing import Optional, List

class AIQueryRequest(BaseModel):
    query: str
    store_id: Optional[str] = None
    language_code: Optional[str] = "auto" # hi, en, hinglish

class MatchedProductInfo(BaseModel):
    id: str
    name_en: str
    name_hi: str
    unit: str
    price: float
    image_url: str

class AIQueryResponse(BaseModel):
    intent: str # ADD_TO_CART, SEARCH, SHOW_CART, REMOVE_FROM_CART, CLARIFICATION, UNKNOWN
    query: str
    quantity: int = 1
    matched_product: Optional[MatchedProductInfo] = None
    reply_hi: str
    reply_en: str
    confidence: float
