# routers/complementarias.py
# ─────────────────────────────────────────────────────────────────────────────
# Módulo de Fichas Complementarias: seguimiento de las solicitudes de
# formación complementaria (reemplaza la matriz de Excel del coordinador).
#
# Capa HTTP únicamente: la lógica vive en services/complementarias_service.py
# (que decide automáticamente entre Dataverse y el modo demo local).
# ─────────────────────────────────────────────────────────────────────────────
import json
from functools import wraps

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import ValidationError

from schemas.complementarias import (
    SolicitudComplementariaCreate,
    SolicitudComplementariaUpdate,
)
from services import complementarias_service as servicio
from services import notificaciones_service

# Reglas de los archivos que sube el instructor (validadas ANTES de crear nada)
TAMANO_MAXIMO_MB = 10
_EXTENSIONES_PERMITIDAS = {
    "matriz": {".xlsx", ".xls", ".xlsm", ".csv"},
    "plano": {".xlsx", ".xls", ".pdf"},
    "adicional": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"},
    "resultados": {".xlsx", ".xls", ".xlsm"},
}
_ETIQUETAS_ARCHIVO = {
    "matriz": "la matriz de la ficha",
    "plano": "el archivo plano de aprendices",
    "adicional": "el documento adicional",
    "resultados": "los resultados de aprendices inscritos",
}

router = APIRouter(prefix="/api/complementarias", tags=["Fichas Complementarias"])


def _con_manejo_de_errores(endpoint):
    """Relanza HTTPException tal cual y envuelve cualquier otro error como 500.
    `@wraps` conserva la firma original, que FastAPI usa para armar el endpoint."""
    @wraps(endpoint)
    async def envoltura(*args, **kwargs):
        try:
            return await endpoint(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            print("ERROR INESPERADO EN COMPLEMENTARIAS:", str(e))
            raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor.")
    return envoltura


def _validar_archivo_subido(campo: str, archivo: UploadFile, contenido: bytes) -> None:
    """Extensión permitida y tamaño máximo, con mensajes claros en español (422)."""
    extension = ("." + archivo.filename.rsplit(".", 1)[-1].lower()) if "." in (archivo.filename or "") else ""
    permitidas = _EXTENSIONES_PERMITIDAS[campo]
    if extension not in permitidas:
        raise HTTPException(
            status_code=422,
            detail=(
                f"El formato '{extension or 'sin extensión'}' no es válido para "
                f"{_ETIQUETAS_ARCHIVO[campo]}. Formatos permitidos: {', '.join(sorted(permitidas))}."
            ),
        )
    if len(contenido) == 0:
        raise HTTPException(status_code=422, detail=f"El archivo de {_ETIQUETAS_ARCHIVO[campo]} está vacío.")
    if len(contenido) > TAMANO_MAXIMO_MB * 1024 * 1024:
        raise HTTPException(
            status_code=422,
            detail=(
                f"El archivo '{archivo.filename}' supera el tamaño máximo de "
                f"{TAMANO_MAXIMO_MB} MB. Comprima o divida el documento."
            ),
        )


# ── SOLICITUDES ──────────────────────────────────────────────────────────────
@router.get("/solicitudes")
@_con_manejo_de_errores
async def obtener_solicitudes(
    estado: str | None = None,
    municipio: str | None = None,
    jornada: str | None = None,
    instructor: str | None = None,
    buscar: str | None = None,
    correo: str | None = None,
):
    """Lista las solicitudes con filtros opcionales (estado, municipio, jornada, instructor,
    correo del instructor para "mis solicitudes") y buscador por programa o código de ficha."""
    return await servicio.listar_solicitudes(estado, municipio, jornada, instructor, buscar, correo)


@router.post("/solicitudes", status_code=201)
@_con_manejo_de_errores
async def crear_solicitud(datos: SolicitudComplementariaCreate):
    """Crea una solicitud. Valida coherencia de fechas y código de ficha duplicado (409)."""
    return await servicio.crear_solicitud(datos.model_dump())


@router.post("/solicitudes/con-archivos", status_code=201)
@_con_manejo_de_errores
async def crear_solicitud_con_archivos(
    datos: str = Form(..., description="Campos de la solicitud en JSON"),
    archivo_matriz: UploadFile = File(..., description="Matriz de la ficha (obligatorio)"),
    archivo_plano: UploadFile = File(..., description="Archivo plano de aprendices (obligatorio)"),
    archivo_adicional: UploadFile | None = File(None, description="Documento adicional (opcional)"),
):
    """Flujo del INSTRUCTOR: crea la solicitud (estado Pendiente), almacena los archivos
    en VoltMind y notifica al administrador — todo en una sola operación."""
    # 1. Validar los campos del formulario con el mismo schema del POST normal
    try:
        modelo = SolicitudComplementariaCreate(**json.loads(datos))
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="El campo 'datos' no contiene un JSON válido.")
    except ValidationError as e:
        primer_error = e.errors()[0]
        raise HTTPException(
            status_code=422,
            detail=f"Datos inválidos ({primer_error.get('loc', ['?'])[0]}): {primer_error.get('msg', '')}",
        )

    # 2. Leer y validar los archivos ANTES de crear la solicitud
    pares = [("matriz", archivo_matriz), ("plano", archivo_plano)]
    if archivo_adicional and archivo_adicional.filename:
        pares.append(("adicional", archivo_adicional))

    archivos = []
    for campo, archivo in pares:
        contenido = await archivo.read()
        _validar_archivo_subido(campo, archivo, contenido)
        archivos.append({"campo": campo, "nombre": archivo.filename, "contenido": contenido})

    # 3. Crear la solicitud: siempre nace Pendiente (el instructor no gestiona)
    cuerpo = {**modelo.model_dump(), "estado": "Pendiente"}
    nueva = await servicio.crear_solicitud(cuerpo)

    # 4. Guardar los archivos; si algo falla, se revierte la solicitud
    try:
        nueva["archivos"] = await servicio.guardar_archivos_solicitud(nueva["id"], archivos)
    except Exception:
        await servicio.eliminar_solicitud(nueva["id"])
        raise HTTPException(
            status_code=500,
            detail="No se pudieron guardar los archivos adjuntos. La solicitud no fue registrada; intente de nuevo.",
        )
    return nueva


