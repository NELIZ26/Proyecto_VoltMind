# routers/tituladas.py
# ─────────────────────────────────────────────────────────────────────────────
# Módulo de Fichas Tituladas y Asignación de Ambientes: digitaliza las matrices
# de Excel de la programación académica (matriz por ficha, por instructor y
# reserva de ambientes en una sola operación).
#
# Capa HTTP únicamente: la lógica vive en services/tituladas_service.py.
# ─────────────────────────────────────────────────────────────────────────────
from functools import wraps

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from schemas.tituladas import (
    AsignacionTituladaCreate,
    AsignacionTituladaUpdate,
    DiagnosticoUpdate,
    FichaTituladaCreate,
    ProgramaCreate,
)
from services import tituladas_service as servicio

router = APIRouter(prefix="/api/tituladas", tags=["Fichas Tituladas"])

# Respaldo de archivos históricos: solo formatos de ofimática, máximo 10 MB
_EXTENSIONES_ARCHIVO = {".xlsx", ".xls", ".xlsm", ".csv", ".pdf", ".docx"}
_TAMANO_MAXIMO = 10 * 1024 * 1024


def _con_manejo_de_errores(endpoint):
    """Relanza HTTPException tal cual y envuelve cualquier otro error como 500."""
    @wraps(endpoint)
    async def envoltura(*args, **kwargs):
        try:
            return await endpoint(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            print("ERROR INESPERADO EN TITULADAS:", str(e))
            raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor.")
    return envoltura


# ── FICHAS ───────────────────────────────────────────────────────────────────
@router.get("/fichas")
@_con_manejo_de_errores
async def obtener_fichas(buscar: str | None = None, jornada: str | None = None, sede: str | None = None):
    """Listado de fichas tituladas con % de programación (filtros opcionales)."""
    return await servicio.listar_fichas(buscar, jornada, sede)


@router.post("/fichas", status_code=201)
@_con_manejo_de_errores
async def crear_ficha(datos: FichaTituladaCreate):
    """Crea una ficha titulada: su diagnóstico se genera copiando la matriz de
    competencias del programa del catálogo (código duplicado responde 409)."""
    return await servicio.crear_ficha(datos.model_dump())


@router.get("/fichas/{ficha_id}")
@_con_manejo_de_errores
async def obtener_ficha(ficha_id: str):
    """Detalle de una ficha: diagnóstico de competencias + asignaciones del calendario."""
    return await servicio.obtener_ficha(ficha_id)


@router.put("/fichas/{ficha_id}/diagnostico")
@_con_manejo_de_errores
async def actualizar_diagnostico(ficha_id: str, datos: DiagnosticoUpdate):
    """Reemplaza la matriz de competencias (diagnóstico) de la ficha. Las
    competencias con asignaciones en el calendario no se pueden eliminar (409)."""
    return await servicio.actualizar_diagnostico(
        ficha_id, [c.model_dump() for c in datos.competencias]
    )


# ── RESPALDO DE ARCHIVOS (Excel históricos de la ficha, solo lectura) ────────
@router.post("/fichas/{ficha_id}/archivos", status_code=201)
@_con_manejo_de_errores
async def subir_archivo_ficha(
    ficha_id: str,
    archivo: UploadFile = File(..., description="Archivo histórico (Excel, CSV, PDF o Word)"),
):
    """Adjunta un archivo histórico a la ficha (respaldo descargable, sin modificar)."""
    extension = ("." + archivo.filename.rsplit(".", 1)[-1].lower()) if "." in (archivo.filename or "") else ""
    if extension not in _EXTENSIONES_ARCHIVO:
        raise HTTPException(
            status_code=422,
            detail=f"El formato '{extension or 'sin extensión'}' no está permitido. "
                   f"Formatos aceptados: {', '.join(sorted(_EXTENSIONES_ARCHIVO))}.",
        )
    contenido = await archivo.read()
    if len(contenido) > _TAMANO_MAXIMO:
        raise HTTPException(status_code=422, detail="El archivo supera el tamaño máximo permitido (10 MB).")
    if not contenido:
        raise HTTPException(status_code=422, detail="El archivo está vacío.")
    archivos = await servicio.agregar_archivo_ficha(ficha_id, archivo.filename, contenido)
    return {"archivos": archivos}


@router.get("/fichas/{ficha_id}/archivos/{archivo_id}")
@_con_manejo_de_errores
async def descargar_archivo_ficha(ficha_id: str, archivo_id: str):
    """Descarga un archivo del respaldo histórico de la ficha."""
    ruta, nombre = servicio.obtener_archivo_ficha(ficha_id, archivo_id)
    return FileResponse(ruta, filename=nombre)


@router.delete("/fichas/{ficha_id}/archivos/{archivo_id}")
@_con_manejo_de_errores
async def eliminar_archivo_ficha(ficha_id: str, archivo_id: str):
    """Elimina un archivo del respaldo de la ficha."""
    return await servicio.eliminar_archivo_ficha(ficha_id, archivo_id)


# ── CATÁLOGOS ────────────────────────────────────────────────────────────────
@router.get("/instructores")
@_con_manejo_de_errores
async def obtener_instructores():
    """Instructores con perfil, tipo de vinculación, fin de contrato y color."""
    return await servicio.listar_instructores()


@router.get("/programas")
@_con_manejo_de_errores
async def obtener_programas():
    """Catálogo de programas de formación (nombre, versión, nivel y competencias)."""
    return await servicio.listar_programas()


@router.post("/programas", status_code=201)
@_con_manejo_de_errores
async def crear_programa(datos: ProgramaCreate):
    """Registra un programa en el catálogo (nombre + versión duplicados → 409)."""
    return await servicio.crear_programa(datos.model_dump())


# ── CALENDARIO DEL INSTRUCTOR (la "matriz por instructor" del Excel) ─────────
@router.get("/calendario-instructor")
@_con_manejo_de_errores
async def obtener_calendario_instructor(instructor_id: str | None = None, correo: str | None = None):
    """Programación completa de un instructor, por id o por correo institucional."""
    return await servicio.calendario_instructor(instructor_id, correo)


@router.get("/ambientes")
@_con_manejo_de_errores
async def obtener_ambientes():
    """Ambientes de formación con sede, capacidad y tipo."""
    return await servicio.listar_ambientes()


# ── DISPONIBILIDAD ───────────────────────────────────────────────────────────
@router.get("/disponibilidad")
@_con_manejo_de_errores
async def obtener_disponibilidad(
    ficha_id: str,
    fecha_inicio: str,
    fecha_fin: str,
    excluir_asignacion: str | None = None,
):
    """Semáforo de instructores (disponible/ocupado/contrato vencido) y ambientes
    para el rango pedido, en la jornada de la ficha. `excluir_asignacion` permite
    editar una asignación sin que se marque a sí misma como cruce."""
    return await servicio.consultar_disponibilidad(ficha_id, fecha_inicio, fecha_fin, excluir_asignacion)


# ── ASIGNACIONES ─────────────────────────────────────────────────────────────
@router.post("/asignaciones", status_code=201)
@_con_manejo_de_errores
async def crear_asignacion(datos: AsignacionTituladaCreate):
    """Programa un rango de días. Valida cruces de ficha, instructor y ambiente,
    contrato vigente y período lectivo (todo responde 409 con mensaje claro)."""
    return await servicio.crear_asignacion(datos.model_dump())


@router.patch("/asignaciones/{asignacion_id}")
@_con_manejo_de_errores
async def actualizar_asignacion(asignacion_id: str, datos: AsignacionTituladaUpdate):
    """Edita una asignación revalidando todas las reglas de negocio."""
    return await servicio.actualizar_asignacion(asignacion_id, datos.model_dump())


@router.delete("/asignaciones/{asignacion_id}")
@_con_manejo_de_errores
async def eliminar_asignacion(asignacion_id: str):
    """Elimina la asignación y libera ficha, instructor y ambiente."""
    return await servicio.eliminar_asignacion(asignacion_id)


# ── INDICADORES ──────────────────────────────────────────────────────────────
@router.get("/indicadores")
@_con_manejo_de_errores
async def obtener_indicadores(mes: str | None = None):
    """Meta del 70 %, alertas de técnica < 60 % y carga mensual por instructor
    frente a su límite (160 h contratista / 128 h planta). `mes` = YYYY-MM."""
    return await servicio.obtener_indicadores(mes)
