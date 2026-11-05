from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.base import MonthlyRationList, MonthlyRationItem, GlobalCatalogItem, Store, StoreProduct
from app.schemas.ration_list import (
    MonthlyRationListCreate,
    MonthlyRationListUpdate,
    MonthlyRationListResponse,
    MonthlyRationItemCreate,
    MonthlyRationItemResponse,
    RationValidateCartResponse,
    RationValidateCartItem
)
from app.core.security import get_current_user_payload

router = APIRouter(prefix="/ration-lists", tags=["Monthly Ration Lists"])

DEFAULT_RATION_ITEMS = [
    {"product_id": "cat_atta", "name_en": "Chakki Fresh Atta", "name_hi": "चक्की फ्रेश आटा", "unit": "5 kg", "quantity": 1, "notes": "Monthly staple flour"},
    {"product_id": "cat_rice", "name_en": "Sonam Rice", "name_hi": "सोनम चावल", "unit": "5 kg", "quantity": 1, "notes": "Clean polished rice"},
    {"product_id": "cat_toor_dal", "name_en": "Desi Toor Dal", "name_hi": "देसी अरहर दाल", "unit": "2 kg", "quantity": 1, "notes": "Yellow split pulse"},
    {"product_id": "cat_mustard_oil", "name_en": "Kachhi Ghani Mustard Oil", "name_hi": "कच्ची घानी सरसों तेल", "unit": "1 L", "quantity": 2, "notes": "Pure edible cooking oil"},
    {"product_id": "cat_sugar", "name_en": "Refined Sugar", "name_hi": "सफेद चीनी", "unit": "2 kg", "quantity": 1, "notes": "Clean white cane sugar"},
    {"product_id": "cat_salt", "name_en": "Tata Iodized Salt", "name_hi": "टाटा आयोडाइज्ड नमक", "unit": "1 kg", "quantity": 1, "notes": "Daily iodized salt"}
]

