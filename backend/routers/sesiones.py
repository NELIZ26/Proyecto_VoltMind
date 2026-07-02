from fastapi import APIRouter, HTTPException
from services.sesiones import registrar_fin_sesion, registrar_inicio_sesion
from services.websocket_manager import manager

# Configuramos el prefijo para que las rutas sean limpias
router = APIRouter(prefix="/api/sesiones", tags=["Control de Sesiones"])

@router.post("/iniciar")
async def iniciar_sesion(ficha: str, email: str):
    try:
        resultado = await registrar_inicio_sesion(ficha, email)
        # Emitimos el evento de inicio de sesión
        import asyncio
        evento = {
            "tipo": "SESION_INICIADA",
            "hora": resultado.get("hora_entrada", ""),
            "sesion_id": resultado.get("sesion_id", "")
        }
        asyncio.create_task(manager.broadcast_to_ambiente("402", evento))
        return resultado
    except Exception as e:
        print("\n================ ERROR DATAVERSE SESIONES ================")
        print(str(e))
        print("==========================================================\n")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/finalizar")
async def finalizar_sesion(sesion_id: str): # <-- ¡Cambia 'ficha' por 'sesion_id' aquí!
    try:
        resultado = await registrar_fin_sesion(sesion_id)
        return resultado
    except Exception as e:
        print("\n================ ERROR CIERRE DE SESIÓN ================")
        print(str(e))
        print("========================================================\n")
        raise HTTPException(status_code=400, detail=str(e))