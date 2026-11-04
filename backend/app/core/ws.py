import json
import logging
from typing import Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.core.security import decode_access_token

logger = logging.getLogger("gaonbazaar.ws")

class ConnectionManager:
    def __init__(self):
        # Map role -> set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "all": set(),
            "vendor": set(),
            "runner": set(),
            "customer": set(),
            "admin": set(),
        }
        # Map websocket -> metadata dict
        self.connection_meta: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, role: str = "all", token: Optional[str] = None):
        await websocket.accept()
        user_id = None
        user_role = role

        if token:
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                user_role = payload.get("role", role)

        if user_role not in self.active_connections:
            self.active_connections[user_role] = set()

        self.active_connections["all"].add(websocket)
        self.active_connections[user_role].add(websocket)
        self.connection_meta[websocket] = {
            "role": user_role,
            "user_id": user_id,
        }
        logger.info("WS connected: role=%s, user=%s (total active: %d)", user_role, user_id, len(self.active_connections["all"]))

    def disconnect(self, websocket: WebSocket):
        meta = self.connection_meta.pop(websocket, {})
        role = meta.get("role", "all")
        self.active_connections["all"].discard(websocket)
        if role in self.active_connections:
            self.active_connections[role].discard(websocket)
        logger.info("WS disconnected: role=%s (remaining: %d)", role, len(self.active_connections["all"]))

    async def broadcast(self, message: dict, role: Optional[str] = None):
        """
        Broadcast JSON message to all clients or a specific role group.
        Non-blocking, resilient to individual client disconnection.
        """
        targets = self.active_connections.get(role, self.active_connections["all"]) if role else self.active_connections["all"]
        dead_sockets = []

        payload = json.dumps(message)
        for ws in list(targets):
            try:
                await ws.send_text(payload)
            except Exception as exc:
                logger.debug("WS send failed, removing socket: %s", exc)
                dead_sockets.append(ws)

        for ws in dead_sockets:
            self.disconnect(ws)

    async def emit_new_order(self, order_data: dict):
        """Emits new order notification to Vendors and Admins"""
        msg = {
            "event": "new_order",
            "type": "ORDER_CREATED",
            "data": order_data
        }
        await self.broadcast(msg, role="vendor")
        await self.broadcast(msg, role="admin")

    async def emit_order_update(self, order_id: str, new_status: str, extra: Optional[dict] = None):
        """Emits order lifecycle state change across all roles"""
        msg = {
            "event": "order_updated",
            "type": "ORDER_STATUS_CHANGED",
            "order_id": order_id,
            "status": new_status,
            "data": extra or {}
        }
        await self.broadcast(msg)

    async def emit_mission_assigned(self, mission_data: dict):
        """Emits mission assignment event to Runners"""
        msg = {
            "event": "mission_assigned",
            "type": "MISSION_ASSIGNED",
            "data": mission_data
        }
        await self.broadcast(msg, role="runner")
        await self.broadcast(msg, role="admin")

ws_manager = ConnectionManager()
