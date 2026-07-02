from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.websocket_manager import manager

router = APIRouter(prefix="/api/kiosko", tags=["Control del Kiosko"])

class KioskoEstado(BaseModel):
    ambiente_id: str
    estado: str # "ACTIVO", "BLOQUEADO", "MODO_SALIDA"

class FirmaForzada(BaseModel):
    ambiente_id: str
    aprendiz_id: str
    nombre_aprendiz: str

@router.post("/estado")
async def cambiar_estado_kiosko(payload: KioskoEstado):
    """
    Cambia el estado global del kiosko (ej. bloquear accesos después de cierta hora)
    """
    # 1. (Futuro) Aquí podrías guardar el estado en la base de datos o en Redis para persistencia
    
    # 2. Publicamos el evento por WebSockets vía Redis PubSub a todas las tablets de ese ambiente
    evento = {
        "tipo": "CAMBIO_ESTADO",
        "nuevo_estado": payload.estado
    }
    await manager.broadcast_to_ambiente(payload.ambiente_id, evento)
    
    return {"mensaje": f"Kiosko del ambiente {payload.ambiente_id} cambiado a {payload.estado}"}

@router.post("/forzar-firma")
async def forzar_firma_aprendiz(payload: FirmaForzada):
    """
    El instructor fuerza a la tablet a abrir el modal de firma para un aprendiz en específico (Salida manual).
    """
    evento = {
        "tipo": "FORZAR_FIRMA",
        "aprendiz_id": payload.aprendiz_id,
        "nombre_aprendiz": payload.nombre_aprendiz
    }
    await manager.broadcast_to_ambiente(payload.ambiente_id, evento)
    
    return {"mensaje": f"Orden de firma enviada a la tablet para {payload.nombre_aprendiz}"}
