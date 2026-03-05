"""
Websocket router — real-time live call events, dashboard stats, and agent test simulator streaming.
"""
from typing import Dict
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

router = APIRouter(tags=["WebSockets"])

# Simple connection manager for active websockets
class ConnectionManager:
    def __init__(self):
        # Maps call_id -> list of active websockets listening to that call
        self.active_call_connections: Dict[str, list[WebSocket]] = {}
        # Global dashboard listeners
        self.dashboard_connections: list[WebSocket] = []

    async def connect_call(self, websocket: WebSocket, call_id: str):
        await websocket.accept()
        if call_id not in self.active_call_connections:
            self.active_call_connections[call_id] = []
        self.active_call_connections[call_id].append(websocket)

    def disconnect_call(self, websocket: WebSocket, call_id: str):
        if call_id in self.active_call_connections:
            if websocket in self.active_call_connections[call_id]:
                self.active_call_connections[call_id].remove(websocket)
            if not self.active_call_connections[call_id]:
                del self.active_call_connections[call_id]

    async def broadcast_call_event(self, call_id: str, event_data: dict):
        if call_id in self.active_call_connections:
            for connection in self.active_call_connections[call_id]:
                try:
                    await connection.send_json(event_data)
                except Exception:
                    self.disconnect_call(connection, call_id)

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.dashboard_connections.append(websocket)

    def disconnect_dashboard(self, websocket: WebSocket):
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)

    async def broadcast_dashboard(self, event_data: dict):
        for connection in self.dashboard_connections:
            try:
                await connection.send_json(event_data)
            except Exception:
                self.disconnect_dashboard(connection)


ws_manager = ConnectionManager()


@router.websocket("/ws/calls/{call_id}")
async def call_websocket(websocket: WebSocket, call_id: str):
    """
    Subscribes frontend to live events for a specific call.
    Receives: {"type": "transcript_partial", "text": "...", "speaker": "ai"}
    """
    await ws_manager.connect_call(websocket, call_id)
    try:
        while True:
            # We don't expect much input from client, but keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_call(websocket, call_id)


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """
    Global dashboard live feed (e.g. "Call answered", "Agent online").
    """
    await ws_manager.connect_dashboard(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect_dashboard(websocket)


async def emit_call_event(call_id: str, event_type: str, payload: dict):
    """Helper for other services to emit events."""
    await ws_manager.broadcast_call_event(call_id, {
        "type": event_type,
        "payload": payload
    })