@router.get("", response_model=List[MonthlyRationListResponse])
async def list_user_ration_lists(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all monthly ration lists for the authenticated customer.
    If none exist yet, automatically provisions the default village ration starter list.
    """
    user_id = payload.get("sub")
    query = (
        select(MonthlyRationList)
        .options(selectinload(MonthlyRationList.items))
        .where(MonthlyRationList.user_id == user_id, MonthlyRationList.is_active == True)
        .order_by(MonthlyRationList.created_at.desc())
    )
    result = await db.execute(query)
    lists = result.scalars().all()

    if not lists:
        # Auto-seed default ration list for first-time user
        now = datetime.now(timezone.utc)
        default_list = MonthlyRationList(
            user_id=user_id,
            name="My Monthly Ration",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        db.add(default_list)
        await db.flush()

        for itm in DEFAULT_RATION_ITEMS:
            r_item = MonthlyRationItem(
                list_id=default_list.id,
                product_id=itm["product_id"],
                product_name_en=itm["name_en"],
                product_name_hi=itm["name_hi"],
                unit=itm["unit"],
                quantity=itm["quantity"],
                notes=itm["notes"],
                created_at=now
            )
            db.add(r_item)

        await db.commit()
        # Re-query with loaded items
        result = await db.execute(query)
        lists = result.scalars().all()

    return [
        MonthlyRationListResponse(
            id=lst.id,
            user_id=lst.user_id,
            name=lst.name,
            is_active=lst.is_active,
            created_at=lst.created_at,
            updated_at=lst.updated_at,
            items=[
                MonthlyRationItemResponse(
                    id=it.id,
                    list_id=it.list_id,
                    product_id=it.product_id,
                    product_name_en=it.product_name_en,
                    product_name_hi=it.product_name_hi,
                    unit=it.unit,
                    quantity=it.quantity,
                    notes=it.notes,
                    created_at=it.created_at
                )
                for it in lst.items
            ]
        )
        for lst in lists
    ]

@router.post("", response_model=MonthlyRationListResponse, status_code=status.HTTP_201_CREATED)
async def create_ration_list(
    data: MonthlyRationListCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    now = datetime.now(timezone.utc)
    new_list = MonthlyRationList(
        user_id=user_id,
        name=data.name or "My Monthly Ration",
        is_active=True,
        created_at=now,
        updated_at=now
    )
    db.add(new_list)
    await db.flush()

    items_to_add = data.items if (data.items is not None and len(data.items) > 0) else [
        MonthlyRationItemCreate(**itm) for itm in DEFAULT_RATION_ITEMS
    ]

    for item in items_to_add:
        r_item = MonthlyRationItem(
            list_id=new_list.id,
            product_id=item.product_id,
            product_name_en=item.product_name_en,
            product_name_hi=item.product_name_hi,
            unit=item.unit,
            quantity=item.quantity,
            notes=item.notes,
            created_at=now
        )
        db.add(r_item)

    await db.commit()

    # Load with items
    query = (
        select(MonthlyRationList)
        .options(selectinload(MonthlyRationList.items))
        .where(MonthlyRationList.id == new_list.id)
    )
    res = await db.execute(query)
    loaded = res.scalars().first()

    return MonthlyRationListResponse(
        id=loaded.id,
        user_id=loaded.user_id,
        name=loaded.name,
        is_active=loaded.is_active,
        created_at=loaded.created_at,
        updated_at=loaded.updated_at,
        items=[
            MonthlyRationItemResponse(
                id=it.id,
                list_id=it.list_id,
                product_id=it.product_id,
                product_name_en=it.product_name_en,
                product_name_hi=it.product_name_hi,
                unit=it.unit,
                quantity=it.quantity,
                notes=it.notes,
                created_at=it.created_at
            )
            for it in loaded.items
        ]
    )

@router.get("/{list_id}", response_model=MonthlyRationListResponse)
async def get_ration_list(
    list_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    query = (
        select(MonthlyRationList)
        .options(selectinload(MonthlyRationList.items))
        .where(MonthlyRationList.id == list_id, MonthlyRationList.user_id == user_id)
    )
    res = await db.execute(query)
    lst = res.scalars().first()
    if not lst:
        raise HTTPException(status_code=404, detail="Monthly ration list not found")

    return MonthlyRationListResponse(
        id=lst.id,
        user_id=lst.user_id,
        name=lst.name,
        is_active=lst.is_active,
        created_at=lst.created_at,
        updated_at=lst.updated_at,
        items=[
            MonthlyRationItemResponse(
                id=it.id,
                list_id=it.list_id,
                product_id=it.product_id,
                product_name_en=it.product_name_en,
                product_name_hi=it.product_name_hi,
                unit=it.unit,
                quantity=it.quantity,
                notes=it.notes,
                created_at=it.created_at
            )
            for it in lst.items
        ]
    )

@router.put("/{list_id}", response_model=MonthlyRationListResponse)
async def update_ration_list(
    list_id: str,
    data: MonthlyRationListUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    query = (
        select(MonthlyRationList)
        .options(selectinload(MonthlyRationList.items))
        .where(MonthlyRationList.id == list_id, MonthlyRationList.user_id == user_id)
    )
    res = await db.execute(query)
    lst = res.scalars().first()
    if not lst:
        raise HTTPException(status_code=404, detail="Monthly ration list not found")

    now = datetime.now(timezone.utc)
    if data.name:
        lst.name = data.name
    lst.updated_at = now

    if data.items is not None:
        lst.items.clear()
        await db.flush()

        for item in data.items:
            r_item = MonthlyRationItem(
                list_id=lst.id,
                product_id=item.product_id,
                product_name_en=item.product_name_en,
                product_name_hi=item.product_name_hi,
                unit=item.unit,
                quantity=item.quantity,
                notes=item.notes,
                created_at=now
            )
            lst.items.append(r_item)

    await db.commit()

    # Reload
    res = await db.execute(query)
    loaded = res.scalars().first()

    return MonthlyRationListResponse(
        id=loaded.id,
        user_id=loaded.user_id,
        name=loaded.name,
        is_active=loaded.is_active,
        created_at=loaded.created_at,
        updated_at=loaded.updated_at,
        items=[
            MonthlyRationItemResponse(
                id=it.id,
                list_id=it.list_id,
                product_id=it.product_id,
                product_name_en=it.product_name_en,
                product_name_hi=it.product_name_hi,
                unit=it.unit,
                quantity=it.quantity,
                notes=it.notes,
                created_at=it.created_at
            )
            for it in loaded.items
        ]
    )

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ration_list(
    list_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    query = select(MonthlyRationList).where(MonthlyRationList.id == list_id, MonthlyRationList.user_id == user_id)
    res = await db.execute(query)
    lst = res.scalars().first()
    if not lst:
        raise HTTPException(status_code=404, detail="Monthly ration list not found")

    await db.delete(lst)
    await db.commit()
    return None

@router.post("/{list_id}/validate-cart", response_model=RationValidateCartResponse)
async def validate_ration_list_for_cart(
    list_id: str,
    store_id: Optional[str] = Query(None),
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates items in a monthly ration list against the selected or nearest store.
    Checks actual availability, current prices, stock flags, and provides total estimated cost.
    """
    user_id = payload.get("sub")
    query = (
        select(MonthlyRationList)
        .options(selectinload(MonthlyRationList.items))
        .where(MonthlyRationList.id == list_id, MonthlyRationList.user_id == user_id)
    )
    res = await db.execute(query)
    lst = res.scalars().first()
    if not lst:
        raise HTTPException(status_code=404, detail="Monthly ration list not found")

    # If store_id not provided, find the primary approved store
    target_store = None
    if store_id:
        st_res = await db.execute(select(Store).where(Store.id == store_id))
        target_store = st_res.scalars().first()

    if not target_store:
        st_res = await db.execute(select(Store).where(Store.is_approved == True))
        target_store = st_res.scalars().first()

    # Load global catalog as reference
    gc_res = await db.execute(select(GlobalCatalogItem))
    catalog_map = {item.id: item for item in gc_res.scalars().all()}

    # Load store products if store exists
    store_products = {}
    if target_store:
        sp_res = await db.execute(select(StoreProduct).where(StoreProduct.store_id == target_store.id))
        for sp in sp_res.scalars().all():
            if sp.global_product_id:
                store_products[sp.global_product_id] = sp
            p_name = sp.custom_name_en or (catalog_map[sp.global_product_id].name_en if sp.global_product_id in catalog_map else "")
            if p_name:
                store_products[p_name.lower()] = sp

    validated_items = []
    total_amount = 0.0
    all_available = True

    for item in lst.items:
        # Match by product_id or by name
        sp = None
        if item.product_id and item.product_id in store_products:
            sp = store_products[item.product_id]
        elif item.product_name_en.lower() in store_products:
            sp = store_products[item.product_name_en.lower()]

        cat_item = catalog_map.get(item.product_id)

        if sp:
            price = float(sp.price)
            is_in_stock = bool(sp.in_stock and (sp.stock_quantity is None or sp.stock_quantity >= item.quantity))
            status_str = "IN_STOCK" if is_in_stock else "OUT_OF_STOCK"
        elif cat_item:
            price = float(cat_item.suggested_mrp or 40.0)
            is_in_stock = True
            status_str = "IN_STOCK"
        else:
            price = 45.0
            is_in_stock = True
            status_str = "IN_STOCK"

        if not is_in_stock:
            all_available = False

        item_total = price * item.quantity
        total_amount += item_total

        validated_items.append(
            RationValidateCartItem(
                product_id=item.product_id or (sp.id if sp else None),
                product_name_en=item.product_name_en,
                product_name_hi=item.product_name_hi,
                unit=item.unit,
                quantity=item.quantity,
                available=is_in_stock,
                current_price=price,
                stock_status=status_str,
                price_changed=False
            )
        )

    return RationValidateCartResponse(
        list_id=lst.id,
        list_name=lst.name,
        store_id=target_store.id if target_store else None,
        store_name=target_store.shop_name if target_store else "GaonBazaar Central Kirana",
        total_estimated_amount=round(total_amount, 2),
        items=validated_items,
        all_available=all_available
    )
