from fastapi import APIRouter, HTTPException
# 🟢 Importamos la nueva función 'obtener_ambientes' desde tus servicios
from services.sesiones import registrar_fin_sesion, registrar_inicio_sesion, obtener_ambientes
from services.websocket_manager import manager

# Configuramos el prefijo para que las rutas sean limpias
router = APIRouter(prefix="/api/sesiones", tags=["Control de Sesiones"])

# ==========================================
# 🟢 NUEVA RUTA: Listar Ambientes de Formación
# ==========================================
@router.get("/ambientes")
async def listar_ambientes():
    try:
        resultado = await obtener_ambientes()
        return resultado
    except Exception as e:
        print("\n================ ERROR DATAVERSE AMBIENTES ================")
        print(str(e))
        print("==========================================================\n")
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# 🟡 RUTA ACTUALIZADA: Iniciar Sesión (Ahora recibe ambiente_id)
# ==========================================
@router.post("/iniciar")
async def iniciar_sesion(ficha: str, email: str, ambiente_id: str = None):
    try:
        # 🟢 Pasamos el ambiente_id a la función del servicio
        resultado = await registrar_inicio_sesion(ficha, email, ambiente_id)
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
    
# ==========================================
# ⚪ RUTA INTACTA: Finalizar Sesión
# ==========================================
@router.post("/finalizar")
async def finalizar_sesion(sesion_id: str): 
    try:
        resultado = await registrar_fin_sesion(sesion_id)
        return resultado
    except Exception as e:
        print("\n================ ERROR CIERRE DE SESIÓN ================")
        print(str(e))
        print("========================================================\n")
        raise HTTPException(status_code=400, detail=str(e))