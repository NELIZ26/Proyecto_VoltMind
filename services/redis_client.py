import redis.asyncio as redis
import os

# Configuración básica de conexión a Redis (Localhost por defecto en el puerto 6379)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cliente de Redis Singleton
_redis_client = None

async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True, protocol=2)
    return _redis_client

async def close_redis_client():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