@router.post("/solicitudes/{solicitud_id}/archivos/resultados", status_code=201)
@_con_manejo_de_errores
async def subir_resultados(
    solicitud_id: str,
    archivo: UploadFile = File(..., description="Excel con los resultados de aprendices inscritos"),
):
    """Flujo del ADMINISTRADOR: adjunta (o reemplaza) el archivo de resultados de
    aprendices inscritos de la ficha. Es el único documento que el instructor
    podrá descargar desde 'Mis solicitudes' cuando la ficha esté Publicada."""
    contenido = await archivo.read()
    _validar_archivo_subido("resultados", archivo, contenido)
    meta = await servicio.agregar_archivo_solicitud(
        solicitud_id, "resultados", archivo.filename, contenido
    )
    return {"archivos": meta}


@router.get("/solicitudes/{solicitud_id}/archivos/{campo}")
@_con_manejo_de_errores
async def descargar_archivo(solicitud_id: str, campo: str, inline: bool = False):
    """Descarga de un archivo de la solicitud (matriz | plano | adicional | resultados).
    Con `?inline=true` se sirve para verlo en el navegador (vista previa del admin)."""
    ruta, nombre = servicio.obtener_archivo(solicitud_id, campo)
    return FileResponse(
        ruta,
        filename=nombre,
        content_disposition_type="inline" if inline else "attachment",
    )


@router.patch("/solicitudes/{solicitud_id}")
@_con_manejo_de_errores
async def actualizar_solicitud(solicitud_id: str, datos: SolicitudComplementariaUpdate):
    """Actualiza campos de una solicitud (estado, checklist de seguimiento, inscritos, etc.)."""
    return await servicio.actualizar_solicitud(solicitud_id, datos.model_dump(exclude_none=True))


@router.post("/solicitudes/{solicitud_id}/reenviar-aviso")
@_con_manejo_de_errores
async def reenviar_aviso(solicitud_id: str):
    """Reenvía al instructor el aviso de ficha Publicada (correo + campana) y
    actualiza la marca `notificado`. Respaldo manual para casos puntuales."""
    solicitud = await servicio.obtener_solicitud(solicitud_id)
    if solicitud.get("estado") != "Publicada":
        raise HTTPException(
            status_code=409,
            detail="Solo se puede enviar el aviso cuando la solicitud está en estado Publicada.",
        )
    return await servicio.avisar_publicacion(solicitud)


@router.delete("/solicitudes/{solicitud_id}")
@_con_manejo_de_errores
async def eliminar_solicitud(solicitud_id: str):
    return await servicio.eliminar_solicitud(solicitud_id)


# ── INDICADORES ──────────────────────────────────────────────────────────────
@router.get("/indicadores")
@_con_manejo_de_errores
async def obtener_indicadores():
    """Totales por estado e inscritos para la cabecera de la sección."""
    return await servicio.obtener_indicadores()


# ── NOTIFICACIONES ───────────────────────────────────────────────────────────
# La campana del panel admin consulta esta lista por polling (~45 s).
@router.get("/notificaciones")
@_con_manejo_de_errores
async def obtener_notificaciones(destinatario: str = "admin", solo_no_leidas: bool = False):
    """Notificaciones del destinatario, de la más reciente a la más antigua."""
    return await notificaciones_service.listar_notificaciones(destinatario, solo_no_leidas)


@router.patch("/notificaciones/{notificacion_id}/leida")
@_con_manejo_de_errores
async def marcar_notificacion_leida(notificacion_id: str):
    """Marca la notificación como leída (se llama al abrir el aviso en la campana)."""
    return await notificaciones_service.marcar_leida(notificacion_id)
