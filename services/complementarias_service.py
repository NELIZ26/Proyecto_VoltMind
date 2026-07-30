# services/complementarias_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Módulo de Fichas Complementarias: seguimiento de solicitudes de formación
# complementaria del Centro Agroforestal y Acuícola Arapaima.
# Reemplaza la matriz de Excel del coordinador (una solicitud = una fila).
#
# Funciona en DOS MODOS automáticos (mismo patrón que programacion_service):
#   1. DATAVERSE : con credenciales en .env consulta la tabla real.
#   2. DEMO      : sin credenciales persiste en backend/data/complementarias_demo.json
#                  con datos semilla. El contrato de la API es IDÉNTICO.
#
# ⚠️ La tabla de Dataverse aún NO existe. Plural OData ASUMIDO
# `cr6a3_fichacomplementarias`, configurable vía env (TABLA_COMPLEMENTARIAS).
# Spec de columnas: docs/DATAVERSE_TABLAS.md (sección Ficha Complementaria).
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import json
import uuid
import shutil
import asyncio
import smtplib
from email.message import EmailMessage
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pathlib import Path

from fastapi import HTTPException

from schemas.complementarias import ESTADOS_SOLICITUD
from services.dataverse import (
    cliente_dataverse,
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    DATAVERSE_URL,
)
from services import notificaciones_service

TABLA_COMPLEMENTARIAS = os.getenv("TABLA_COMPLEMENTARIAS", "cr6a3_fichacomplementarias")

# Mapeo campo API ↔ columna Dataverse (una sola fuente de verdad).
# `enlaces_pdf` viaja como texto con URLs separadas por ';'.
_CAMPOS_DV = {
    "nombre_instructor": "cr6a3_nombre_instructor",
    "correo_instructor": "cr6a3_correo_instructor",
    "celular_instructor": "cr6a3_celular_instructor",
    "codigo_programa": "cr6a3_codigo_programa",
    "version_programa": "cr6a3_version_programa",
    "nombre_programa": "cr6a3_nombre_programa",
    "duracion_horas": "cr6a3_duracion_horas",
    "fecha_inicio_inscripcion": "cr6a3_fecha_inicio_inscripcion",
    "fecha_cierre_inscripcion": "cr6a3_fecha_cierre_inscripcion",
    "fecha_inicio_formacion": "cr6a3_fecha_inicio_formacion",
    "fecha_fin_formacion": "cr6a3_fecha_fin_formacion",
    "jornada": "cr6a3_jornada",
    "municipio": "cr6a3_municipio",
    "lugar_ejecucion": "cr6a3_lugar_ejecucion",
    "enlace_carta_empresa": "cr6a3_enlace_carta_empresa",
    "enlace_formato_solicitud": "cr6a3_enlace_formato_solicitud",
    "enlace_matriz_ficha": "cr6a3_enlace_matriz_ficha",
    "enlace_archivo_plano": "cr6a3_enlace_archivo_plano",
    "enlaces_pdf": "cr6a3_enlaces_pdf",
    "codigo_empresa": "cr6a3_codigo_empresa",
    "codigo_ficha": "cr6a3_codigo_ficha",
    "fecha_creacion": "cr6a3_fecha_creacion",
    "publicacion": "cr6a3_publicacion",
    "asignar_ficha": "cr6a3_asignar_ficha",
    "gestion_ficha": "cr6a3_gestion_ficha",
    "proceso_matricula": "cr6a3_proceso_matricula",
    "estado": "cr6a3_estado",
    "enlace_lista_matriculados": "cr6a3_enlace_lista_matriculados",
    "observaciones": "cr6a3_observaciones",
    "cantidad_inscritos": "cr6a3_cantidad_inscritos",
    # Fecha/hora ISO del último aviso de publicación enviado al instructor
    "notificado": "cr6a3_notificado",
    # Metadatos de los archivos subidos por el instructor (JSON serializado).
    # Los archivos físicos viven en backend/storage/complementarias/<id>/.
    "archivos": "cr6a3_archivos_json",
}
_ID_DV = "cr6a3_fichacomplementariaid"

_RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
_RUTA_DEMO = _RUTA_DATA / "complementarias_demo.json"

# Archivos por solicitud: matriz/plano/adicional los sube el instructor y
# "resultados" (aprendices inscritos) lo adjunta el administrador al finalizar.
# Se guardan en disco en AMBOS modos: Dataverse solo conserva los metadatos.
_RUTA_STORAGE = Path(__file__).resolve().parent.parent / "storage" / "complementarias"
CAMPOS_ARCHIVO = ("matriz", "plano", "adicional", "resultados")

