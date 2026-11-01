from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import Store, Runner, Order, User, GlobalCatalogItem
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Super Admin Operations"])

@router.get("/overview")
async def get_admin_overview(db: AsyncSession = Depends(get_db)):
    stores_res = await db.execute(select(Store))
    stores = stores_res.scalars().all()
    
    runners_res = await db.execute(select(Runner))
    runners = runners_res.scalars().all()
    
    orders_res = await db.execute(select(Order))
    orders = orders_res.scalars().all()
    
    total_gmv = sum(o.total_amount for o in orders if o.status == "DELIVERED")
    active_orders = [o for o in orders if o.status not in ["DELIVERED", "CANCELLED"]]
    pending_vendors = [s for s in stores if not s.is_approved]
    pending_runners = [r for r in runners if not r.is_approved]
    
    return {
        "pilot_area": f"{settings.PILOT_BLOCK}, {settings.PILOT_DISTRICT}, {settings.PILOT_STATE}",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "total_stores": len(stores),
        "active_stores": len([s for s in stores if s.is_online and s.is_approved]),
        "total_runners": len(runners),
        "online_runners": len([r for r in runners if r.is_online and r.is_approved]),
        "total_orders": len(orders),
        "active_orders_count": len(active_orders),
        "total_gmv": round(total_gmv, 2),
        "pending_vendor_approvals": len(pending_vendors),
        "pending_runner_approvals": len(pending_runners)
    }

@router.get("/vendors/pending")
async def get_pending_vendors(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Store).where(Store.is_approved == False))
    return res.scalars().all()

@router.post("/vendors/{store_id}/approve")
async def approve_vendor(store_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Store).where(Store.id == store_id))
    st = res.scalars().first()
    if not st:
        raise HTTPException(status_code=404, detail="Store not found")
    st.is_approved = True
    await db.commit()
    return {"message": f"Store {st.shop_name} approved successfully"}

@router.get("/runners/pending")
async def get_pending_runners(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Runner).where(Runner.is_approved == False))
    return res.scalars().all()

@router.post("/runners/{runner_id}/approve")
async def approve_runner(runner_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Runner).where(Runner.id == runner_id))
    rn = res.scalars().first()
    if not rn:
        raise HTTPException(status_code=404, detail="Runner not found")
    rn.is_approved = True
    await db.commit()
    return {"message": f"Runner {rn.full_name} approved successfully"}
