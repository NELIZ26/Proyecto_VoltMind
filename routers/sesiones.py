from pydantic import BaseModel
from routers.asistencia import redis_client
from fastapi import APIRouter, HTTPException
from services.websocket_manager import manager
# 🟢 Importamos la nueva función 'obtener_ambientes' desde tus servicios
from services.sesiones import registrar_fin_sesion, registrar_inicio_sesion, obtener_ambientes

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
class SesionIniciadaData(BaseModel):
    ficha: str
    email: str
    ambiente_id: str = None

@router.post("/iniciar")
async def iniciar_sesion(datos: SesionIniciadaData):
    try:
        # 1. Pasamos los datos extraídos del JSON al servicio de Dataverse
        resultado = await registrar_inicio_sesion(datos.ficha, datos.email, datos.ambiente_id)
        
        # 2. Tomamos el ambiente real que nos envía el Frontend
        ambiente_actual = datos.ambiente_id or "Sin Definir"
        
        # 3. 🟢 EL BACKEND MEMORIZA EL AULA EN REDIS (Por 12 horas)
        sesion_id = resultado.get("sesion_id", "")
        if sesion_id and ambiente_actual != "Sin Definir":
            await redis_client.setex(f"sesion:{sesion_id}:ambiente", 43200, ambiente_actual)
        
        # 4. 🟢 ADIÓS AL 402 QUEMADO: Armamos el evento dinámico para WebSockets
        evento = {
            "tipo": "SESION_INICIADA",
            "hora": resultado.get("hora_entrada", ""),
            "sesion_id": sesion_id,
            "ambiente_guid": ambiente_actual
        }
        
        print(f"📢 WEBSOCKET: Sincronizando Kiosko y Dashboard en el ambiente {ambiente_actual}")
        await manager.broadcast_to_ambiente(ambiente_actual, evento)
            
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