# Serializa los ciclos cargar-validar-guardar del modo demo
_demo_lock = asyncio.Lock()

_ZONA_BOGOTA = ZoneInfo("America/Bogota")


def dataverse_configurado() -> bool:
    """True si el .env tiene todas las credenciales necesarias de Dataverse."""
    return all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, DATAVERSE_URL])


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIONES DE NEGOCIO (comunes a ambos modos)
# ─────────────────────────────────────────────────────────────────────────────
def _validar_coherencia_fechas(datos: dict) -> None:
    """Las fechas de cada par deben estar en orden cronológico (409 si no)."""
    pares = [
        ("fecha_inicio_inscripcion", "fecha_cierre_inscripcion", "inscripciones"),
        ("fecha_inicio_formacion", "fecha_fin_formacion", "formación"),
    ]
    for inicio, fin, etiqueta in pares:
        v_inicio, v_fin = datos.get(inicio) or "", datos.get(fin) or ""
        if v_inicio and v_fin and date.fromisoformat(v_fin) < date.fromisoformat(v_inicio):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"La fecha de cierre/fin de {etiqueta} ({v_fin}) no puede ser anterior "
                    f"a la de inicio ({v_inicio}). Corrija las fechas de la solicitud."
                ),
            )


def _validar_ficha_duplicada(solicitudes: list, datos: dict, excluir_id: str | None = None) -> None:
    """Un código de ficha asignado no puede repetirse entre solicitudes (409)."""
    codigo = (datos.get("codigo_ficha") or "").strip()
    if not codigo:
        return
    for s in solicitudes:
        if s.get("codigo_ficha") == codigo and s.get("id") != excluir_id:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"El código de ficha {codigo} ya está registrado en la solicitud "
                    f'"{s.get("nombre_programa", "")}" de {s.get("nombre_instructor", "")}. '
                    "Verifique el número en Sofía Plus."
                ),
            )


