import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.base import Notification
from app.schemas.notification import NotificationResponse
from app.core.security import get_current_user_payload

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifs = res.scalars().all()
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            body=n.body,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at.isoformat() if n.created_at else "",
            metadata=json.loads(n.metadata_json) if n.metadata_json else None
        )
        for n in notifs
    ]

@router.post("/mark-all-read")
async def mark_all_read(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(
        select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)
    )
    unread = res.scalars().all()
    for n in unread:
        n.is_read = True
    await db.commit()
    return {"success": True, "marked_count": len(unread)}

@router.patch("/{notification_id}/read")
async def mark_single_read(
    notification_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    res = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notif = res.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    return {"success": True}
