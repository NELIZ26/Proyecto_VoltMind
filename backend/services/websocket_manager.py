import json
from typing import Dict, Set
from fastapi import WebSocket
from services.redis_client import get_redis_client

class ConnectionManager:
    def __init__(self):
        # Diccionario para mantener las conexiones activas por ambiente
        # Ej: {"402": {websocket1, websocket2}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.pubsub = None

    async def connect(self, websocket: WebSocket, ambiente: str):
        await websocket.accept()
        if ambiente not in self.active_connections:
            self.active_connections[ambiente] = set()
            # Si es el primer websocket para este ambiente, nos suscribimos en Redis
            await self.subscribe_to_redis(ambiente)
        self.active_connections[ambiente].add(websocket)
        print(f"[{ambiente}] Cliente conectado. Total: {len(self.active_connections[ambiente])}")

    def disconnect(self, websocket: WebSocket, ambiente: str):
        if ambiente in self.active_connections:
            self.active_connections[ambiente].discard(websocket)
            print(f"[{ambiente}] Cliente desconectado. Total: {len(self.active_connections[ambiente])}")
            if not self.active_connections[ambiente]:
                del self.active_connections[ambiente]
                # Podríamos desuscribirnos de Redis si el ambiente se queda vacío
                # pero para mantenerlo simple, lo dejamos vivo.

    async def broadcast_to_ambiente(self, ambiente: str, message: dict):
        # Este método publica en Redis. No envía directamente a los WS.
        redis = await get_redis_client()
        await redis.publish(f"ambiente:{ambiente}", json.dumps(message))

    async def subscribe_to_redis(self, ambiente: str):
        """ Escucha los eventos de Redis y los redirige a todos los WebSockets locales de ese ambiente """
        redis = await get_redis_client()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"ambiente:{ambiente}")
        
        import asyncio
        asyncio.create_task(self._listen_redis(pubsub, ambiente))

    async def _listen_redis(self, pubsub, ambiente: str):
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    # Retransmitir a todos los WebSockets locales conectados a este ambiente
                    if ambiente in self.active_connections:
                        dead_sockets = set()
                        for connection in self.active_connections[ambiente]:
                            try:
                                await connection.send_text(data)
                            except Exception:
                                dead_sockets.add(connection)
                        
                        # Limpiar conexiones muertas
                        for dead in dead_sockets:
                            self.disconnect(dead, ambiente)
        except Exception as e:
            print(f"Error escuchando Redis PubSub para {ambiente}: {e}")

manager = ConnectionManager()
