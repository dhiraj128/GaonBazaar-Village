from pydantic import BaseModel
from typing import Optional, Dict, Any

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    type: str
    is_read: bool
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

class MarkNotificationReadRequest(BaseModel):
    notification_id: str
