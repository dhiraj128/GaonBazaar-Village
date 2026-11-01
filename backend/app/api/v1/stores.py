from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.base import Store, StoreProduct, GlobalCatalogItem, User
from app.schemas.store import (
    StoreResponse, StoreProductResponse, GlobalCatalogResponse, AddProductToStoreRequest, StoreRegistrationRequest,
    StoreStatusUpdate, ProductStockUpdate
)
from app.services.geo_service import calculate_haversine_distance, is_within_service_radius
from app.core.security import get_current_user_payload

router = APIRouter(tags=["Stores & Products"])

@router.post("/stores/onboard", response_model=StoreResponse)
async def onboard_store(
    req: StoreRegistrationRequest,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    owner_id = payload.get("sub")
    
    # Check if store already exists for user
    res = await db.execute(select(Store).where(Store.owner_id == owner_id))
    existing = res.scalars().first()
    if existing:
        existing.shop_name = req.shop_name
        existing.owner_name = req.owner_name
        existing.category = req.category
        existing.latitude = req.latitude
        existing.longitude = req.longitude
        existing.village = req.village
        existing.landmark = req.landmark
        existing.block = req.block
        existing.district = req.district
        if req.banner_url:
            existing.banner_url = req.banner_url
        if req.upi_id:
            existing.upi_id = req.upi_id
        await db.commit()
        await db.refresh(existing)
        return StoreResponse(
            id=existing.id,
            owner_id=existing.owner_id,
            shop_name=existing.shop_name,
            owner_name=existing.owner_name,
            category=existing.category,
            latitude=existing.latitude,
            longitude=existing.longitude,
            village=existing.village,
            landmark=existing.landmark,
            block=existing.block,
            district=existing.district,
            is_online=existing.is_online,
            is_approved=existing.is_approved,
            is_featured=existing.is_featured,
            rating=existing.rating,
            banner_url=existing.banner_url
        )
        
    new_store = Store(
        owner_id=owner_id,
        shop_name=req.shop_name,
        owner_name=req.owner_name,
        category=req.category,
        latitude=req.latitude,
        longitude=req.longitude,
        village=req.village,
        landmark=req.landmark,
        block=req.block,
        district=req.district,
        is_online=True,
        is_approved=False, # Requires Admin approval
        is_featured=False,
        rating=5.0,
        banner_url=req.banner_url or "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500",
        commission_rate=0.0,
        upi_id=req.upi_id
    )
    db.add(new_store)
    await db.commit()
    await db.refresh(new_store)
    
    return StoreResponse(
        id=new_store.id,
        owner_id=new_store.owner_id,
        shop_name=new_store.shop_name,
        owner_name=new_store.owner_name,
        category=new_store.category,
        latitude=new_store.latitude,
        longitude=new_store.longitude,
        village=new_store.village,
        landmark=new_store.landmark,
        block=new_store.block,
        district=new_store.district,
        is_online=new_store.is_online,
        is_approved=new_store.is_approved,
        is_featured=new_store.is_featured,
        rating=new_store.rating,
        banner_url=new_store.banner_url
    )


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

@router.get("/stores/me", response_model=StoreResponse)
async def get_my_store(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    owner_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == owner_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found for this vendor")
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

@router.patch("/stores/status")
async def update_store_status(
    data: StoreStatusUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    owner_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == owner_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
    if not st.is_approved and data.is_online:
        raise HTTPException(status_code=400, detail="Store must be approved by admin before going online")
    st.is_online = data.is_online
    await db.commit()
    return {"message": f"Store is now {'online' if st.is_online else 'offline'}", "is_online": st.is_online}

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

@router.patch("/stores/products/{product_id}/stock")
async def update_product_stock(
    product_id: str,
    data: ProductStockUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    owner_id = payload.get("sub")
    res = await db.execute(select(Store).where(Store.owner_id == owner_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
    pres = await db.execute(select(StoreProduct).where(StoreProduct.id == product_id, StoreProduct.store_id == st.id))
    p = pres.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found in this store")
    if data.in_stock is not None:
        p.in_stock = data.in_stock
    if data.stock_quantity is not None:
        p.stock_quantity = data.stock_quantity
    if data.price is not None:
        p.price = data.price
    await db.commit()
    return {
        "message": "Product updated successfully",
        "product_id": p.id,
        "in_stock": p.in_stock,
        "stock_quantity": p.stock_quantity,
        "price": p.price
    }
