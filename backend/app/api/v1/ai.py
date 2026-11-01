from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import StoreProduct
from app.schemas.ai import AIQueryRequest, AIQueryResponse, MatchedProductInfo
from app.services.ai_service import parse_ai_shopping_query

router = APIRouter(prefix="/ai", tags=["AI Voice Assistant"])

@router.post("/query", response_model=AIQueryResponse)
async def process_ai_query(data: AIQueryRequest, db: AsyncSession = Depends(get_db)):
    store_products = None
    if data.store_id:
        res = await db.execute(
            select(StoreProduct).where(StoreProduct.store_id == data.store_id, StoreProduct.in_stock == True)
        )
        prods = res.scalars().all()
        store_products = [
            {
                "id": p.id,
                "name_en": p.custom_name_en or (p.global_item.name_en if p.global_item else "Product"),
                "name_hi": p.custom_name_hi or (p.global_item.name_hi if p.global_item else "उत्पाद"),
                "unit": p.unit,
                "price": p.price,
                "image_url": p.image_url,
                "keywords": [
                    (p.custom_name_en or "").lower(),
                    (p.custom_name_hi or "").lower(),
                ]
            }
            for p in prods
        ]
        
    result = parse_ai_shopping_query(data.query, store_products)
    
    matched = None
    if result.get("matched_product"):
        m = result["matched_product"]
        matched = MatchedProductInfo(
            id=m["id"],
            name_en=m["name_en"],
            name_hi=m["name_hi"],
            unit=m["unit"],
            price=m["price"],
            image_url=m["image_url"]
        )
        
    return AIQueryResponse(
        intent=result["intent"],
        query=result["query"],
        quantity=result["quantity"],
        matched_product=matched,
        reply_hi=result["reply_hi"],
        reply_en=result["reply_en"],
        confidence=result["confidence"]
    )
