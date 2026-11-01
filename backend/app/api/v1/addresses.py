from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import Address, Store
from app.schemas.address import (
    AddressCreate, AddressResponse, ServiceabilityCheckRequest, ServiceabilityCheckResponse
)
from app.core.security import get_current_user_payload
from app.services.geo_service import is_within_service_radius, get_nearest_pilot_locality
from app.core.config import settings

router = APIRouter(prefix="/addresses", tags=["Addresses & Geolocation"])

@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    result = await db.execute(select(Address).where(Address.user_id == user_id))
    addresses = result.scalars().all()
    return [
        AddressResponse(
            id=a.id,
            user_id=a.user_id,
            title=a.title,
            recipient_name=a.recipient_name,
            phone=a.phone,
            latitude=a.latitude,
            longitude=a.longitude,
            village=a.village,
            landmark=a.landmark,
            block=a.block,
            district=a.district,
            state=a.state,
            is_default=a.is_default
        )
        for a in addresses
    ]

@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    data: AddressCreate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    
    # If default, unset previous defaults
    if data.is_default:
        result = await db.execute(select(Address).where(Address.user_id == user_id))
        for existing in result.scalars().all():
            existing.is_default = False
            
    address = Address(
        user_id=user_id,
        title=data.title,
        recipient_name=data.recipient_name,
        phone=data.phone,
        latitude=data.latitude,
        longitude=data.longitude,
        village=data.village,
        landmark=data.landmark,
        block=data.block,
        district=data.district,
        state=data.state,
        is_default=data.is_default
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)
    
    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        title=address.title,
        recipient_name=address.recipient_name,
        phone=address.phone,
        latitude=address.latitude,
        longitude=address.longitude,
        village=address.village,
        landmark=address.landmark,
        block=address.block,
        district=address.district,
        state=address.state,
        is_default=address.is_default
    )

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    result = await db.execute(
        select(Address).where(Address.id == address_id, Address.user_id == user_id)
    )
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    await db.delete(address)
    await db.commit()
    return None

@router.post("/serviceability/check", response_model=ServiceabilityCheckResponse)
async def check_serviceability(
    data: ServiceabilityCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    # Find reference store lat/lng
    store_lat = settings.DEFAULT_CENTER_LAT
    store_lng = settings.DEFAULT_CENTER_LNG
    
    if data.store_id:
        res = await db.execute(select(Store).where(Store.id == data.store_id))
        st = res.scalars().first()
        if st:
            store_lat = st.latitude
            store_lng = st.longitude
            
    is_serv, dist_km = is_within_service_radius(store_lat, store_lng, data.latitude, data.longitude)
    closest_loc, _ = get_nearest_pilot_locality(data.latitude, data.longitude)
    
    est_mins = int(25 + (dist_km * 4)) # ~30-60 mins delivery target
    
    if is_serv:
        msg = f"डिलीवरी उपलब्ध है ({dist_km} किमी दूरी, ~{est_mins} मिनट)"
    else:
        msg = f"क्षमा करें, यह स्थान 8 किमी डिलीवरी सीमा से बाहर है ({dist_km} किमी)"
        
    return ServiceabilityCheckResponse(
        is_serviceable=is_serv,
        distance_km=dist_km,
        max_allowed_km=settings.MAX_DELIVERY_RADIUS_KM,
        estimated_delivery_minutes=est_mins,
        village_hint=closest_loc["name"] if closest_loc else None,
        message=msg
    )
