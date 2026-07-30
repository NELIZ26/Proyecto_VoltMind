from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import manager

router = APIRouter(prefix="/api/ws", tags=["WebSockets Kiosko"])

@router.websocket("/ambiente/{ambiente_id}")
async def websocket_endpoint(websocket: WebSocket, ambiente_id: str):
    await manager.connect(websocket, ambiente_id)
    try:
        while True:
            # Mantener la conexión viva y escuchar si envían algo desde el cliente
            data = await websocket.receive_text()
            # Opcional: Podríamos procesar mensajes que vengan directo del kiosko hacia el server aquí.
            # Por ahora, solo queremos que el kiosko ESCUCHE las instrucciones.
            print(f"[{ambiente_id}] Kiosko envió: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, ambiente_id)