# ─────────────────────────────────────────────────────────────────────────────
# MODO DEMO — Persistencia local en JSON
# ─────────────────────────────────────────────────────────────────────────────
_SEMILLA_DEMO = {
    "solicitudes": [
        {
            "id": "comp-6",
            "nombre_instructor": "Andrea Guzmán", "correo_instructor": "aguzman@sena.edu.co",
            "celular_instructor": "3157788990",
            "codigo_programa": "13410002", "version_programa": "1",
            "nombre_programa": "Manipulación Higiénica de Alimentos", "duracion_horas": 40,
            "fecha_inicio_inscripcion": "2026-07-13", "fecha_cierre_inscripcion": "2026-07-24",
            "fecha_inicio_formacion": "2026-08-03", "fecha_fin_formacion": "2026-09-04",
            "jornada": "Mañana", "municipio": "Villagarzón",
            "lugar_ejecucion": "Restaurante escolar — I.E. Villagarzón",
            "enlace_carta_empresa": "",
            "enlace_formato_solicitud": "",
            "enlace_matriz_ficha": "https://forms.office.com/matriz-13410002.xlsx",
            "enlace_archivo_plano": "https://forms.office.com/plano-13410002.txt",
            "enlaces_pdf": [],
            "codigo_empresa": "", "codigo_ficha": "",
            "fecha_creacion": "2026-07-06",
            "publicacion": False, "asignar_ficha": False, "gestion_ficha": False, "proceso_matricula": False,
            "estado": "Pendiente",
            "enlace_lista_matriculados": "",
            "observaciones": "",
            "cantidad_inscritos": 0,
            "notificado": "",
        },
        {
            "id": "comp-1",
            "nombre_instructor": "Carlos Díaz", "correo_instructor": "cdiaz@sena.edu.co",
            "celular_instructor": "3114567890",
            "codigo_programa": "12310114", "version_programa": "1",
            "nombre_programa": "Excel Básico para el Registro de Información", "duracion_horas": 40,
            "fecha_inicio_inscripcion": "2026-06-15", "fecha_cierre_inscripcion": "2026-06-30",
            "fecha_inicio_formacion": "2026-07-06", "fecha_fin_formacion": "2026-08-07",
            "jornada": "Tarde", "municipio": "Puerto Asís",
            "lugar_ejecucion": "Alcaldía de Puerto Asís — Sala de sistemas",
            "enlace_carta_empresa": "https://forms.office.com/carta-alcaldia.pdf",
            "enlace_formato_solicitud": "https://forms.office.com/solicitud-12310114.pdf",
            "enlace_archivo_plano": "https://forms.office.com/plano-12310114.txt",
            "enlaces_pdf": ["https://forms.office.com/listado-preinscritos.pdf"],
            "codigo_empresa": "EMP-9014521", "codigo_ficha": "3120045",
            "fecha_creacion": "2026-06-10",
            "publicacion": True, "asignar_ficha": True, "gestion_ficha": True, "proceso_matricula": True,
            "estado": "En Ejecución",
            "enlace_lista_matriculados": "https://forms.office.com/matriculados-3120045.pdf",
            "observaciones": "Grupo completo. La alcaldía presta el aula con 25 equipos.",
            "cantidad_inscritos": 25,
            "notificado": "",
        },
        {
            "id": "comp-2",
            "nombre_instructor": "Luisa Bañól", "correo_instructor": "lbanol@sena.edu.co",
            "celular_instructor": "3129876543",
            "codigo_programa": "23310017", "version_programa": "2",
            "nombre_programa": "Instalación de Redes de Datos en Cobre", "duracion_horas": 48,
            "fecha_inicio_inscripcion": "2026-07-01", "fecha_cierre_inscripcion": "2026-07-20",
            "fecha_inicio_formacion": "2026-08-03", "fecha_fin_formacion": "2026-09-11",
            "jornada": "Noche", "municipio": "Mocoa",
            "lugar_ejecucion": "Institución Educativa Ciudad Mocoa",
            "enlace_carta_empresa": "https://forms.office.com/carta-iemocoa.pdf",
            "enlace_formato_solicitud": "https://forms.office.com/solicitud-23310017.pdf",
            "enlace_archivo_plano": "",
            "enlaces_pdf": [],
            "codigo_empresa": "EMP-9014876", "codigo_ficha": "",
            "fecha_creacion": "2026-06-28",
            "publicacion": True, "asignar_ficha": False, "gestion_ficha": False, "proceso_matricula": False,
            "estado": "Publicada",
            "enlace_lista_matriculados": "",
            "observaciones": "Pendiente completar el mínimo de 20 inscritos para asignar ficha.",
            "cantidad_inscritos": 13,
            "notificado": "",
        },
        {
            "id": "comp-3",
            "nombre_instructor": "Elena Martínez", "correo_instructor": "emartinez@sena.edu.co",
            "celular_instructor": "3105554433",
            "codigo_programa": "63310010", "version_programa": "1",
            "nombre_programa": "Emprendimiento y Fortalecimiento Empresarial", "duracion_horas": 60,
            "fecha_inicio_inscripcion": "2026-06-20", "fecha_cierre_inscripcion": "2026-07-10",
            "fecha_inicio_formacion": "2026-07-21", "fecha_fin_formacion": "2026-09-25",
            "jornada": "Mañana", "municipio": "Sibundoy",
            "lugar_ejecucion": "Casa de la Cultura de Sibundoy",
            "enlace_carta_empresa": "https://forms.office.com/carta-sibundoy.pdf",
            "enlace_formato_solicitud": "https://forms.office.com/solicitud-63310010.pdf",
            "enlace_archivo_plano": "https://forms.office.com/plano-63310010.txt",
            "enlaces_pdf": ["https://forms.office.com/cronograma-63310010.pdf"],
            "codigo_empresa": "EMP-9015102", "codigo_ficha": "3120088",
            "fecha_creacion": "2026-06-18",
            "publicacion": True, "asignar_ficha": True, "gestion_ficha": False, "proceso_matricula": False,
            "estado": "Publicada",
            "enlace_lista_matriculados": "",
            "observaciones": "",
            "cantidad_inscritos": 21,
            "notificado": "",
        },
        {
            "id": "comp-4",
            "nombre_instructor": "Juan Pérez", "correo_instructor": "jperez@sena.edu.co",
            "celular_instructor": "3201112233",
            "codigo_programa": "41310028", "version_programa": "1",
            "nombre_programa": "Fotografía Básica con Dispositivos Móviles", "duracion_horas": 40,
            "fecha_inicio_inscripcion": "2026-05-04", "fecha_cierre_inscripcion": "2026-05-22",
            "fecha_inicio_formacion": "2026-06-01", "fecha_fin_formacion": "2026-07-03",
            "jornada": "Tarde", "municipio": "Orito",
            "lugar_ejecucion": "Biblioteca Municipal de Orito",
            "enlace_carta_empresa": "",
            "enlace_formato_solicitud": "https://forms.office.com/solicitud-41310028.pdf",
            "enlace_archivo_plano": "",
            "enlaces_pdf": [],
            "codigo_empresa": "", "codigo_ficha": "",
            "fecha_creacion": "2026-04-28",
            "publicacion": True, "asignar_ficha": False, "gestion_ficha": False, "proceso_matricula": False,
            "estado": "Cancelada",
            "enlace_lista_matriculados": "",
            "observaciones": "Cancelada por baja inscripción (7 personas). Se reprogramará en el segundo semestre.",
            "cantidad_inscritos": 7,
            "notificado": "",
        },
        {
            "id": "comp-5",
            "nombre_instructor": "Carlos Díaz", "correo_instructor": "cdiaz@sena.edu.co",
            "celular_instructor": "3114567890",
            "codigo_programa": "22210025", "version_programa": "3",
            "nombre_programa": "Buenas Prácticas Piscícolas para la Producción de Arapaima", "duracion_horas": 80,
            "fecha_inicio_inscripcion": "2026-06-01", "fecha_cierre_inscripcion": "2026-06-19",
            "fecha_inicio_formacion": "2026-06-29", "fecha_fin_formacion": "2026-09-04",
            "jornada": "Mixta", "municipio": "Puerto Leguízamo",
            "lugar_ejecucion": "Asociación de Piscicultores del Bajo Putumayo",
            "enlace_carta_empresa": "https://forms.office.com/carta-asopez.pdf",
            "enlace_formato_solicitud": "https://forms.office.com/solicitud-22210025.pdf",
            "enlace_archivo_plano": "https://forms.office.com/plano-22210025.txt",
            "enlaces_pdf": ["https://forms.office.com/guia-practicas.pdf", "https://forms.office.com/acta-inicio.pdf"],
            "codigo_empresa": "EMP-9013990", "codigo_ficha": "3119902",
            "fecha_creacion": "2026-05-26",
            "publicacion": True, "asignar_ficha": True, "gestion_ficha": True, "proceso_matricula": True,
            "estado": "En Ejecución",
            "enlace_lista_matriculados": "https://forms.office.com/matriculados-3119902.pdf",
            "observaciones": "Formación en campo. Transporte fluvial coordinado con la asociación.",
            "cantidad_inscritos": 18,
            "notificado": "",
        },
    ],
}


