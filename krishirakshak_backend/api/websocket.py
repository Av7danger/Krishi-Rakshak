from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.farmer_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, farmer_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.farmer_connections.setdefault(farmer_id, set()).add(websocket)

    def disconnect(self, farmer_id: int, websocket: WebSocket) -> None:
        conns = self.farmer_connections.get(farmer_id)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                self.farmer_connections.pop(farmer_id, None)

    async def send_json_to_farmer(self, farmer_id: int, message: dict) -> None:
        for ws in list(self.farmer_connections.get(farmer_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(farmer_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/")
async def ws_endpoint(ws: WebSocket, farmer_id: int = Query(...)):
    await manager.connect(farmer_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(farmer_id, ws)
