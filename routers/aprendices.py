# routers/aprendices.py
from fastapi import APIRouter, HTTPException
from services.aprendices_service import consultar_aprendices_por_ficha
# 🚀 IMPORTAMOS EL ESCUDO Y EL LOGGER:
from services.dataverse import sanitizar_odata
from core.logger import log
from schemas.aprendices import AprendizCreate
from services.aprendices_service import consultar_aprendices_por_ficha, crear_aprendiz_service

router = APIRouter(
    prefix="/api/fichas",
    tags=["Gestión de Fichas y Aprendices"]
)

@router.get("/aprendices")
async def obtener_todos_aprendices():
    """
    Endpoint para recuperar el listado de todos los aprendices en el sistema.
    """
    try:
        log.info("Solicitando listado de todos los aprendices")
        from services.aprendices_service import consultar_todos_aprendices
        resultados = await consultar_todos_aprendices()
        return resultados
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        log.error(f"Error crítico en obtener_todos_aprendices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor.")

@router.get("/busqueda")
async def busqueda_global_aprendices(q: str):
    """
    Endpoint para buscar aprendices a nivel global por documento o nombre.
    """
    try:
        from services.aprendices_service import buscar_aprendices_global
        return await buscar_aprendices_global(q)
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        log.error(f"Error crítico en busqueda_global_aprendices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en búsqueda global")

@router.get("/{numero_ficha}/aprendices")
async def obtener_relacion_aprendices(numero_ficha: str):
    """
    Endpoint para recuperar el listado de aprendices vinculados a una ficha específica
    al interactuar con la interfaz del frontend.
    """
    try:
        # 🛡️ LIMPIAMOS EL NÚMERO DE FICHA
        ficha_segura = sanitizar_odata(numero_ficha)
        
        # 🟢 NUEVO: Registro de la petición entrante
        log.info(f"Solicitando listado de aprendices para la ficha: {numero_ficha}")
        
        # Pasamos la variable segura al servicio
        resultados = await consultar_aprendices_por_ficha(ficha_segura)
        
        # 🟢 NUEVO: Confirmación de éxito
        log.info(f"Listado de aprendices recuperado exitosamente para la ficha: {numero_ficha}")
        
        return resultados
        
    except HTTPException as http_e:
        # Errores HTTP esperados (como un 404 si la ficha no existe)
        raise http_e
    except Exception as e:
        # 🛑 REEMPLAZADO: El print desaparece y entra el log.error profesional
        log.error(f"Error crítico en obtener_relacion_aprendices (Ficha: {numero_ficha}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor.")

@router.post("/aprendiz", status_code=201)
async def crear_nuevo_aprendiz(aprendiz: AprendizCreate):
    """
    Endpoint para registrar un nuevo aprendiz y vincularlo a su ficha.
    """
    try:
        log.info(f"Petición para crear aprendiz: {aprendiz.cr6a3_documento_de_identidad}")
        resultado = await crear_aprendiz_service(aprendiz)
        return resultado
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        log.error(f"Error crítico al crear aprendiz: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado al crear el aprendiz.")