def _cargar_db() -> dict:
    """Carga (o inicializa con semilla) la base de datos local del modo demo."""
    if not _RUTA_DEMO.exists():
        _RUTA_DATA.mkdir(parents=True, exist_ok=True)
        _RUTA_DEMO.write_text(json.dumps(_SEMILLA_DEMO, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(_RUTA_DEMO.read_text(encoding="utf-8"))


def _guardar_db(db: dict) -> None:
    _RUTA_DEMO.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DATAVERSE
# ─────────────────────────────────────────────────────────────────────────────
def _a_cuerpo_dataverse(datos: dict) -> dict:
    """Convierte el payload de la API al cuerpo OData (enlaces_pdf → texto ';')."""
    cuerpo = {}
    for campo, columna in _CAMPOS_DV.items():
        if campo not in datos or datos[campo] is None:
            continue
        valor = datos[campo]
        if campo == "enlaces_pdf":
            valor = ";".join(valor)
        elif campo == "archivos":
            valor = json.dumps(valor, ensure_ascii=False)
        cuerpo[columna] = valor
    return cuerpo


def _desde_fila_dataverse(fila: dict) -> dict:
    """Convierte una fila OData al contrato de la API."""
    resultado = {"id": fila.get(_ID_DV)}
    for campo, columna in _CAMPOS_DV.items():
        valor = fila.get(columna)
        if campo == "enlaces_pdf":
            valor = [u for u in (valor or "").split(";") if u.strip()]
        elif campo == "archivos":
            try:
                valor = json.loads(valor) if valor else []
            except (TypeError, ValueError):
                valor = []
        elif campo in ("publicacion", "asignar_ficha", "gestion_ficha", "proceso_matricula"):
            valor = bool(valor)
        elif campo in ("duracion_horas", "cantidad_inscritos"):
            valor = valor or 0
        else:
            valor = valor or ""
        resultado[campo] = valor
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# ARCHIVOS SUBIDOS (matriz de la ficha, archivo plano, documento adicional)
# ─────────────────────────────────────────────────────────────────────────────
def _nombre_seguro(nombre: str) -> str:
    """Sanitiza el nombre del archivo: sin rutas ni caracteres peligrosos."""
    base = os.path.basename(nombre or "archivo")
    limpio = re.sub(r"[^\w.\- ]", "_", base).strip() or "archivo"
    return limpio[:120]


def _carpeta_solicitud(solicitud_id: str) -> Path:
    """Carpeta física de los archivos de una solicitud (se crea si no existe)."""
    carpeta = _RUTA_STORAGE / _nombre_seguro(solicitud_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def _escribir_archivo(carpeta: Path, campo: str, nombre: str, contenido: bytes) -> dict:
    """Escribe el archivo de un campo (un archivo por campo: reemplaza la versión
    anterior si existía) y devuelve sus metadatos {"campo", "nombre", "tamano"}."""
    if campo not in CAMPOS_ARCHIVO:
        raise HTTPException(status_code=422, detail=f"Tipo de archivo desconocido: {campo}.")
    nombre = _nombre_seguro(nombre)
    for viejo in carpeta.glob(f"{campo}__*"):
        viejo.unlink()
    (carpeta / f"{campo}__{nombre}").write_bytes(contenido)
    return {"campo": campo, "nombre": nombre, "tamano": len(contenido)}


async def guardar_archivos_solicitud(solicitud_id: str, archivos: list[dict]) -> list[dict]:
    """Guarda en disco los archivos de la solicitud y registra sus metadatos.
    Cada elemento de `archivos`: {"campo": matriz|plano|adicional, "nombre": str, "contenido": bytes}."""
    carpeta = _carpeta_solicitud(solicitud_id)
    meta = [_escribir_archivo(carpeta, a["campo"], a["nombre"], a["contenido"]) for a in archivos]
    await _registrar_archivos(solicitud_id, meta)
    return meta


async def agregar_archivo_solicitud(solicitud_id: str, campo: str, nombre: str, contenido: bytes) -> list[dict]:
    """Adjunta (o reemplaza) UN archivo de una solicitud existente conservando
    los demás. Lo usa el admin para el archivo de resultados de inscritos."""
    solicitud = await obtener_solicitud(solicitud_id)  # 404 si no existe
    nuevo = _escribir_archivo(_carpeta_solicitud(solicitud_id), campo, nombre, contenido)

    # Metadatos: se conservan los archivos existentes y se sustituye el del campo
    meta = [a for a in (solicitud.get("archivos") or []) if a.get("campo") != campo]
    meta.append(nuevo)
    await _registrar_archivos(solicitud_id, meta)
    return meta


async def _guardar_campos(solicitud_id: str, campos: dict, error_dataverse: str) -> None:
    """Persiste campos puntuales de una solicitud existente en el modo activo
    (JSON demo o PATCH a Dataverse). 404 si la solicitud no existe en demo."""
    if not dataverse_configurado():
        async with _demo_lock:
            db = _cargar_db()
            for sol in db["solicitudes"]:
                if sol["id"] == solicitud_id:
                    sol.update(campos)
                    _guardar_db(db)
                    return
            raise HTTPException(status_code=404, detail="La solicitud no existe.")

    # --- MODO DATAVERSE ---
    async with await cliente_dataverse() as client:
        res = await client.patch(
            f"{TABLA_COMPLEMENTARIAS}({solicitud_id})",
            json=_a_cuerpo_dataverse(campos),
        )
        if res.status_code != 204:
            raise HTTPException(status_code=400, detail=error_dataverse)


async def _registrar_archivos(solicitud_id: str, meta: list[dict]) -> None:
    """Persiste los metadatos de los archivos en el registro de la solicitud."""
    await _guardar_campos(
        solicitud_id, {"archivos": meta},
        "No se pudieron registrar los archivos en Dataverse.",
    )


def obtener_archivo(solicitud_id: str, campo: str) -> tuple[Path, str]:
    """Devuelve (ruta, nombre_original) del archivo pedido, o 404 si no existe."""
    if campo not in CAMPOS_ARCHIVO:
        raise HTTPException(status_code=422, detail=f"Tipo de archivo desconocido: {campo}.")
    carpeta = _RUTA_STORAGE / _nombre_seguro(solicitud_id)
    coincidencias = sorted(carpeta.glob(f"{campo}__*")) if carpeta.exists() else []
    if not coincidencias:
        raise HTTPException(status_code=404, detail="El archivo solicitado no existe en el servidor.")
    ruta = coincidencias[0]
    return ruta, ruta.name.split("__", 1)[1]


def _eliminar_archivos_solicitud(solicitud_id: str) -> None:
    """Borra la carpeta de archivos al eliminar la solicitud."""
    shutil.rmtree(_RUTA_STORAGE / _nombre_seguro(solicitud_id), ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUDES
# ─────────────────────────────────────────────────────────────────────────────
async def listar_solicitudes(
    estado: str | None = None,
    municipio: str | None = None,
    jornada: str | None = None,
    instructor: str | None = None,
    buscar: str | None = None,
    correo: str | None = None,
) -> list:
    """Solicitudes de formación complementaria con filtros opcionales."""
    if not dataverse_configurado():
        solicitudes = _cargar_db()["solicitudes"]
    else:
        # --- MODO DATAVERSE ---
        async with await cliente_dataverse() as client:
            columnas = ",".join([_ID_DV, *_CAMPOS_DV.values()])
            res = await client.get(f"{TABLA_COMPLEMENTARIAS}?$select={columnas}")
            if res.status_code != 200:
                print("ERROR DATAVERSE COMPLEMENTARIAS:", res.text)
                raise HTTPException(
                    status_code=res.status_code,
                    detail="Error al consultar las fichas complementarias en Dataverse.",
                )
            solicitudes = [_desde_fila_dataverse(f) for f in res.json().get("value", [])]

    # Filtros en memoria: el volumen es bajo (decenas de solicitudes por trimestre)
    # y así el contrato es idéntico en ambos modos.
    if estado:
        solicitudes = [s for s in solicitudes if s.get("estado") == estado]
    if municipio:
        solicitudes = [s for s in solicitudes if s.get("municipio") == municipio]
    if jornada:
        solicitudes = [s for s in solicitudes if s.get("jornada") == jornada]
    if instructor:
        solicitudes = [s for s in solicitudes if s.get("nombre_instructor") == instructor]
    if correo:
        # "Mis solicitudes" del instructor: comparación insensible a mayúsculas
        solicitudes = [s for s in solicitudes if (s.get("correo_instructor") or "").lower() == correo.lower()]
    if buscar:
        q = buscar.lower()
        solicitudes = [
            s for s in solicitudes
            if q in (s.get("nombre_programa") or "").lower()
            or q in (s.get("codigo_programa") or "").lower()
            or q in (s.get("codigo_ficha") or "").lower()
        ]
    return solicitudes


async def obtener_solicitud(solicitud_id: str) -> dict:
    """Una solicitud por su id (404 si no existe)."""
    if not dataverse_configurado():
        for s in _cargar_db()["solicitudes"]:
            if s["id"] == solicitud_id:
                return s
        raise HTTPException(status_code=404, detail="La solicitud no existe.")

    # --- MODO DATAVERSE ---
    async with await cliente_dataverse() as client:
        columnas = ",".join([_ID_DV, *_CAMPOS_DV.values()])
        res = await client.get(f"{TABLA_COMPLEMENTARIAS}({solicitud_id})?$select={columnas}")
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="La solicitud no existe en Dataverse.")
        return _desde_fila_dataverse(res.json())


async def _notificar_solicitud_pendiente(solicitud: dict) -> None:
    """Avisa al admin cuando un instructor envía una solicitud (estado Pendiente).
    Un fallo en la notificación NO debe tumbar la creación de la solicitud."""
    if solicitud.get("estado") != "Pendiente":
        return
    try:
        await notificaciones_service.crear_notificacion(
            destinatario="admin",
            tipo="solicitud_ficha",
            texto=(
                f"El instructor {solicitud.get('nombre_instructor', 'desconocido')} solicitó "
                f"la creación de una ficha complementaria: {solicitud.get('nombre_programa', '')}."
            ),
            ficha_relacionada=solicitud.get("id", ""),
        )
    except Exception as e:
        print("AVISO: la solicitud se creó pero falló la notificación al admin:", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# AVISO DE PUBLICACIÓN AL INSTRUCTOR (correo institucional + campana)
# ─────────────────────────────────────────────────────────────────────────────
def _correo_configurado() -> bool:
    """True si el .env tiene la cuenta SMTP para despachar correos."""
    return bool(os.getenv("SMTP_EMAIL") and os.getenv("SMTP_PASSWORD"))


def _enviar_correo_publicacion(solicitud: dict) -> None:
    """Correo institucional al instructor: su ficha quedó Publicada.
    SMTP es bloqueante: llamar siempre con asyncio.to_thread.
    Mismo despacho SSL (Gmail 465) que reportes_service."""
    def rango(inicio: str | None, fin: str | None) -> str:
        return f"del {inicio or 'por definir'} al {fin or 'por definir'}"

    msg = EmailMessage()
    msg["Subject"] = f"Ficha complementaria publicada — {solicitud.get('nombre_programa', '')}"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = solicitud.get("correo_instructor")
    cuerpo = (
        f"Cordial saludo, instructor(a) {solicitud.get('nombre_instructor', '')}.\n\n"
        "Su ficha de formación complementaria fue PUBLICADA y está disponible para ejecución.\n\n"
        f"  Programa: {solicitud.get('nombre_programa', '')} "
        f"(código {solicitud.get('codigo_programa', '')}, versión {solicitud.get('version_programa') or '1'})\n"
        f"  Código de ficha: {solicitud.get('codigo_ficha') or 'por asignar'}\n"
        f"  Inscripciones: {rango(solicitud.get('fecha_inicio_inscripcion'), solicitud.get('fecha_cierre_inscripcion'))}\n"
        f"  Formación: {rango(solicitud.get('fecha_inicio_formacion'), solicitud.get('fecha_fin_formacion'))}\n"
        f"  Jornada: {solicitud.get('jornada') or 'por definir'} · Municipio: {solicitud.get('municipio') or 'por definir'}\n\n"
        'Puede consultar el detalle en "Mis solicitudes" dentro de VoltMind Access.\n\n'
        "Mensaje automático de VoltMind — no responda a este correo."
    )
    msg.set_content(cuerpo, charset="utf-8")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        smtp.send_message(msg)


async def avisar_publicacion(solicitud: dict) -> dict:
    """Avisa al instructor que su ficha quedó Publicada por dos canales:
    notificación in-app (campana, destinatario = correo del instructor) y
    correo institucional. Actualiza la marca `notificado` (hora de Bogotá)."""
    correo = (solicitud.get("correo_instructor") or "").strip()
    if not correo:
        raise HTTPException(
            status_code=409,
            detail="La solicitud no tiene correo del instructor; regístrelo antes de enviar el aviso.",
        )

    # 1. Notificación in-app: llega a la campana de la vista del instructor
    await notificaciones_service.crear_notificacion(
        destinatario=correo.lower(),
        tipo="ficha_publicada",
        texto=(
            f'Su ficha complementaria "{solicitud.get("nombre_programa", "")}" fue publicada '
            "y está disponible para ejecución."
        ),
        ficha_relacionada=solicitud.get("id", ""),
    )

    # 2. Correo institucional (solo si el servidor tiene SMTP configurado)
    correo_enviado = False
    if _correo_configurado():
        await asyncio.to_thread(_enviar_correo_publicacion, solicitud)
        correo_enviado = True

    # 3. Marca de notificado para la tarjeta del admin ("Avisado el DD/MM")
    fecha = datetime.now(_ZONA_BOGOTA).isoformat(timespec="seconds")
    await _guardar_campos(
        solicitud["id"], {"notificado": fecha},
        "No se pudo registrar la marca de aviso en Dataverse.",
    )

    return {
        "notificado": fecha,
        "correo_enviado": correo_enviado,
        "mensaje": (
            f"Aviso enviado a {correo} por correo institucional y notificación interna."
            if correo_enviado
            else (
                f"Notificación interna enviada a {correo}. El correo no salió porque el servidor "
                "no tiene configurado SMTP_EMAIL/SMTP_PASSWORD."
            )
        ),
    }


async def _avisar_publicacion_sin_fallar(solicitud: dict) -> None:
    """El aviso automático no debe tumbar el cambio de estado (mismo criterio que
    _notificar_solicitud_pendiente). Si falla, la tarjeta queda "Pendiente de
    avisar" y el admin puede usar "Reenviar aviso"."""
    try:
        await avisar_publicacion(solicitud)
    except Exception as e:
        print("AVISO: la ficha quedó Publicada pero falló el aviso al instructor:", str(e))


async def crear_solicitud(datos: dict) -> dict:
    _validar_coherencia_fechas(datos)

    if not dataverse_configurado():
        async with _demo_lock:
            db = _cargar_db()
            _validar_ficha_duplicada(db["solicitudes"], datos)
            nueva = {
                "id": f"comp-{uuid.uuid4().hex[:8]}",
                **datos,
                "fecha_creacion": date.today().isoformat(),
                "notificado": "",
            }
            db["solicitudes"].append(nueva)
            _guardar_db(db)
        await _notificar_solicitud_pendiente(nueva)
        return nueva

    # --- MODO DATAVERSE ---
    existentes = await listar_solicitudes()
    _validar_ficha_duplicada(existentes, datos)
    async with await cliente_dataverse() as client:
        cuerpo = _a_cuerpo_dataverse({**datos, "fecha_creacion": date.today().isoformat()})
        res = await client.post(TABLA_COMPLEMENTARIAS, json=cuerpo)
        if res.status_code != 204:
            print("ERROR DATAVERSE CREAR COMPLEMENTARIA:", res.text)
            raise HTTPException(status_code=400, detail="No se pudo crear la solicitud en Dataverse.")
        entity_url = res.headers.get("OData-EntityId", "")
        nuevo_id = entity_url.split("(")[-1].replace(")", "") if "(" in entity_url else ""
        nueva = {"id": nuevo_id, **datos}
    await _notificar_solicitud_pendiente(nueva)
    return nueva


async def actualizar_solicitud(solicitud_id: str, datos: dict) -> dict:
    if not dataverse_configurado():
        actualizada = None
        estado_anterior = None
        cambios = {k: v for k, v in datos.items() if v is not None}
        async with _demo_lock:
            db = _cargar_db()
            for sol in db["solicitudes"]:
                if sol["id"] == solicitud_id:
                    combinada = {**sol, **cambios}
                    _validar_coherencia_fechas(combinada)
                    _validar_ficha_duplicada(db["solicitudes"], combinada, excluir_id=solicitud_id)
                    estado_anterior = sol.get("estado")
                    sol.update(cambios)
                    _guardar_db(db)
                    actualizada = dict(sol)
                    break
            if actualizada is None:
                raise HTTPException(status_code=404, detail="La solicitud no existe.")
        # Fuera del lock: el aviso vuelve a entrar a la persistencia (marca `notificado`)
        if actualizada.get("estado") == "Publicada" and estado_anterior != "Publicada":
            await _avisar_publicacion_sin_fallar(actualizada)
        return actualizada

    # --- MODO DATAVERSE ---
    _validar_coherencia_fechas(datos)
    if datos.get("codigo_ficha"):
        existentes = await listar_solicitudes()
        _validar_ficha_duplicada(existentes, datos, excluir_id=solicitud_id)
    # Para detectar la transición a "Publicada" se necesita el estado previo
    previa = await obtener_solicitud(solicitud_id) if datos.get("estado") == "Publicada" else None
    async with await cliente_dataverse() as client:
        cuerpo = _a_cuerpo_dataverse(datos)
        res = await client.patch(f"{TABLA_COMPLEMENTARIAS}({solicitud_id})", json=cuerpo)
        if res.status_code != 204:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la solicitud en Dataverse.")
    if previa is not None and previa.get("estado") != "Publicada":
        await _avisar_publicacion_sin_fallar({**previa, **datos, "id": solicitud_id})
    return {"id": solicitud_id, **datos}


async def eliminar_solicitud(solicitud_id: str) -> dict:
    if not dataverse_configurado():
        async with _demo_lock:
            db = _cargar_db()
            antes = len(db["solicitudes"])
            db["solicitudes"] = [s for s in db["solicitudes"] if s["id"] != solicitud_id]
            if len(db["solicitudes"]) == antes:
                raise HTTPException(status_code=404, detail="La solicitud no existe.")
            _guardar_db(db)
        _eliminar_archivos_solicitud(solicitud_id)
        return {"mensaje": "Solicitud eliminada con éxito."}

    # --- MODO DATAVERSE ---
    async with await cliente_dataverse() as client:
        res = await client.delete(f"{TABLA_COMPLEMENTARIAS}({solicitud_id})")
        if res.status_code != 204:
            raise HTTPException(status_code=400, detail="No se pudo eliminar la solicitud en Dataverse.")
    _eliminar_archivos_solicitud(solicitud_id)
    return {"mensaje": "Solicitud eliminada con éxito."}


# ─────────────────────────────────────────────────────────────────────────────
# INDICADORES (cabecera de la sección)
# ─────────────────────────────────────────────────────────────────────────────
async def obtener_indicadores() -> dict:
    """Totales por estado e inscritos, para los contadores de la vista."""
    solicitudes = await listar_solicitudes()
    por_estado = {e: 0 for e in ESTADOS_SOLICITUD}
    for s in solicitudes:
        if s.get("estado") in por_estado:
            por_estado[s["estado"]] += 1
    return {
        "total": len(solicitudes),
        "pendientes": por_estado["Pendiente"],
        "publicadas": por_estado["Publicada"],
        "en_ejecucion": por_estado["En Ejecución"],
        "canceladas": por_estado["Cancelada"],
        "inscritos_total": sum(s.get("cantidad_inscritos") or 0 for s in solicitudes),
        "modo_demo": not dataverse_configurado(),
    }
