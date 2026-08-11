import os
import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
import redis.asyncio as redis
import redis.exceptions  # 🟢 IMPORTANTE: Importamos las excepciones de Redis para atrapar el Timeout
import redis.asyncio as redis_async

# 🟢 Conexión independiente para el Manager (Evita colisiones e importaciones circulares)
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Mantenemos el protocol=2 para evitar el error HELLO 3
        self.redis = redis_async.from_url(REDIS_URL, decode_responses=True, protocol=2)

    async def connect(self, websocket: WebSocket, ambiente: str):
        # 🟢 ESTA ES LA LÍNEA QUE ELIMINA EL ERROR 403 FORBIDDEN
        await websocket.accept()
        
        if ambiente not in self.active_connections:
            self.active_connections[ambiente] = set()
            # Si es el primer websocket para este ambiente, nos suscribimos en Redis
            await self.subscribe_to_redis(ambiente)
            
        self.active_connections[ambiente].add(websocket)
        print(f"[{ambiente}] Kiosco conectado. Total en sala: {len(self.active_connections[ambiente])}")

    def disconnect(self, websocket: WebSocket, ambiente: str):
        if ambiente in self.active_connections:
            self.active_connections[ambiente].discard(websocket)
            print(f"[{ambiente}] Kiosco desconectado. Total en sala: {len(self.active_connections[ambiente])}")
            if not self.active_connections[ambiente]:
                del self.active_connections[ambiente]

    async def broadcast_to_ambiente(self, ambiente: str, message: dict):
        # Publica en Redis. No envía directamente a los WS locales.
        await self.redis.publish(f"ambiente:{ambiente}", json.dumps(message))

    async def subscribe_to_redis(self, ambiente: str):
        """ Escucha los eventos de Redis y los redirige a los WebSockets """
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"ambiente:{ambiente}")
        
        asyncio.create_task(self._listen_redis(pubsub, ambiente))

    async def _listen_redis(self, pubsub, ambiente: str):
        # 🟢 NUEVO BUCLE BLINDADO CONTRA TIMEOUTS DE INACTIVIDAD
        try:
            while True:
                try:
                    # get_message con timeout permite que el hilo no se bloquee infinitamente
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    
                    if message and message["type"] == "message":
                        data = message["data"]
                        # Retransmitir a todos los WebSockets conectados a este ambiente
                        if ambiente in self.active_connections:
                            dead_sockets = set()
                            for connection in self.active_connections[ambiente]:
                                try:
                                    await connection.send_text(data)
                                except Exception:
                                    dead_sockets.add(connection)
                            
                            # Limpiar conexiones muertas para liberar memoria
                            for dead in dead_sockets:
                                self.disconnect(dead, ambiente)
                                
                except redis.exceptions.TimeoutError:
                    # Silencio en la red (nadie ha enviado mensajes). Lo ignoramos y seguimos escuchando.
                    continue
                except Exception as e:
                    print(f"⚠️ Caída temporal de PubSub para {ambiente}, reintentando: {e}")
                    await asyncio.sleep(1) # Pausa de 1 seg para no saturar el CPU si hay un error grave
                    
        except asyncio.CancelledError:
            print(f"Oyente de Redis para {ambiente} cerrado de forma segura.")

manager = ConnectionManager()