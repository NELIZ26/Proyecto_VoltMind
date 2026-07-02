from fastapi import APIRouter, HTTPException
from services.dataverse import obtener_cliente, sanitizar_odata
# 🚀 NUEVO: Importamos el logger profesional centralizado
from core.logger import log

router = APIRouter(
    prefix="/api/fichas",
    tags=["Fichas y Aprendices"]
)

@router.get("/{correo_instructor}")
async def obtener_fichas_por_instructor(correo_instructor: str):
    try:
        # 🛡️ PASO 0: Sanitizar la entrada y forzar MINÚSCULAS (El exorcismo + La armadura)
        correo_limpio = correo_instructor.lower() # 🟢 Conversión obligatoria para Dataverse
        correo_seguro = sanitizar_odata(correo_limpio)
        log.info(f"Iniciando consulta de fichas para el instructor: {correo_seguro}")

        # Cliente Dataverse
        client = obtener_cliente()

        # PASO 1: Buscar instructor (usando el correo limpio)
        url_instructor = (
            f"cr6a3_instructors?"
            f"$filter=cr6a3_correo_institucional eq '{correo_seguro}'"
            f"&$select=cr6a3_instructorid,cr6a3_nombre_completo"
        )

        res_instructor = await client.get(url_instructor)

        if res_instructor.status_code != 200:
            # 🛑 REEMPLAZADO: log.error registra el estatus exacto y la respuesta de Microsoft sin perder datos
            log.error(
                f"Falla en Dataverse (Paso 1) para {correo_seguro}. "
                f"Status: {res_instructor.status_code}. Respuesta: {res_instructor.text}"
            )
            raise HTTPException(
                status_code=res_instructor.status_code,
                detail="Error al buscar el instructor en Dataverse"
            )

        datos_instructor = res_instructor.json().get("value", [])

        if not datos_instructor:
            # ⚠️ NUEVO: log.warning nos avisa si alguien consulta un correo que no existe en el SENA
            log.warning(f"Intento de acceso de instructor no registrado: {correo_seguro}")
            raise HTTPException(
                status_code=404,
                detail="Instructor no encontrado en el sistema"
            )

        instructor_id = datos_instructor[0]["cr6a3_instructorid"]
        nombre_instructor = datos_instructor[0]["cr6a3_nombre_completo"]
        log.info(f"Instructor autenticado exitosamente: {nombre_instructor} (ID: {instructor_id})")

        # PASO 2: Buscar fichas asociadas
        url_fichas = (
            f"cr6a3_fichas?"
            f"$filter=_cr6a3_instructorasignado_value eq '{instructor_id}'"
            f"&$select=cr6a3_numero_ficha,cr6a3_nombre_programa"
        )

        res_fichas = await client.get(url_fichas)

        if res_fichas.status_code != 200:
            # 🛑 REEMPLAZADO: log.error para auditoría de la consulta de fichas
            log.error(
                f"Falla en Dataverse (Paso 2) para ID Instructor {instructor_id}. "
                f"Status: {res_fichas.status_code}. Respuesta: {res_fichas.text}"
            )
            raise HTTPException(
                status_code=res_fichas.status_code,
                detail="Error al recuperar las fichas de Dataverse"
            )

        datos_fichas = res_fichas.json().get("value", [])
        
        # 🟢 NUEVO: Monitoreo del volumen de datos transferidos
        log.info(f"Fichas recuperadas con éxito. Total: {len(datos_fichas)} para el instructor {nombre_instructor}")

        fichas_mapeadas = [
            {
                "numero_ficha": ficha.get("cr6a3_numero_ficha"),
                "nombre_programa": ficha.get("cr6a3_nombre_programa")
            }
            for ficha in datos_fichas
        ]

        return fichas_mapeadas

    except HTTPException as http_e:
        # Los errores HTTP controlados se elevan directamente sin ensuciar el log general de caídas
        raise http_e

    except Exception as e:
        # 🛑 REEMPLAZADO y Mejorado: El parámetro exc_info=True es una joya. 
        # No solo guarda tu mensaje personalizado, sino que vuelca TODO el árbol del error 
        # (Traceback completo con las líneas exactas de la falla) directamente en el archivo .log
        log.error(f"Colapso crítico en obtener_fichas_por_instructor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error inesperado en el servidor de VoltMind."
        )