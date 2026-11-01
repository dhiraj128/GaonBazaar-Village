from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.base import Store, StoreProduct, GlobalCatalogItem, User
from app.schemas.store import (
    StoreResponse, StoreProductResponse, GlobalCatalogResponse, AddProductToStoreRequest
)
from app.services.geo_service import calculate_haversine_distance, is_within_service_radius
from app.core.security import get_current_user_payload

router = APIRouter(tags=["Stores & Products"])

@router.get("/stores/nearby", response_model=List[StoreResponse])
async def get_nearby_stores(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(8.0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Store).where(Store.is_approved == True))
    all_stores = result.scalars().all()
    
    nearby = []
    for store in all_stores:
        is_serv, dist = is_within_service_radius(store.latitude, store.longitude, latitude, longitude)
        if is_serv and dist <= radius_km:
            nearby.append((store, dist))
            
    # Sort by distance
    nearby.sort(key=lambda x: x[1])
    
    # Return formatted list (ensuring top stores have featured flags appropriately set)
    stores_out = []
    for idx, (st, dist) in enumerate(nearby):
        stores_out.append(StoreResponse(
            id=st.id,
            owner_id=st.owner_id,
            shop_name=st.shop_name,
            owner_name=st.owner_name,
            category=st.category,
            latitude=st.latitude,
            longitude=st.longitude,
            village=st.village,
            landmark=st.landmark,
            block=st.block,
            district=st.district,
            is_online=st.is_online,
            is_approved=st.is_approved,
            is_featured=(idx < 2), # Exactly two featured nearby stores
            rating=st.rating,
            banner_url=st.banner_url,
            distance_km=dist
        ))
    return stores_out

@router.get("/stores/{store_id}", response_model=StoreResponse)
async def get_store_details(store_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.id == store_id))
    st = result.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
        
    return StoreResponse(
        id=st.id,
        owner_id=st.owner_id,
        shop_name=st.shop_name,
        owner_name=st.owner_name,
        category=st.category,
        latitude=st.latitude,
        longitude=st.longitude,
        village=st.village,
        landmark=st.landmark,
        block=st.block,
        district=st.district,
        is_online=st.is_online,
        is_approved=st.is_approved,
        is_featured=st.is_featured,
        rating=st.rating,
        banner_url=st.banner_url
    )

@router.get("/stores/{store_id}/products", response_model=List[StoreProductResponse])
async def get_store_products(
    store_id: str,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(StoreProduct).options(selectinload(StoreProduct.global_item)).where(StoreProduct.store_id == store_id, StoreProduct.in_stock == True)
    if category:
        query = query.where(StoreProduct.category == category)
        
    result = await db.execute(query)
    products = result.scalars().all()
    
    output = []
    for p in products:
        name_en = p.custom_name_en or (p.global_item.name_en if p.global_item else "Product")
        name_hi = p.custom_name_hi or (p.global_item.name_hi if p.global_item else "उत्पाद")
        output.append(StoreProductResponse(
            id=p.id,
            store_id=p.store_id,
            global_product_id=p.global_product_id,
            name_en=name_en,
            name_hi=name_hi,
            category=p.category,
            unit=p.unit,
            price=p.price,
            mrp=p.mrp,
            image_url=p.image_url,
            in_stock=p.in_stock,
            stock_quantity=p.stock_quantity
        ))
    return output

@router.get("/catalog/global", response_model=List[GlobalCatalogResponse])
async def get_global_catalog(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GlobalCatalogItem))
    items = result.scalars().all()
    return [
        GlobalCatalogResponse(
            id=i.id,
            name_en=i.name_en,
            name_hi=i.name_hi,
            category=i.category,
            default_unit=i.default_unit,
            suggested_mrp=i.suggested_mrp,
            image_url=i.image_url,
            tags=i.tags
        )
        for i in items
    ]

@router.post("/vendor/products", response_model=StoreProductResponse)
async def add_vendor_product(
    data: AddProductToStoreRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == user_id))
    store = res.scalars().first()
    if not store:
        raise HTTPException(status_code=403, detail="Only verified vendors can add products")
        
    image_url = data.image_url
    name_en = data.custom_name_en
    name_hi = data.custom_name_hi
    
    if data.global_product_id:
        gres = await db.execute(select(GlobalCatalogItem).where(GlobalCatalogItem.id == data.global_product_id))
        gitem = gres.scalars().first()
        if gitem:
            if not image_url:
                image_url = gitem.image_url
            if not name_en:
                name_en = gitem.name_en
            if not name_hi:
                name_hi = gitem.name_hi
                
    product = StoreProduct(
        store_id=store.id,
        global_product_id=data.global_product_id,
        custom_name_en=name_en,
        custom_name_hi=name_hi,
        category=data.category,
        unit=data.unit,
        price=data.price,
        mrp=data.mrp,
        image_url=image_url or "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400",
        stock_quantity=data.stock_quantity,
        in_stock=data.in_stock
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return StoreProductResponse(
        id=product.id,
        store_id=product.store_id,
        global_product_id=product.global_product_id,
        name_en=name_en or "Product",
        name_hi=name_hi or "उत्पाद",
        category=product.category,
        unit=product.unit,
        price=product.price,
        mrp=product.mrp,
        image_url=product.image_url,
        in_stock=product.in_stock,
        stock_quantity=product.stock_quantity
    )
