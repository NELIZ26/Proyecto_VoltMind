from fastapi import APIRouter, HTTPException
from services.sesiones import registrar_fin_sesion, registrar_inicio_sesion

# Configuramos el prefijo para que las rutas sean limpias
router = APIRouter(prefix="/api/sesiones", tags=["Control de Sesiones"])

@router.post("/iniciar")
async def iniciar_sesion(ficha: str, email: str):
    try:
        resultado = await registrar_inicio_sesion(ficha, email)
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