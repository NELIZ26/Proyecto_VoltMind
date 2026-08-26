# services/tituladas_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Módulo de Fichas Tituladas y Asignación de Ambientes.
#
# Digitaliza las matrices de Excel de la programación académica del coordinador:
#   · Matriz por ficha  → calendario de asignaciones de cada ficha.
#   · Matriz por instructor → se calcula automáticamente desde las asignaciones.
#   · Ambientes → la misma asignación reserva el ambiente en su jornada.
#
# Una ASIGNACIÓN equivale a pintar un rango de celdas en el Excel:
#   instructor + competencia + ambiente + rango de días (jornada = la de la ficha).
# Las horas se calculan como días hábiles (lunes a viernes) × 6 h del bloque.
#
# MODO DE DATOS: por ahora persiste en backend/data/tituladas_demo.json (semilla
# incluida; borrar el JSON la restaura). Las tablas de Dataverse de este módulo
# aún NO existen: cuando se creen, implementar la rama Dataverse y activarla con
# la variable de entorno TITULADAS_MODO=dataverse (hoy responde 501).
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import json
import uuid
import asyncio
from calendar import monthrange
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import HTTPException

# ── Reglas institucionales SENA ──
HORAS_POR_DIA = 6            # cada jornada es un bloque fijo de 6 horas
META_PROGRAMACION = 70       # % ideal de horas del programa a programar
META_TECNICA = 60            # % mínimo de horas técnicas sobre lo programado
LIMITES_MENSUALES = {"Contratista": 160, "Planta": 128}  # formación directa/mes

_MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

_RUTA_DATA = Path(__file__).resolve().parent.parent / "data"
_RUTA_DEMO = _RUTA_DATA / "tituladas_demo.json"

# Respaldo de los Excel históricos de cada ficha (adjuntos descargables)
_RUTA_STORAGE = Path(__file__).resolve().parent.parent / "storage" / "tituladas"

# Serializa los ciclos cargar-validar-guardar del modo demo
_demo_lock = asyncio.Lock()

_ZONA_BOGOTA = ZoneInfo("America/Bogota")


def _es_demo() -> bool:
    """Las tablas de Dataverse de tituladas aún no existen: demo salvo que se
    active explícitamente TITULADAS_MODO=dataverse (rama pendiente de construir)."""
    return os.getenv("TITULADAS_MODO", "demo").lower() != "dataverse"


def _exigir_demo() -> None:
    if not _es_demo():
        raise HTTPException(
            status_code=501,
            detail=(
                "El modo Dataverse de Fichas Tituladas aún no está disponible: "
                "primero deben crearse las tablas (ver docs/DATAVERSE_TABLAS.md). "
                "Quite TITULADAS_MODO=dataverse del .env para usar el modo demo."
            ),
        )


# ─────────────────────────────────────────────────────────────────────────────
# FECHAS Y HORAS (días hábiles lunes-viernes × bloque de 6 h)
# ─────────────────────────────────────────────────────────────────────────────
def _fecha(valor: str) -> date:
    return date.fromisoformat(valor[:10])


def _dias_habiles(inicio: date, fin: date) -> int:
    """Cantidad de días lunes-viernes dentro del rango (ambos incluidos)."""
    dias, dia = 0, inicio
    while dia <= fin:
        if dia.weekday() < 5:
            dias += 1
        dia += timedelta(days=1)
    return dias


def _horas_rango(inicio: date, fin: date) -> int:
    return _dias_habiles(inicio, fin) * HORAS_POR_DIA


def _solapan(a_inicio: date, a_fin: date, b_inicio: date, b_fin: date) -> bool:
    return a_inicio <= b_fin and b_inicio <= a_fin


def _horas_en_mes(asignacion: dict, anio: int, mes: int) -> int:
    """Horas de la asignación que caen dentro del mes indicado (para la carga mensual)."""
    inicio = _fecha(asignacion["fecha_inicio"])
    fin = _fecha(asignacion["fecha_fin"])
    mes_inicio = date(anio, mes, 1)
    mes_fin = date(anio, mes, monthrange(anio, mes)[1])
    desde, hasta = max(inicio, mes_inicio), min(fin, mes_fin)
    if desde > hasta:
        return 0
    return _horas_rango(desde, hasta)


def _formatear(fecha_iso: str) -> str:
    """DD/MM/YYYY para los mensajes de error legibles por el coordinador."""
    try:
        return _fecha(fecha_iso).strftime("%d/%m/%Y")
    except ValueError:
        return fecha_iso


# ─────────────────────────────────────────────────────────────────────────────
# MODO DEMO — Persistencia local en JSON (semilla con el caso real del relato
# del coordinador: ficha de programas deportivos, inducción de J.I.R., etc.)
# ─────────────────────────────────────────────────────────────────────────────
_SEMILLA_DEMO = {
    # Catálogo de programas: la matriz de competencias (diagnóstico) de una ficha
    # nueva se genera copiando la del programa elegido.
    "programas": [
        {
            "id": "prog-deportes", "nombre": "Ejecución de Programas Deportivos",
            "version": "1", "nivel": "Técnico",
            "competencias": [
                {"nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"nombre": "Entrenar deportistas según plan de trabajo", "tipo": "Técnica", "horas": 220},
                {"nombre": "Asistir personas de acuerdo con guías de atención", "tipo": "Técnica", "horas": 120},
                {"nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"nombre": "Derechos fundamentales del trabajo", "tipo": "Básica", "horas": 48},
                {"nombre": "Ambiental y seguridad", "tipo": "Transversal", "horas": 48},
                {"nombre": "Comunicación", "tipo": "Básica", "horas": 48},
                {"nombre": "Emprendimiento", "tipo": "Básica", "horas": 48},
                {"nombre": "Deportes y actividad física", "tipo": "Transversal", "horas": 48},
                {"nombre": "Idiomas (inglés)", "tipo": "Básica", "horas": 120},
            ],
        },
        {
            "id": "prog-adso", "nombre": "Análisis y Desarrollo de Software",
            "version": "1", "nivel": "Tecnólogo",
            "competencias": [
                {"nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"nombre": "Desarrollar el software según el diseño", "tipo": "Técnica", "horas": 380},
                {"nombre": "Implementar redes de datos", "tipo": "Técnica", "horas": 140},
                {"nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"nombre": "Comunicación", "tipo": "Básica", "horas": 48},
                {"nombre": "Idiomas (inglés)", "tipo": "Básica", "horas": 320},
            ],
        },
        {
            "id": "prog-cocina", "nombre": "Preparación de Alimentos",
            "version": "1", "nivel": "Técnico",
            "competencias": [
                {"nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"nombre": "Preparar alimentos según estándares", "tipo": "Técnica", "horas": 260},
                {"nombre": "Higiene y manipulación de alimentos", "tipo": "Técnica", "horas": 80},
                {"nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"nombre": "Deportes y actividad física", "tipo": "Transversal", "horas": 48},
            ],
        },
    ],
    "instructores": [
        {
            "id": "inst-jir", "nombre": "Jorge Iván Rivas", "iniciales": "J.I.R.",
            "correo": "jrivas@sena.edu.co", "tipo_vinculacion": "Contratista",
            "fin_contrato": "2026-08-31", "color": "#E67E22",
            "perfil": ["Entrenamiento deportivo", "Actividad física", "Inducción"],
        },
        {
            "id": "inst-slo", "nombre": "Sandra Londoño", "iniciales": "S.L.",
            "correo": "slondono@sena.edu.co", "tipo_vinculacion": "Planta",
            "fin_contrato": "", "color": "#8E44AD",
            "perfil": ["Ética y cultura de paz", "Comunicación"],
        },
        {
            "id": "inst-rer", "nombre": "Robert Erazo", "iniciales": "R.E.",
            "correo": "rerazo@sena.edu.co", "tipo_vinculacion": "Contratista",
            "fin_contrato": "2026-12-31", "color": "#2980B9",
            "perfil": ["Derechos fundamentales del trabajo", "Emprendimiento", "Deportes"],
        },
        {
            "id": "inst-dmu", "nombre": "Diana Muñoz", "iniciales": "D.M.",
            "correo": "dmunoz@sena.edu.co", "tipo_vinculacion": "Contratista",
            "fin_contrato": "2026-12-31", "color": "#C0392B",
            "perfil": ["Comunicación", "Ética y cultura de paz"],
        },
        {
            "id": "inst-mgo", "nombre": "Marlon González", "iniciales": "M.G.",
            "correo": "mgonzalez@sena.edu.co", "tipo_vinculacion": "Contratista",
            "fin_contrato": "2027-01-31", "color": "#16A085",
            "perfil": ["Desarrollo de software", "Redes de datos"],
        },
        {
            "id": "inst-cpe", "nombre": "Carlos Peña", "iniciales": "C.P.",
            "correo": "cpena@sena.edu.co", "tipo_vinculacion": "Contratista",
            "fin_contrato": "2026-10-30", "color": "#B7950B",
            "perfil": ["Cocina", "Manipulación de alimentos"],
        },
    ],
    "ambientes": [
        {"id": "amb-101", "nombre": "Aula 101", "sede": "Principal Puerto Asís", "capacidad": 30, "tipo": "Aula"},
        {"id": "amb-102", "nombre": "Aula 102", "sede": "Principal Puerto Asís", "capacidad": 28, "tipo": "Aula"},
        {"id": "amb-cancha", "nombre": "Cancha Deportiva", "sede": "Principal Puerto Asís", "capacidad": 35, "tipo": "Campo deportivo"},
        {"id": "amb-sistemas", "nombre": "Sala de Sistemas (Lego)", "sede": "Principal Puerto Asís", "capacidad": 25, "tipo": "Laboratorio"},
        {"id": "amb-biblio", "nombre": "Biblioteca", "sede": "Principal Puerto Asís", "capacidad": 40, "tipo": "Biblioteca"},
        {"id": "amb-cocina", "nombre": "Taller de Cocina", "sede": "Santa Teresa", "capacidad": 20, "tipo": "Taller"},
        {"id": "amb-biling", "nombre": "Aula de Bilingüismo", "sede": "Puerto Caicedo", "capacidad": 30, "tipo": "Aula"},
    ],
    "fichas": [
        {
            "id": "fic-deportes", "codigo": "3411495",
            "programa": "Ejecución de Programas Deportivos", "nivel": "Técnico",
            "jornada": "Mañana", "sede": "Principal Puerto Asís", "municipio": "Puerto Asís",
            "instructor_titular_id": "inst-jir",
            "fecha_inicio": "2026-03-05", "fecha_fin": "2026-12-04",
            "numero_aprendices": 25,
            "competencias": [
                {"id": "f1-c1", "nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"id": "f1-c2", "nombre": "Entrenar deportistas según plan de trabajo", "tipo": "Técnica", "horas": 220},
                {"id": "f1-c3", "nombre": "Asistir personas de acuerdo con guías de atención", "tipo": "Técnica", "horas": 120},
                {"id": "f1-c4", "nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"id": "f1-c5", "nombre": "Derechos fundamentales del trabajo", "tipo": "Básica", "horas": 48},
                {"id": "f1-c6", "nombre": "Ambiental y seguridad", "tipo": "Transversal", "horas": 48},
                {"id": "f1-c7", "nombre": "Comunicación", "tipo": "Básica", "horas": 48},
                {"id": "f1-c8", "nombre": "Emprendimiento", "tipo": "Básica", "horas": 48},
                {"id": "f1-c9", "nombre": "Deportes y actividad física", "tipo": "Transversal", "horas": 48},
                {"id": "f1-c10", "nombre": "Idiomas (inglés)", "tipo": "Básica", "horas": 120},
            ],
        },
        {
            "id": "fic-adso", "codigo": "3455872",
            "programa": "Análisis y Desarrollo de Software", "nivel": "Tecnólogo",
            "jornada": "Tarde", "sede": "Principal Puerto Asís", "municipio": "Puerto Asís",
            "instructor_titular_id": "inst-mgo",
            "fecha_inicio": "2026-07-21", "fecha_fin": "2028-06-20",
            "numero_aprendices": 28,
            "competencias": [
                {"id": "f2-c1", "nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"id": "f2-c2", "nombre": "Desarrollar el software según el diseño", "tipo": "Técnica", "horas": 380},
                {"id": "f2-c3", "nombre": "Implementar redes de datos", "tipo": "Técnica", "horas": 140},
                {"id": "f2-c4", "nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"id": "f2-c5", "nombre": "Comunicación", "tipo": "Básica", "horas": 48},
                {"id": "f2-c6", "nombre": "Idiomas (inglés)", "tipo": "Básica", "horas": 320},
            ],
        },
        {
            "id": "fic-cocina", "codigo": "3467210",
            "programa": "Preparación de Alimentos", "nivel": "Técnico",
            "jornada": "Noche", "sede": "Santa Teresa", "municipio": "Puerto Asís",
            "instructor_titular_id": "inst-cpe",
            "fecha_inicio": "2026-07-06", "fecha_fin": "2027-04-05",
            "numero_aprendices": 20,
            "competencias": [
                {"id": "f3-c1", "nombre": "Inducción", "tipo": "Inducción", "horas": 30},
                {"id": "f3-c2", "nombre": "Preparar alimentos según estándares", "tipo": "Técnica", "horas": 260},
                {"id": "f3-c3", "nombre": "Higiene y manipulación de alimentos", "tipo": "Técnica", "horas": 80},
                {"id": "f3-c4", "nombre": "Ética y cultura de paz", "tipo": "Transversal", "horas": 48},
                {"id": "f3-c5", "nombre": "Deportes y actividad física", "tipo": "Transversal", "horas": 48},
            ],
        },
    ],
    # Las horas de cada asignación salen de días hábiles × 6 (las de marzo
    # reproducen el caso real: 30 h de inducción, 42 h técnicas y 36 h de ética).
    "asignaciones": [
        {"id": "asig-01", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c1",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-03-05", "fecha_fin": "2026-03-11", "horas": 30},
        {"id": "asig-02", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c2",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-03-12", "fecha_fin": "2026-03-20", "horas": 42},
        {"id": "asig-03", "ficha_id": "fic-deportes", "instructor_id": "inst-slo", "competencia_id": "f1-c4",
         "ambiente_id": "amb-101", "fecha_inicio": "2026-03-24", "fecha_fin": "2026-03-31", "horas": 36},
        {"id": "asig-04", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c2",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-04-01", "fecha_fin": "2026-04-17", "horas": 78},
        {"id": "asig-05", "ficha_id": "fic-deportes", "instructor_id": "inst-rer", "competencia_id": "f1-c5",
         "ambiente_id": "amb-101", "fecha_inicio": "2026-04-20", "fecha_fin": "2026-04-24", "horas": 30},
        {"id": "asig-06", "ficha_id": "fic-deportes", "instructor_id": "inst-dmu", "competencia_id": "f1-c7",
         "ambiente_id": "amb-101", "fecha_inicio": "2026-04-27", "fecha_fin": "2026-04-30", "horas": 24},
        {"id": "asig-07", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c3",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-05-04", "fecha_fin": "2026-05-15", "horas": 60},
        {"id": "asig-08", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c2",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-14", "horas": 60},
        {"id": "asig-09", "ficha_id": "fic-deportes", "instructor_id": "inst-rer", "competencia_id": "f1-c8",
         "ambiente_id": "amb-101", "fecha_inicio": "2026-08-18", "fecha_fin": "2026-08-21", "horas": 24},
        {"id": "asig-10", "ficha_id": "fic-deportes", "instructor_id": "inst-jir", "competencia_id": "f1-c3",
         "ambiente_id": "amb-cancha", "fecha_inicio": "2026-08-24", "fecha_fin": "2026-08-28", "horas": 30},
        {"id": "asig-11", "ficha_id": "fic-adso", "instructor_id": "inst-mgo", "competencia_id": "f2-c1",
         "ambiente_id": "amb-sistemas", "fecha_inicio": "2026-07-21", "fecha_fin": "2026-07-27", "horas": 30},
        {"id": "asig-12", "ficha_id": "fic-adso", "instructor_id": "inst-mgo", "competencia_id": "f2-c2",
         "ambiente_id": "amb-sistemas", "fecha_inicio": "2026-07-28", "fecha_fin": "2026-08-21", "horas": 114},
        {"id": "asig-13", "ficha_id": "fic-adso", "instructor_id": "inst-dmu", "competencia_id": "f2-c4",
         "ambiente_id": "amb-sistemas", "fecha_inicio": "2026-08-24", "fecha_fin": "2026-08-28", "horas": 30},
        {"id": "asig-14", "ficha_id": "fic-cocina", "instructor_id": "inst-cpe", "competencia_id": "f3-c1",
         "ambiente_id": "amb-cocina", "fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10", "horas": 30},
        {"id": "asig-15", "ficha_id": "fic-cocina", "instructor_id": "inst-slo", "competencia_id": "f3-c4",
         "ambiente_id": "amb-cocina", "fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-17", "horas": 30},
        {"id": "asig-16", "ficha_id": "fic-cocina", "instructor_id": "inst-rer", "competencia_id": "f3-c5",
         "ambiente_id": "amb-cocina", "fecha_inicio": "2026-07-20", "fecha_fin": "2026-07-24", "horas": 30},
    ],
}


def _cargar_db() -> dict:
    """Carga (o inicializa con semilla) la base de datos local del modo demo."""
    if not _RUTA_DEMO.exists():
        _RUTA_DATA.mkdir(parents=True, exist_ok=True)
        _RUTA_DEMO.write_text(json.dumps(_SEMILLA_DEMO, ensure_ascii=False, indent=2), encoding="utf-8")
    db = json.loads(_RUTA_DEMO.read_text(encoding="utf-8"))
    # Compatibilidad con archivos demo creados antes del catálogo y los adjuntos
    db.setdefault("programas", _SEMILLA_DEMO["programas"])
    for f in db.get("fichas", []):
        f.setdefault("archivos", [])
    return db


def _guardar_db(db: dict) -> None:
    _RUTA_DEMO.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# BÚSQUEDAS Y ENRIQUECIMIENTO
# ─────────────────────────────────────────────────────────────────────────────
def _buscar(coleccion: list, elemento_id: str, nombre: str) -> dict:
    for item in coleccion:
        if item["id"] == elemento_id:
            return item
    raise HTTPException(status_code=404, detail=f"{nombre} no existe.")


def _competencia_de(ficha: dict, competencia_id: str) -> dict:
    for c in ficha.get("competencias", []):
        if c["id"] == competencia_id:
            return c
    raise HTTPException(
        status_code=404,
        detail=f"La competencia seleccionada no pertenece al programa de la ficha {ficha['codigo']}.",
    )


def _resumen_instructor(instructor: dict) -> dict:
    return {
        "id": instructor["id"], "nombre": instructor["nombre"],
        "iniciales": instructor["iniciales"], "color": instructor["color"],
    }


def _enriquecer_asignacion(a: dict, db: dict) -> dict:
    """Agrega a la asignación los datos que la UI necesita para pintar el calendario."""
    ficha = next((f for f in db["fichas"] if f["id"] == a["ficha_id"]), {})
    instructor = next((i for i in db["instructores"] if i["id"] == a["instructor_id"]), None)
    ambiente = next((am for am in db["ambientes"] if am["id"] == a["ambiente_id"]), None)
    competencia = next((c for c in ficha.get("competencias", []) if c["id"] == a["competencia_id"]), None)
    return {
        **a,
        "jornada": ficha.get("jornada", ""),
        "ficha_codigo": ficha.get("codigo", ""),
        "ficha_programa": ficha.get("programa", ""),
        "instructor": _resumen_instructor(instructor) if instructor else None,
        "competencia": ({"id": competencia["id"], "nombre": competencia["nombre"], "tipo": competencia["tipo"]}
                        if competencia else None),
        "ambiente": ({"id": ambiente["id"], "nombre": ambiente["nombre"], "sede": ambiente["sede"]}
                     if ambiente else None),
    }


def _resumen_programacion(ficha: dict, asignaciones: list) -> dict:
    """Indicadores de la ficha: % programado (meta 70 %) y % técnico (mínimo 60 %)."""
    propias = [a for a in asignaciones if a["ficha_id"] == ficha["id"]]
    total_programa = sum(c["horas"] for c in ficha.get("competencias", []))
    horas_programadas = sum(a["horas"] for a in propias)
    tipos = {c["id"]: c["tipo"] for c in ficha.get("competencias", [])}
    horas_tecnicas = sum(a["horas"] for a in propias if tipos.get(a["competencia_id"]) == "Técnica")
    porcentaje = round(horas_programadas / total_programa * 100) if total_programa else 0
    porcentaje_tecnica = round(horas_tecnicas / horas_programadas * 100) if horas_programadas else 0
    return {
        "total_horas_programa": total_programa,
        "horas_programadas": horas_programadas,
        "porcentaje_programacion": porcentaje,
        "porcentaje_tecnica": porcentaje_tecnica,
        "alerta_tecnica": horas_programadas > 0 and porcentaje_tecnica < META_TECNICA,
        "bajo_meta": porcentaje < META_PROGRAMACION,
    }


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIONES DE NEGOCIO (todas responden 409 con mensaje claro en español)
# ─────────────────────────────────────────────────────────────────────────────
def _exigir_diagnostico(ficha: dict) -> None:
    """El flujo real arranca con la matriz de competencias: sin diagnóstico
    registrado la ficha no se puede programar."""
    if not ficha.get("competencias"):
        raise HTTPException(
            status_code=409,
            detail=f"La ficha {ficha['codigo']} no tiene diagnóstico de competencias registrado. "
                   "Registre primero la matriz de competencias (diagnóstico) para poder programarla.",
        )


def _meses_del_rango(inicio: date, fin: date) -> list:
    """Pares (año, mes) que toca el rango, para validar el tope mensual."""
    meses, (a, m) = [], (inicio.year, inicio.month)
    while (a, m) <= (fin.year, fin.month):
        meses.append((a, m))
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return meses


def _validar_asignacion(db: dict, datos: dict, excluir_id: str | None = None) -> int:
    """Aplica todas las reglas y devuelve las horas del rango. Lanza 404/409."""
    ficha = _buscar(db["fichas"], datos["ficha_id"], "La ficha titulada")
    instructor = _buscar(db["instructores"], datos["instructor_id"], "El instructor")
    ambiente = _buscar(db["ambientes"], datos["ambiente_id"], "El ambiente")
    _exigir_diagnostico(ficha)
    _competencia_de(ficha, datos["competencia_id"])

    # El ambiente debe pertenecer a la sede de la ficha
    if ambiente.get("sede") and ficha.get("sede") and ambiente["sede"] != ficha["sede"]:
        raise HTTPException(
            status_code=409,
            detail=f"El ambiente {ambiente['nombre']} pertenece a la sede {ambiente['sede']} "
                   f"y la ficha {ficha['codigo']} es de la sede {ficha['sede']}: "
                   "elija un ambiente de la misma sede.",
        )

    inicio, fin = _fecha(datos["fecha_inicio"]), _fecha(datos["fecha_fin"])
    if fin < inicio:
        raise HTTPException(
            status_code=409,
            detail=f"La fecha final ({_formatear(datos['fecha_fin'])}) no puede ser anterior "
                   f"a la inicial ({_formatear(datos['fecha_inicio'])}).",
        )

    horas = _horas_rango(inicio, fin)
    if horas == 0:
        raise HTTPException(
            status_code=409,
            detail="El rango seleccionado no contiene días hábiles (lunes a viernes): no suma horas de formación.",
        )

    # Dentro del período lectivo de la ficha
    if ficha.get("fecha_inicio") and inicio < _fecha(ficha["fecha_inicio"]):
        raise HTTPException(
            status_code=409,
            detail=f"La ficha {ficha['codigo']} inicia el {_formatear(ficha['fecha_inicio'])}: "
                   "no se puede programar antes de esa fecha.",
        )
    if ficha.get("fecha_fin") and fin > _fecha(ficha["fecha_fin"]):
        raise HTTPException(
            status_code=409,
            detail=f"La ficha {ficha['codigo']} termina su etapa lectiva el {_formatear(ficha['fecha_fin'])}: "
                   "no se puede programar después de esa fecha.",
        )

    # Contrato del instructor vigente durante todo el rango
    if instructor.get("fin_contrato") and fin > _fecha(instructor["fin_contrato"]):
        raise HTTPException(
            status_code=409,
            detail=f"El contrato de {instructor['nombre']} vence el {_formatear(instructor['fin_contrato'])}: "
                   "no se puede programar más allá de esa fecha.",
        )

    fichas_por_id = {f["id"]: f for f in db["fichas"]}
    for otra in db["asignaciones"]:
        if otra["id"] == excluir_id:
            continue
        if not _solapan(inicio, fin, _fecha(otra["fecha_inicio"]), _fecha(otra["fecha_fin"])):
            continue
        ficha_otra = fichas_por_id.get(otra["ficha_id"], {})

        # 1. La misma ficha no puede tener dos asignaciones en las mismas fechas
        if otra["ficha_id"] == ficha["id"]:
            quien = next((i["nombre"] for i in db["instructores"] if i["id"] == otra["instructor_id"]), "otro instructor")
            raise HTTPException(
                status_code=409,
                detail=f"La ficha {ficha['codigo']} ya tiene programado a {quien} del "
                       f"{_formatear(otra['fecha_inicio'])} al {_formatear(otra['fecha_fin'])}. "
                       "Elija fechas que no se crucen.",
            )

        # Los cruces entre fichas solo aplican si comparten jornada (mismo bloque de 6 h)
        if ficha_otra.get("jornada") != ficha.get("jornada"):
            continue

        # 2. Cruce del instructor con otra ficha en la misma jornada
        if otra["instructor_id"] == instructor["id"]:
            raise HTTPException(
                status_code=409,
                detail=f"{instructor['nombre']} ya está ocupado en la jornada {ficha['jornada']} con la ficha "
                       f"{ficha_otra.get('codigo', '')} ({ficha_otra.get('programa', '')}) del "
                       f"{_formatear(otra['fecha_inicio'])} al {_formatear(otra['fecha_fin'])}.",
            )

        # 3. Cruce del ambiente con otra ficha en la misma jornada
        if otra["ambiente_id"] == datos["ambiente_id"]:
            raise HTTPException(
                status_code=409,
                detail=f"El ambiente {ambiente.get('nombre', '')} ya está reservado en la jornada "
                       f"{ficha['jornada']} por la ficha {ficha_otra.get('codigo', '')} del "
                       f"{_formatear(otra['fecha_inicio'])} al {_formatear(otra['fecha_fin'])}.",
            )

    # Tope MENSUAL de formación directa (160 h contratista / 128 h planta)
    limite = LIMITES_MENSUALES.get(instructor.get("tipo_vinculacion"), 160)
    nueva = {"fecha_inicio": datos["fecha_inicio"], "fecha_fin": datos["fecha_fin"]}
    for anio_mes, num_mes in _meses_del_rango(inicio, fin):
        horas_nuevas = _horas_en_mes(nueva, anio_mes, num_mes)
        if not horas_nuevas:
            continue
        existentes = sum(
            _horas_en_mes(a, anio_mes, num_mes)
            for a in db["asignaciones"]
            if a["instructor_id"] == instructor["id"] and a["id"] != excluir_id
        )
        if existentes + horas_nuevas > limite:
            raise HTTPException(
                status_code=409,
                detail=f"{instructor['nombre']} quedaría con {existentes + horas_nuevas} h en "
                       f"{_MESES_ES[num_mes - 1]} de {anio_mes} y su límite mensual es {limite} h "
                       f"({instructor.get('tipo_vinculacion', 'Contratista')}). "
                       "Reduzca el rango o reparta la programación con otro instructor.",
            )
    return horas


# ─────────────────────────────────────────────────────────────────────────────
# FICHAS
# ─────────────────────────────────────────────────────────────────────────────
async def listar_fichas(buscar: str | None = None, jornada: str | None = None, sede: str | None = None) -> list:
    """Listado de fichas tituladas con su % de programación calculado."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        # Traer todas las fichas
        res = await consultar_dataverse("cr6a3_fichas?$expand=cr6a3_ProgramaId")
        fichas_db = res.get("value", [])
        
        # Traer todas las competencias y asignaciones para calcular el progreso de las fichas
        import asyncio
        res_comps_task = consultar_dataverse("cr6a3_competenciafichas?$select=cr6a3_horas,_cr6a3_fichaid_value,cr6a3_tipo")
        res_asig_task = consultar_dataverse("cr6a3_asignacioneses?$select=cr6a3_horas,_cr6a3_fichaid_value,_cr6a3_competenciafichaid_value")
        res_inst_task = listar_instructores()
        
        res_comps, res_asig, instructores_list = await asyncio.gather(res_comps_task, res_asig_task, res_inst_task)
        instructores_dict = {i["id"]: i for i in instructores_list}
        
        # Agrupar por ficha
        from collections import defaultdict
        
        comps_por_ficha = defaultdict(list)
        for c in res_comps.get("value", []):
            fid = (c.get("_cr6a3_fichaid_value") or "").lower()
            if fid:
                comps_por_ficha[fid].append(c)
                
        asig_por_ficha = defaultdict(list)
        for a in res_asig.get("value", []):
            fid = (a.get("_cr6a3_fichaid_value") or "").lower()
            if fid:
                asig_por_ficha[fid].append(a)

        fichas_mapeadas = []
        for f in fichas_db:
            if jornada and f.get("cr6a3_jornada") != jornada:
                continue
            if sede and f.get("cr6a3_sede") != sede:
                continue
            
            codigo = f.get("cr6a3_numero_ficha", "")
            programa = f.get("cr6a3_nombre_programa", "")
            
            if buscar:
                q = buscar.lower()
                if q not in codigo.lower() and q not in programa.lower():
                    continue

            ficha_id_key = next((k for k in f.keys() if k.startswith("cr6a3_") and k.endswith("id")), "cr6a3_fichaid")
            fid = f.get(ficha_id_key)
            fid_lower = (fid or "").lower()
            
            # Calcular horas de competencias
            comps_ficha = comps_por_ficha[fid_lower]
            total_horas = sum(c.get("cr6a3_horas", 0) for c in comps_ficha)
            horas_tecnicas = sum(c.get("cr6a3_horas", 0) for c in comps_ficha if c.get("cr6a3_tipo") == "Técnica")
            
            # Calcular horas de asignaciones
            asig_ficha = asig_por_ficha[fid_lower]
            horas_prog = sum(a.get("cr6a3_horas", 0) for a in asig_ficha)
            
            # De las asignaciones, ¿cuáles son técnicas?
            # En Dataverse el id de competencia está en _cr6a3_competenciafichaid_value o _cr6a3_competenciaid_value
            horas_tecnicas_prog = 0
            for a in asig_ficha:
                cid = a.get("_cr6a3_competenciafichaid_value") or a.get("_cr6a3_competenciaid_value", "")
                # Buscar si esta competencia es "Técnica"
                comp = next((c for c in comps_ficha if c.get("cr6a3_competenciafichaid") == cid), None)
                if comp and comp.get("cr6a3_tipo") == "Técnica":
                    horas_tecnicas_prog += a.get("cr6a3_horas", 0)
            
            pct_prog = round((horas_prog / total_horas * 100)) if total_horas > 0 else 0
            pct_tec = round((horas_tecnicas_prog / horas_tecnicas * 100)) if horas_tecnicas > 0 else 0
            
            titular_id = f.get("_cr6a3_instructorasignado_value")
            
            tiene_diagnostico = len(comps_ficha) > 0
            map_nivel_inv = {
                430120000: "Tecnólogo",
                430120001: "Técnico",
                430120002: "Operario",
                430120003: "Auxiliar",
                430120004: "Complementario"
            }
            
            prog_obj = f.get("cr6a3_ProgramaId") or {}
            
            fichas_mapeadas.append({
                "id": fid,
                "codigo": codigo,
                "programa": programa,
                "nivel": map_nivel_inv.get(prog_obj.get("cr6a3_nivel"), "Técnico"),
                "jornada": {430120000: "Mañana", 430120001: "Tarde", 430120002: "Noche"}.get(f.get("cr6a3_jornada"), "Mañana"),
                "municipio": f.get("cr6a3_municipio", ""),
                "vocero": f.get("cr6a3_vocero", ""),
                "fecha_inicio": f.get("cr6a3_fecha_inicio", "")[:10] if f.get("cr6a3_fecha_inicio") else "",
                "fecha_fin": f.get("cr6a3_fecha_fin", "")[:10] if f.get("cr6a3_fecha_fin") else "",
                "fecha_inicio_practicas": f.get("cr6a3_fecha_inicio_practicas", "")[:10] if f.get("cr6a3_fecha_inicio_practicas") else "",
                "fecha_fin_practicas": f.get("cr6a3_fecha_fin_practicas", "")[:10] if f.get("cr6a3_fecha_fin_practicas") else "",
                "numero_aprendices": 0,
                "horas_programa_formacion": f.get("cr6a3_horas_programa_formacion", 0),
                "instructor_titular": instructores_dict.get(titular_id),
                "instructor_titular_id": titular_id,
                "tiene_diagnostico": tiene_diagnostico,
                "total_horas_programa": total_horas,
                "horas_programadas": horas_prog,
                "porcentaje_programacion": min(pct_prog, 100),
                "porcentaje_tecnica": min(pct_tec, 100),
                "alerta_tecnica": tiene_diagnostico and (pct_tec < META_TECNICA),
                "bajo_meta": tiene_diagnostico and (pct_prog < META_PROGRAMACION),
            })
        return fichas_mapeadas

    _exigir_demo()
    db = _cargar_db()
    instructores = {i["id"]: i for i in db["instructores"]}

    fichas = []
    for f in db["fichas"]:
        titular = instructores.get(f.get("instructor_titular_id"))
        fichas.append({
            "id": f["id"], "codigo": f["codigo"], "programa": f["programa"], "nivel": f["nivel"],
            "jornada": f["jornada"], "sede": f["sede"], "municipio": f.get("municipio", ""),
            "fecha_inicio": f.get("fecha_inicio", ""), "fecha_fin": f.get("fecha_fin", ""),
            "fecha_inicio_practicas": f.get("fecha_inicio_practicas", ""),
            "fecha_fin_practicas": f.get("fecha_fin_practicas", ""),
            "numero_aprendices": f.get("numero_aprendices", 0),
            "horas_programa_formacion": f.get("horas_programa_formacion", 0),
            "instructor_titular": _resumen_instructor(titular) if titular else None,
            "tiene_diagnostico": bool(f.get("competencias")),
            **_resumen_programacion(f, db["asignaciones"]),
        })

    if jornada:
        fichas = [f for f in fichas if f["jornada"] == jornada]
    if sede:
        fichas = [f for f in fichas if f["sede"] == sede]
    if buscar:
        q = buscar.lower()
        fichas = [
            f for f in fichas
            if q in f["codigo"].lower() or q in f["programa"].lower()
            or q in ((f["instructor_titular"] or {}).get("nombre", "").lower())
        ]
    return fichas


async def obtener_ficha(ficha_id: str) -> dict:
    """Detalle de la ficha: diagnóstico de competencias + asignaciones del calendario."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        # 1. Traer la ficha principal
        try:
            ficha_db = await consultar_dataverse(f"cr6a3_fichas({ficha_id})?$expand=cr6a3_ProgramaId")
        except Exception:
            raise HTTPException(status_code=404, detail="La ficha no existe.")
            
        # 2. Traer las competencias de esta ficha
        res_comps = await consultar_dataverse(f"cr6a3_competenciafichas?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        competencias_db = res_comps.get("value", [])
        
        # 3. Traer asignaciones de la ficha
        res_asig = await consultar_dataverse(f"cr6a3_asignacioneses?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        asignaciones_db = res_asig.get("value", [])
        
        # 4. Traer instructores para nombres
        res_inst = await consultar_dataverse("cr6a3_instructors")
        instructores_dict = {(i.get("cr6a3_instructorid") or "").lower(): i.get("cr6a3_nombre_completo") or "Instructor Asignado" for i in res_inst.get("value", [])}
        
        instructores_list = await listar_instructores()
        instructores_full_dict = {i["id"]: i for i in instructores_list}
        ambientes_list = await listar_ambientes()
        ambientes_full_dict = {a["id"]: a for a in ambientes_list}
        
        from collections import defaultdict
        horas_por_comp = defaultdict(int)
        instructores_por_comp = defaultdict(set)
        
        asignaciones = []
        for a in asignaciones_db:
            cid = a.get("_cr6a3_competenciafichaid_value") or a.get("_cr6a3_competenciaid_value", "")
            h = a.get("cr6a3_horas", 0)
            iid = a.get("_cr6a3_instructorid_value", "")
            amb_id = a.get("_cr6a3_ambienteid_value", "")
            
            if cid:
                horas_por_comp[cid.lower()] += h
                if iid:
                    instructores_por_comp[cid.lower()].add(instructores_dict.get(iid.lower(), "Instructor Asignado"))
            
            comp_db_obj = next((c for c in competencias_db if c.get("cr6a3_competenciafichaid") == cid), None)
            comp_obj = {"id": cid, "nombre": comp_db_obj.get("cr6a3_nombre", ""), "tipo": comp_db_obj.get("cr6a3_tipo", "")} if comp_db_obj else None
            
            inst_obj = instructores_full_dict.get(iid)
            ambiente_obj = ambientes_full_dict.get(amb_id)
            
            asignaciones.append({
                "id": a.get("cr6a3_asignacionesid"),
                "competencia_id": cid,
                "instructor_id": iid,
                "ambiente_id": amb_id,
                "fecha_inicio": a.get("cr6a3_fecha_inicio", "")[:10] if a.get("cr6a3_fecha_inicio") else "",
                "fecha_fin": a.get("cr6a3_fecha_fin", "")[:10] if a.get("cr6a3_fecha_fin") else "",
                "horas": h,
                "instructor": {"id": inst_obj["id"], "nombre": inst_obj["nombre"], "iniciales": "".join([p[0].upper() for p in inst_obj["nombre"].split() if p]), "color": "#39A900"} if inst_obj else None,
                "ambiente": {"id": ambiente_obj["id"], "nombre": ambiente_obj["nombre"], "sede": ambiente_obj["sede"]} if ambiente_obj else None,
                "competencia": comp_obj
            })
        
        diagnostico = []
        for c in competencias_db:
            cid = c.get("cr6a3_competenciafichaid", "")
            cid_lower = cid.lower() if cid else ""
            h_totales = c.get("cr6a3_horas", 0)
            h_prog = horas_por_comp[cid_lower]
            pct = round((h_prog / h_totales * 100)) if h_totales > 0 else 0
            
            diagnostico.append({
                "id": cid,
                "nombre": c.get("cr6a3_nombre", ""),
                "tipo": c.get("cr6a3_tipo", ""),
                "horas": h_totales,
                "horas_programadas": h_prog,
                "porcentaje": min(pct, 100),
                "instructores": list(instructores_por_comp[cid_lower]),
            })
            
        # Extraer ID dinámico por si Dataverse lo llama cr6a3_fichasid o cr6a3_fichaid
        ficha_id_key = next((k for k in ficha_db.keys() if k.startswith("cr6a3_") and k.endswith("id")), "cr6a3_fichaid")
        
        map_j = {430120000: "Mañana", 430120001: "Tarde", 430120002: "Noche"}
        
        total_prog = sum(c["horas"] for c in diagnostico)
        horas_prog_total = sum(a["horas"] for a in asignaciones)
        
        # Calcular técnica
        horas_tecnicas_programa = sum(c["horas"] for c in diagnostico if c["tipo"] == "Técnica")
        horas_tecnicas_prog = sum(a["horas"] for a in asignaciones if a.get("competencia") and a["competencia"].get("tipo") == "Técnica")
        pct_tecnica = round((horas_tecnicas_prog / horas_tecnicas_programa * 100)) if horas_tecnicas_programa > 0 else 0
        pct_prog_total = round((horas_prog_total / total_prog * 100)) if total_prog > 0 else 0
        tiene_diagnostico = len(diagnostico) > 0
        
        map_nivel_inv = {
            430120000: "Tecnólogo",
            430120001: "Técnico",
            430120002: "Operario",
            430120003: "Auxiliar",
            430120004: "Complementario"
        }
        
        prog_obj = ficha_db.get("cr6a3_ProgramaId") or {}
        
        return {
            "id": ficha_db.get(ficha_id_key),
            "codigo": ficha_db.get("cr6a3_numero_ficha", ""),
            "programa": ficha_db.get("cr6a3_nombre_programa", ""),
            "nivel": map_nivel_inv.get(prog_obj.get("cr6a3_nivel"), "Técnico"),
            "jornada": map_j.get(ficha_db.get("cr6a3_jornada"), "Mañana"),
            "municipio": ficha_db.get("cr6a3_municipio", ""),
            "vocero": ficha_db.get("cr6a3_vocero", ""),
            "fecha_inicio": ficha_db.get("cr6a3_fecha_inicio", "")[:10] if ficha_db.get("cr6a3_fecha_inicio") else "",
            "fecha_fin": ficha_db.get("cr6a3_fecha_fin", "")[:10] if ficha_db.get("cr6a3_fecha_fin") else "",
            "fecha_inicio_practicas": ficha_db.get("cr6a3_fecha_inicio_practicas", "")[:10] if ficha_db.get("cr6a3_fecha_inicio_practicas") else "",
            "fecha_fin_practicas": ficha_db.get("cr6a3_fecha_fin_practicas", "")[:10] if ficha_db.get("cr6a3_fecha_fin_practicas") else "",
            "numero_aprendices": 0,
            "horas_programa_formacion": ficha_db.get("cr6a3_horas_programa_formacion", 0),
            "instructor_titular": instructores_full_dict.get(ficha_db.get("_cr6a3_instructorasignado_value")),
            "instructor_titular_id": ficha_db.get("_cr6a3_instructorasignado_value"),
            "tiene_diagnostico": tiene_diagnostico,
            "diagnostico": diagnostico,
            "archivos": [],
            "asignaciones": asignaciones,
            "total_horas_programa": total_prog,
            "horas_programadas": horas_prog_total,
            "porcentaje_programacion": min(pct_prog_total, 100),
            "porcentaje_tecnica": min(pct_tecnica, 100),
            "alerta_tecnica": tiene_diagnostico and (pct_tecnica < META_TECNICA),
            "bajo_meta": tiene_diagnostico and (pct_prog_total < META_PROGRAMACION),
        }


    _exigir_demo()
    db = _cargar_db()
    ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
    instructores = {i["id"]: i for i in db["instructores"]}
    propias = sorted(
        (a for a in db["asignaciones"] if a["ficha_id"] == ficha_id),
        key=lambda a: a["fecha_inicio"],
    )

    # Diagnóstico: avance por competencia (horas e instructores que la han dictado)
    diagnostico = []
    for c in ficha.get("competencias", []):
        de_competencia = [a for a in propias if a["competencia_id"] == c["id"]]
        horas_programadas = sum(a["horas"] for a in de_competencia)
        nombres = []
        for a in de_competencia:
            nombre = instructores.get(a["instructor_id"], {}).get("nombre")
            if nombre and nombre not in nombres:
                nombres.append(nombre)
        diagnostico.append({
            **c,
            "horas_programadas": horas_programadas,
            "porcentaje": round(horas_programadas / c["horas"] * 100) if c["horas"] else 0,
            "instructores": nombres,
        })

    titular = instructores.get(ficha.get("instructor_titular_id"))
    return {
        "id": ficha["id"], "codigo": ficha["codigo"], "programa": ficha["programa"],
        "nivel": ficha["nivel"], "jornada": ficha["jornada"], "sede": ficha["sede"],
        "municipio": ficha.get("municipio", ""),
        "fecha_inicio": ficha.get("fecha_inicio", ""), "fecha_fin": ficha.get("fecha_fin", ""),
        "fecha_inicio_practicas": ficha.get("fecha_inicio_practicas", ""),
        "fecha_fin_practicas": ficha.get("fecha_fin_practicas", ""),
        "numero_aprendices": ficha.get("numero_aprendices", 0),
        "horas_programa_formacion": ficha.get("horas_programa_formacion", 0),
        "instructor_titular": _resumen_instructor(titular) if titular else None,
        "tiene_diagnostico": bool(ficha.get("competencias")),
        "diagnostico": diagnostico,
        "archivos": ficha.get("archivos", []),
        "asignaciones": [_enriquecer_asignacion(a, db) for a in propias],
        **_resumen_programacion(ficha, db["asignaciones"]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGOS (selects del formulario de programación)
# ─────────────────────────────────────────────────────────────────────────────
async def listar_instructores() -> list:
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        try:
            res = await consultar_dataverse("cr6a3_instructors")
            return [{"id": i.get("cr6a3_instructorid"), "nombre": i.get("cr6a3_nombre_completo", "")} for i in res.get("value", [])]
        except Exception:
            return []
    _exigir_demo()
    return _cargar_db()["instructores"]


async def listar_ambientes() -> list:
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        try:
            res = await consultar_dataverse("cr6a3_ambiente_formacions?$expand=cr6a3_sede")
            lista = []
            for a in res.get("value", []):
                sede_obj = a.get("cr6a3_sede") or {}
                sede_str = sede_obj.get("cr6a3_nombre", "")
                mun_str = sede_obj.get("cr6a3_municipio", "")
                ubicacion = f"{sede_str} ({mun_str})" if mun_str else sede_str
                lista.append({
                    "id": a.get("cr6a3_ambiente_formacionid"), 
                    "nombre": a.get("cr6a3_nombre_ambiente", ""), 
                    "capacidad": a.get("cr6a3_capacidad_aprendices", 30),
                    "sede": ubicacion
                })
            return lista
        except Exception:
            return []
    _exigir_demo()
    return _cargar_db()["ambientes"]


# ─────────────────────────────────────────────────────────────────────────────
# DISPONIBILIDAD (el semáforo 🟢/🔴/⚪ de la pantalla de programación)
# ─────────────────────────────────────────────────────────────────────────────
async def consultar_disponibilidad(
    ficha_id: str,
    fecha_inicio: str,
    fecha_fin: str,
    excluir_asignacion: str | None = None,
) -> dict:
    """Calcula, para el rango y la jornada de la ficha, el estado de cada
    instructor (disponible / ocupado / contrato vencido) y de cada ambiente."""
    try:
        inicio, fin = _fecha(fecha_inicio), _fecha(fecha_fin)
    except ValueError:
        raise HTTPException(status_code=422, detail="Las fechas del rango no son válidas (formato YYYY-MM-DD).")
    if fin < inicio:
        raise HTTPException(status_code=409, detail="La fecha final del rango no puede ser anterior a la inicial.")

    if not _es_demo():
        from services.dataverse import consultar_dataverse
        
        # 1. Ficha info
        ficha = await obtener_ficha(ficha_id)
        if not ficha:
            raise HTTPException(status_code=404, detail="La ficha no existe.")
        jornada = ficha.get("jornada", "")
        sede = ficha.get("sede", "")
        numero_aprendices = ficha.get("numero_aprendices", 0)

        # 2. Instructores, Ambientes, Fichas y Competencias
        instructores_raw = await consultar_dataverse("cr6a3_instructors")
        ambientes_raw = await consultar_dataverse("cr6a3_ambiente_formacions?$expand=cr6a3_sede")
        fichas_raw = await consultar_dataverse("cr6a3_fichas")
        competencias_raw = await consultar_dataverse("cr6a3_competenciafichas")
        
        fichas_dict = {(f.get("cr6a3_fichaid") or "").lower(): f for f in fichas_raw.get("value", [])}
        comp_dict = {(c.get("cr6a3_competenciafichaid") or "").lower(): c for c in competencias_raw.get("value", [])}
        
        # 3. Asignaciones que se cruzan en fecha (inicio <= fin AND fin >= inicio)
        query_asig = f"cr6a3_asignacioneses?$filter=cr6a3_fecha_inicio le '{fecha_fin}' and cr6a3_fecha_fin ge '{fecha_inicio}'"
        asignaciones_raw = await consultar_dataverse(query_asig)
        asignaciones_db = asignaciones_raw.get("value", [])

        map_jornada_inv = {430120000: "Mañana", 430120001: "Tarde", 430120002: "Noche"}
        map_vinculacion_inv = {430120000: "Planta", 430120001: "Contratista"}

        def cruces_de_dv(campo: str, id_valor: str) -> list:
            res = []
            for a in asignaciones_db:
                if (a.get("cr6a3_asignacionesid") or "").lower() == (excluir_asignacion or "").lower(): continue
                if (a.get(campo) or "").lower() != (id_valor or "").lower(): continue
                ficha_rel = fichas_dict.get((a.get("_cr6a3_fichaid_value") or "").lower()) or {}
                jornada_rel = map_jornada_inv.get(ficha_rel.get("cr6a3_jornada"), "")
                if jornada_rel != jornada: continue
                res.append(a)
            return res

        ficha_ocupada = None
        ocupada_por_ficha = [a for a in asignaciones_db if (a.get("_cr6a3_fichaid_value") or "").lower() == (ficha_id or "").lower() and (a.get("cr6a3_asignacionesid") or "").lower() != (excluir_asignacion or "").lower()]
        if ocupada_por_ficha:
            primera = ocupada_por_ficha[0]
            ficha_ocupada = {"detalle": f"La ficha ya tiene clase del {_formatear(primera.get('cr6a3_fecha_inicio', ''))} al {_formatear(primera.get('cr6a3_fecha_fin', ''))}."}

        instructores = []
        for i in instructores_raw.get("value", []):
            i_id = i.get("cr6a3_instructorid")
            fin_contrato = i.get("cr6a3_fin_contrato")
            if fin_contrato and fin > _fecha(fin_contrato[:10]):
                estado, detalle = "contrato_vencido", f"Contrato hasta el {_formatear(fin_contrato[:10])}"
            else:
                cruces = cruces_de_dv("_cr6a3_instructorid_value", i_id)
                if cruces:
                    c = cruces[0]
                    ficha_rel = fichas_dict.get((c.get("_cr6a3_fichaid_value") or "").lower()) or {}
                    estado = "ocupado"
                    detalle = f"Ocupado con ficha {ficha_rel.get('cr6a3_numero_ficha')} ({ficha_rel.get('cr6a3_nombre_programa')}) del {_formatear(c.get('cr6a3_fecha_inicio', ''))} al {_formatear(c.get('cr6a3_fecha_fin', ''))}"
                else:
                    estado, detalle = "disponible", "Disponible en todo el rango"
            
            ocupaciones = []
            for a in asignaciones_db:
                if (a.get("_cr6a3_instructorid_value") or "").lower() != (i_id or "").lower() or (a.get("cr6a3_asignacionesid") or "").lower() == (excluir_asignacion or "").lower(): continue
                ficha_rel = fichas_dict.get((a.get("_cr6a3_fichaid_value") or "").lower()) or {}
                comp_rel = comp_dict.get((a.get("_cr6a3_competenciafichaid_value") or "").lower()) or {}
                ocupaciones.append({
                    "ficha_codigo": ficha_rel.get("cr6a3_numero_ficha", ""),
                    "programa": ficha_rel.get("cr6a3_nombre_programa", ""),
                    "jornada": map_jornada_inv.get(ficha_rel.get("cr6a3_jornada"), ""),
                    "competencia": comp_rel.get("cr6a3_nombre", ""),
                    "fecha_inicio": a.get("cr6a3_fecha_inicio", "")[:10] if a.get("cr6a3_fecha_inicio") else "",
                    "fecha_fin": a.get("cr6a3_fecha_fin", "")[:10] if a.get("cr6a3_fecha_fin") else "",
                })
            
            # Extract perfil properly
            perfil_str = i.get("cr6a3_perfil", "")
            perfil_list = [p.strip() for p in perfil_str.split(",")] if perfil_str else []

            instructores.append({
                "id": i_id, "nombre": i.get("cr6a3_nombre_completo", ""),
                "tipo_vinculacion": map_vinculacion_inv.get(i.get("cr6a3_tipo_vinculacion"), "Desconocido"),
                "perfil": perfil_list,
                "estado": estado, "detalle": detalle, "ocupaciones": ocupaciones
            })

        ambientes = []
        for am in ambientes_raw.get("value", []):
            am_id = am.get("cr6a3_ambiente_formacionid")
            cruces = cruces_de_dv("_cr6a3_ambienteid_value", am_id)
            if cruces:
                c = cruces[0]
                ficha_rel = fichas_dict.get((c.get("_cr6a3_fichaid_value") or "").lower()) or {}
                estado = "ocupado"
                detalle = f"Reservado por ficha {ficha_rel.get('cr6a3_numero_ficha')} del {_formatear(c.get('cr6a3_fecha_inicio', ''))} al {_formatear(c.get('cr6a3_fecha_fin', ''))}"
            else:
                estado, detalle = "disponible", "Disponible en todo el rango"
            
            sede_obj = am.get("cr6a3_sede") or {}
            sede_str = sede_obj.get("cr6a3_nombre", "")
            mun_str = sede_obj.get("cr6a3_municipio", "")
            ubicacion_completa = f"{sede_str} ({mun_str})" if mun_str else sede_str
            
            capacidad = am.get("cr6a3_capacidad_aprendices", 0)
            cap_ok = capacidad >= numero_aprendices
            
            import unicodedata
            def normalizar(texto):
                return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
                
            ficha_sede_norm = normalizar(sede) if sede else ""
            sede_ok = (not ficha_sede_norm) or (ficha_sede_norm in normalizar(mun_str)) or (ficha_sede_norm in normalizar(sede_str))
            
            if not sede_ok:
                detalle = f"{ubicacion_completa} (La ficha pertenece a {sede})"
            
            ambientes.append({
                "id": am_id, "nombre": am.get("cr6a3_nombre_ambiente", ""), "sede": ubicacion_completa,
                "capacidad": capacidad, "tipo": am.get("cr6a3_tipo_ambiente"),
                "capacidad_suficiente": cap_ok, "sede_coincide": sede_ok,
                "estado": estado, "detalle": detalle
            })
            
        return {
            "jornada": jornada,
            "dias_habiles": _dias_habiles(inicio, fin),
            "horas_estimadas": _horas_rango(inicio, fin),
            "ficha_ocupada": ficha_ocupada,
            "instructores": instructores,
            "ambientes": ambientes,
        }

    _exigir_demo()
    db = _cargar_db()
    ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
    _exigir_diagnostico(ficha)

    fichas_por_id = {f["id"]: f for f in db["fichas"]}
    jornada = ficha.get("jornada", "")

    def cruces_de(campo: str, valor: str) -> list:
        resultado = []
        for a in db["asignaciones"]:
            if a["id"] == excluir_asignacion or a[campo] != valor: continue
            if fichas_por_id.get(a["ficha_id"], {}).get("jornada") != jornada: continue
            if _solapan(inicio, fin, _fecha(a["fecha_inicio"]), _fecha(a["fecha_fin"])):
                resultado.append(a)
        return resultado

    ocupada = [a for a in db["asignaciones"] if a["ficha_id"] == ficha_id and a["id"] != excluir_asignacion and _solapan(inicio, fin, _fecha(a["fecha_inicio"]), _fecha(a["fecha_fin"]))]
    ficha_ocupada = None
    if ocupada:
        primera = _enriquecer_asignacion(ocupada[0], db)
        ficha_ocupada = {"detalle": f"La ficha ya tiene programado a {(primera['instructor'] or {}).get('nombre', 'un instructor')} del {_formatear(primera['fecha_inicio'])} al {_formatear(primera['fecha_fin'])}."}

    instructores = []
    for i in db["instructores"]:
        if i.get("fin_contrato") and fin > _fecha(i["fin_contrato"]):
            estado, detalle = "contrato_vencido", f"Contrato hasta el {_formatear(i['fin_contrato'])}"
        else:
            cruces = cruces_de("instructor_id", i["id"])
            if cruces:
                cruce = cruces[0]
                ficha_cruce = fichas_por_id.get(cruce["ficha_id"], {})
                estado = "ocupado"
                detalle = f"Ocupado con la ficha {ficha_cruce.get('codigo', '')} ({ficha_cruce.get('programa', '')}) del {_formatear(cruce['fecha_inicio'])} al {_formatear(cruce['fecha_fin'])}"
            else:
                estado, detalle = "disponible", "Disponible en todo el rango"

        ocupaciones = []
        for a in sorted(db["asignaciones"], key=lambda x: x["fecha_inicio"]):
            if a["instructor_id"] != i["id"] or a["id"] == excluir_asignacion: continue
            if not _solapan(inicio, fin, _fecha(a["fecha_inicio"]), _fecha(a["fecha_fin"])): continue
            ficha_a = fichas_por_id.get(a["ficha_id"], {})
            competencia = next((c["nombre"] for c in ficha_a.get("competencias", []) if c["id"] == a["competencia_id"]), "")
            ocupaciones.append({
                "ficha_codigo": ficha_a.get("codigo", ""),
                "programa": ficha_a.get("programa", ""),
                "jornada": ficha_a.get("jornada", ""),
                "competencia": competencia,
                "fecha_inicio": a["fecha_inicio"],
                "fecha_fin": a["fecha_fin"],
            })

        instructores.append({**_resumen_instructor(i), "tipo_vinculacion": i["tipo_vinculacion"], "perfil": i.get("perfil", []), "estado": estado, "detalle": detalle, "ocupaciones": ocupaciones})

    ambientes = []
    for am in db["ambientes"]:
        cruces = cruces_de("ambiente_id", am["id"])
        if cruces:
            cruce = cruces[0]
            ficha_cruce = fichas_por_id.get(cruce["ficha_id"], {})
            estado = "ocupado"
            detalle = f"Reservado por la ficha {ficha_cruce.get('codigo', '')} del {_formatear(cruce['fecha_inicio'])} al {_formatear(cruce['fecha_fin'])}"
        else:
            estado, detalle = "disponible", "Disponible en todo el rango"
        capacidad_ok = am.get("capacidad", 0) >= ficha.get("numero_aprendices", 0)
        sede_coincide = not ficha.get("sede") or am.get("sede") == ficha.get("sede")
        if not sede_coincide:
            detalle = f"Sede {am['sede']}: la ficha pertenece a la sede {ficha['sede']}"
        ambientes.append({"id": am["id"], "nombre": am["nombre"], "sede": am["sede"], "capacidad": am["capacidad"], "tipo": am["tipo"], "capacidad_suficiente": capacidad_ok, "sede_coincide": sede_coincide, "estado": estado, "detalle": detalle})

    return {
        "jornada": jornada,
        "dias_habiles": _dias_habiles(inicio, fin),
        "horas_estimadas": _horas_rango(inicio, fin),
        "ficha_ocupada": ficha_ocupada,
        "instructores": instructores,
        "ambientes": ambientes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ASIGNACIONES (crear / actualizar / eliminar)
# ─────────────────────────────────────────────────────────────────────────────

async def _validar_asignacion_dataverse(datos: dict, excluir_id: str | None = None):
    from services.dataverse import consultar_dataverse
    from datetime import date
    
    fecha_inicio = datos.get("fecha_inicio")
    fecha_fin = datos.get("fecha_fin")
    ficha_id = datos.get("ficha_id")
    instructor_id = datos.get("instructor_id")
    ambiente_id = datos.get("ambiente_id")
    
    # Necesitamos la jornada de la ficha actual
    ficha_actual = await consultar_dataverse(f"cr6a3_fichas({ficha_id})")
    if not ficha_actual:
        raise HTTPException(status_code=404, detail="La ficha seleccionada no existe en Dataverse.")
    jornada_actual = ficha_actual.get("cr6a3_jornada")
    codigo_actual = ficha_actual.get("cr6a3_numero_ficha", "")
    
    inicio_ficha = ficha_actual.get("cr6a3_fecha_inicio")
    fin_ficha = ficha_actual.get("cr6a3_fecha_fin")
    
    dt_inicio = date.fromisoformat(fecha_inicio[:10])
    dt_fin = date.fromisoformat(fecha_fin[:10])
    
    if inicio_ficha and dt_inicio < date.fromisoformat(inicio_ficha[:10]):
        raise HTTPException(status_code=409, detail=f"La ficha {codigo_actual} inicia el {inicio_ficha[:10]}: no se puede programar antes.")
    if fin_ficha and dt_fin > date.fromisoformat(fin_ficha[:10]):
        raise HTTPException(status_code=409, detail=f"La ficha {codigo_actual} termina su etapa lectiva el {fin_ficha[:10]}: no se puede programar después.")
        
    query_asig = f"cr6a3_asignacioneses?$filter=cr6a3_fecha_inicio le '{fecha_fin}' and cr6a3_fecha_fin ge '{fecha_inicio}'"
    asignaciones_raw = await consultar_dataverse(query_asig)
    asignaciones_cruce = asignaciones_raw.get("value", [])
    
    map_jornada_inv = {430120000: "Mañana", 430120001: "Tarde", 430120002: "Noche"}
    jornada_texto_actual = map_jornada_inv.get(jornada_actual, "")
    
    # Obtener todas las fichas cruzadas para comparar su jornada
    fichas_cruzadas_ids = list(set(a.get("_cr6a3_fichaid_value") for a in asignaciones_cruce if a.get("_cr6a3_fichaid_value")))
    fichas_dict = {}
    if fichas_cruzadas_ids:
        filtros_fichas = " or ".join([f"cr6a3_fichaid eq {fid}" for fid in fichas_cruzadas_ids])
        f_raw = await consultar_dataverse(f"cr6a3_fichas?$filter={filtros_fichas}")
        for f in f_raw.get("value", []):
            fichas_dict[f.get("cr6a3_fichaid")] = f
            
    for otra in asignaciones_cruce:
        if (otra.get("cr6a3_asignacionesid") or "").lower() == (excluir_id or "").lower():
            continue
            
        # 1. Cruce misma ficha
        if (otra.get("_cr6a3_fichaid_value") or "").lower() == (ficha_id or "").lower():
            raise HTTPException(
                status_code=409,
                detail=f"La ficha {codigo_actual} ya tiene una programación que se cruza entre el {otra.get('cr6a3_fecha_inicio')} y el {otra.get('cr6a3_fecha_fin')}."
            )
            
        ficha_otra = fichas_dict.get(otra.get("_cr6a3_fichaid_value")) or {}
        
        if ficha_otra.get("cr6a3_jornada") != jornada_actual:
            continue
            
        # 2. Cruce instructor (misma jornada)
        if (otra.get("_cr6a3_instructorid_value") or "").lower() == (instructor_id or "").lower():
            raise HTTPException(
                status_code=409,
                detail=f"El instructor ya está ocupado en la jornada {jornada_texto_actual} con otra ficha del {otra.get('cr6a3_fecha_inicio')} al {otra.get('cr6a3_fecha_fin')}."
            )
            
        # 3. Cruce ambiente (misma jornada)
        if (otra.get("_cr6a3_ambienteid_value") or "").lower() == (ambiente_id or "").lower():
            raise HTTPException(
                status_code=409,
                detail=f"El ambiente ya está ocupado en la jornada {jornada_texto_actual} con otra ficha del {otra.get('cr6a3_fecha_inicio')} al {otra.get('cr6a3_fecha_fin')}."
            )

async def crear_asignacion(datos: dict) -> dict:
    if not _es_demo():
        from services.dataverse import crear_registro_dataverse
        from datetime import date, timedelta
        
        await _validar_asignacion_dataverse(datos)
        
        inicio = date.fromisoformat(datos["fecha_inicio"])
        fin = date.fromisoformat(datos["fecha_fin"])
        dias = sum(1 for d in range((fin - inicio).days + 1) if (inicio + timedelta(days=d)).weekday() < 5)
        horas = dias * 6
        
        # Nota: Dataverse suele requerir el nombre lógico en plural para los @odata.bind. 
        # Ejemplo: cr6a3_instructors para cr6a3_instructor.
        payload = {
            "cr6a3_nombre": f"Asignación Ficha",
            "cr6a3_fecha_inicio": datos["fecha_inicio"],
            "cr6a3_fecha_fin": datos["fecha_fin"],
            "cr6a3_horas": horas,
            "cr6a3_FichaId@odata.bind": f"/cr6a3_fichas({datos['ficha_id']})",
            "cr6a3_CompetenciaFichaId@odata.bind": f"/cr6a3_competenciafichas({datos['competencia_id']})",
            "cr6a3_InstructorId@odata.bind": f"/cr6a3_instructors({datos['instructor_id']})",
            "cr6a3_AmbienteId@odata.bind": f"/cr6a3_ambiente_formacions({datos['ambiente_id']})"
        }
        
        res = await crear_registro_dataverse("cr6a3_asignacioneses", payload)
        
        return {
            "id": res.get("cr6a3_asignacionid"), 
            "ficha_id": datos["ficha_id"],
            "instructor_id": datos["instructor_id"],
            "competencia_id": datos["competencia_id"],
            "ambiente_id": datos["ambiente_id"],
            "fecha_inicio": datos["fecha_inicio"],
            "fecha_fin": datos["fecha_fin"],
            "horas": horas
        }

    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        horas = _validar_asignacion(db, datos)
        asignacion = {"id": f"asig-{uuid.uuid4().hex[:8]}", **datos, "horas": horas}
        db["asignaciones"].append(asignacion)
        _guardar_db(db)
        return _enriquecer_asignacion(asignacion, db)


async def actualizar_asignacion(asignacion_id: str, datos: dict) -> dict:
    """Edita una asignación revalidando todas las reglas (se excluye a sí misma)."""
    if not _es_demo():
        from services.dataverse import actualizar_registro_dataverse, consultar_dataverse
        from datetime import date, timedelta
        
        actual_raw = await consultar_dataverse(f"cr6a3_asignacioneses({asignacion_id})")
        if not actual_raw:
            raise HTTPException(status_code=404, detail="La asignación no existe en Dataverse.")
            
        propuesta = {
            "fecha_inicio": datos.get("fecha_inicio", actual_raw.get("cr6a3_fecha_inicio")),
            "fecha_fin": datos.get("fecha_fin", actual_raw.get("cr6a3_fecha_fin")),
            "ficha_id": datos.get("ficha_id", actual_raw.get("_cr6a3_fichaid_value")),
            "instructor_id": datos.get("instructor_id", actual_raw.get("_cr6a3_instructorid_value")),
            "ambiente_id": datos.get("ambiente_id", actual_raw.get("_cr6a3_ambienteid_value"))
        }
        
        await _validar_asignacion_dataverse(propuesta, excluir_id=asignacion_id)
        
        payload = {}
        if "fecha_inicio" in datos and "fecha_fin" in datos:
            inicio = date.fromisoformat(datos["fecha_inicio"])
            fin = date.fromisoformat(datos["fecha_fin"])
            dias = sum(1 for d in range((fin - inicio).days + 1) if (inicio + timedelta(days=d)).weekday() < 5)
            horas = dias * 6
            payload["cr6a3_fecha_inicio"] = datos["fecha_inicio"]
            payload["cr6a3_fecha_fin"] = datos["fecha_fin"]
            payload["cr6a3_horas"] = horas
            
        if "instructor_id" in datos:
            payload["cr6a3_InstructorId@odata.bind"] = f"/cr6a3_instructors({datos['instructor_id']})"
        if "ambiente_id" in datos:
            payload["cr6a3_AmbienteId@odata.bind"] = f"/cr6a3_ambiente_formacions({datos['ambiente_id']})"
            
        if payload:
            await actualizar_registro_dataverse("cr6a3_asignacioneses", asignacion_id, payload)
            
        return {"id": asignacion_id, "mensaje": "Asignación actualizada en Dataverse"}

    _exigir_demo()
    cambios = {k: v for k, v in datos.items() if v is not None}
    async with _demo_lock:
        db = _cargar_db()
        actual = _buscar(db["asignaciones"], asignacion_id, "La asignación")
        propuesta = {**actual, **cambios}
        horas = _validar_asignacion(db, propuesta, excluir_id=asignacion_id)
        actual.update({**cambios, "horas": horas})
        _guardar_db(db)
        return _enriquecer_asignacion(actual, db)


async def eliminar_asignacion(asignacion_id: str) -> dict:
    if not _es_demo():
        from services.dataverse import obtener_token_dataverse, cliente_dataverse
        import os
        import httpx
        url = f"{os.getenv('DATAVERSE_URL')}/api/data/v9.2/cr6a3_asignacioneses({asignacion_id})"
        headers = {
            "Authorization": f"Bearer {obtener_token_dataverse()}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json"
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.delete(url, headers=headers)
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            from fastapi import HTTPException
            raise HTTPException(status_code=exc.response.status_code, detail="No se pudo eliminar de Dataverse.")
        return {"mensaje": "Asignación eliminada de Dataverse."}

    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        _buscar(db["asignaciones"], asignacion_id, "La asignación")
        db["asignaciones"] = [a for a in db["asignaciones"] if a["id"] != asignacion_id]
        _guardar_db(db)
        return {"mensaje": "Asignación eliminada. La ficha, el instructor y el ambiente quedaron liberados."}


# ─────────────────────────────────────────────────────────────────────────────
# INDICADORES (meta 70 %, alerta técnica < 60 %, carga mensual vs 160 h)
# ─────────────────────────────────────────────────────────────────────────────
async def obtener_indicadores(mes: str | None = None) -> dict:
    """`mes` en formato YYYY-MM; por defecto el mes actual de Bogotá."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        
        hoy = datetime.now(_ZONA_BOGOTA).date()
        try:
            anio, num_mes = (int(p) for p in (mes or hoy.strftime("%Y-%m")).split("-"))
            date(anio, num_mes, 1)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail=f"'{mes}' no es un mes válido (formato esperado YYYY-MM).")
            
        fichas_list = await listar_fichas()
        
        res_asig = await consultar_dataverse("cr6a3_asignacioneses")
        asignaciones_db = res_asig.get("value", [])
        
        instructores_list = await listar_instructores()
        
        porcentajes = []
        fichas_bajo_meta = []
        alertas_tecnica = []
        
        for f in fichas_list:
            pct = f.get("porcentaje_programacion", 0)
            pct_tec = f.get("porcentaje_tecnica", 0)
            porcentajes.append(pct)
            
            if pct < META_PROGRAMACION:
                fichas_bajo_meta.append({"id": f["id"], "codigo": f["codigo"], "programa": f["programa"], "porcentaje": pct})
                
            if pct_tec < META_TECNICA and f.get("tiene_diagnostico"):
                alertas_tecnica.append({"id": f["id"], "codigo": f["codigo"], "programa": f["programa"], "porcentaje_tecnica": pct_tec})

        carga_instructores = []
        for i in instructores_list:
            horas_mes = sum(
                a.get("cr6a3_horas", 0)
                for a in asignaciones_db 
                if a.get("_cr6a3_instructorid_value") == i["id"] 
                and a.get("cr6a3_fecha_inicio", "").startswith(f"{anio:04d}-{num_mes:02d}")
            )
            limite = LIMITES_MENSUALES.get(i.get("tipo_vinculacion", "Contratista"), 160)
            carga_instructores.append({
                "id": i["id"],
                "nombre": i["nombre"],
                "iniciales": "".join([p[0].upper() for p in i["nombre"].split() if p]),
                "color": "#39A900",
                "tipo_vinculacion": i.get("tipo_vinculacion", "Contratista"),
                "horas_mes": horas_mes,
                "limite": limite,
                "porcentaje": round(horas_mes / limite * 100) if limite else 0,
            })
        carga_instructores.sort(key=lambda c: c["horas_mes"], reverse=True)

        return {
            "modo_demo": False,
            "mes": f"{anio:04d}-{num_mes:02d}",
            "total_fichas": len(fichas_list),
            "promedio_programacion": round(sum(porcentajes) / len(porcentajes)) if porcentajes else 0,
            "meta_programacion": META_PROGRAMACION,
            "meta_tecnica": META_TECNICA,
            "fichas_bajo_meta": fichas_bajo_meta,
            "alertas_tecnica": alertas_tecnica,
            "carga_instructores": carga_instructores,
        }
    _exigir_demo()
    db = _cargar_db()

    hoy = datetime.now(_ZONA_BOGOTA).date()
    try:
        anio, num_mes = (int(p) for p in (mes or hoy.strftime("%Y-%m")).split("-"))
        date(anio, num_mes, 1)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail=f"'{mes}' no es un mes válido (formato esperado YYYY-MM).")

    resumenes = {f["id"]: _resumen_programacion(f, db["asignaciones"]) for f in db["fichas"]}
    porcentajes = [r["porcentaje_programacion"] for r in resumenes.values()]

    fichas_bajo_meta = [
        {"id": f["id"], "codigo": f["codigo"], "programa": f["programa"],
         "porcentaje": resumenes[f["id"]]["porcentaje_programacion"]}
        for f in db["fichas"] if resumenes[f["id"]]["bajo_meta"]
    ]
    alertas_tecnica = [
        {"id": f["id"], "codigo": f["codigo"], "programa": f["programa"],
         "porcentaje_tecnica": resumenes[f["id"]]["porcentaje_tecnica"]}
        for f in db["fichas"] if resumenes[f["id"]]["alerta_tecnica"]
    ]

    carga_instructores = []
    for i in db["instructores"]:
        horas_mes = sum(
            _horas_en_mes(a, anio, num_mes)
            for a in db["asignaciones"] if a["instructor_id"] == i["id"]
        )
        limite = LIMITES_MENSUALES.get(i["tipo_vinculacion"], 160)
        carga_instructores.append({
            **_resumen_instructor(i),
            "tipo_vinculacion": i["tipo_vinculacion"],
            "horas_mes": horas_mes,
            "limite": limite,
            "porcentaje": round(horas_mes / limite * 100) if limite else 0,
        })
    carga_instructores.sort(key=lambda c: c["horas_mes"], reverse=True)

    return {
        "modo_demo": _es_demo(),
        "mes": f"{anio:04d}-{num_mes:02d}",
        "total_fichas": len(db["fichas"]),
        "promedio_programacion": round(sum(porcentajes) / len(porcentajes)) if porcentajes else 0,
        "meta_programacion": META_PROGRAMACION,
        "meta_tecnica": META_TECNICA,
        "fichas_bajo_meta": fichas_bajo_meta,
        "alertas_tecnica": alertas_tecnica,
        "carga_instructores": carga_instructores,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO DE PROGRAMAS (el diagnóstico de una ficha nueva se genera desde aquí)
# ─────────────────────────────────────────────────────────────────────────────
def _resumen_programa(p: dict) -> dict:
    return {
        **p,
        "total_horas": sum(c["horas"] for c in p.get("competencias", [])),
    }


async def listar_municipios() -> list[str]:
    """Lista los municipios disponibles (obtenidos de la tabla de sedes)."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        try:
            res = await consultar_dataverse("cr6a3_sedes?$select=cr6a3_municipio")
            return sorted(list(set(
                item.get("cr6a3_municipio") 
                for item in res.get("value", []) 
                if item.get("cr6a3_municipio")
            )))
        except Exception:
            return []
            
    db = _cargar_db()
    return sorted(list(set(f.get("municipio") for f in db["fichas"] if f.get("municipio"))))


async def listar_programas() -> list:
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        # 1. Traer todos los programas
        res_prog = await consultar_dataverse("cr6a3_programases")
        programas_db = res_prog.get("value", [])
        
        # 2. Mapearlos al formato esperado
        map_nivel_inverso = {
            430120000: "Tecnólogo",
            430120001: "Técnico",
            430120002: "Operario",
            430120003: "Auxiliar",
            430120004: "Complementario"
        }
        
        programas_mapeados = []
        for p in programas_db:
            nivel_raw = p.get("cr6a3_nivel")
            nivel_str = map_nivel_inverso.get(nivel_raw, "Técnico") if nivel_raw else "Técnico"
            
            programas_mapeados.append({
                "id": p.get("cr6a3_programasid"),
                "nombre": p.get("cr6a3_nombre", ""),
                "version": p.get("cr6a3_version", ""),
                "nivel": nivel_str,
                "total_horas": 0, # Podríamos traer las competencias para sumar, pero en el listado básico puede omitirse o calcularse luego
                "competencias": []
            })
        return programas_mapeados

    _exigir_demo()
    return [_resumen_programa(p) for p in _cargar_db()["programas"]]


async def listar_competencias_programa(programa_id: str) -> list:
    """Devuelve las competencias de un programa específico."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse
        # Consultar las competencias asociadas al programa
        # Ajustamos el filtro para usar el campo relacional
        query = f"cr6a3_competenciasprogramas?$filter=_cr6a3_programaid_value eq '{programa_id}'"
        res_comp = await consultar_dataverse(query)
        competencias_db = res_comp.get("value", [])
        
        competencias_mapeadas = []
        for c in competencias_db:
            competencias_mapeadas.append({
                "nombre": c.get("cr6a3_nombre", ""),
                "tipo": c.get("cr6a3_tipo", ""),
                "horas": c.get("cr6a3_horas", 0)
            })
        return competencias_mapeadas

    _exigir_demo()
    db = _cargar_db()
    for p in db["programas"]:
        if p["id"] == programa_id:
            return p.get("competencias", [])
    return []


async def crear_programa(datos: dict) -> dict:
    """Registra un programa en el catálogo (nombre + versión únicos)."""
    if not _es_demo():
        from services.dataverse import crear_registro_dataverse
        
        map_nivel = {
            "Tecnólogo": 430120000,
            "Técnico": 430120001,
            "Operario": 430120002,
            "Auxiliar": 430120003,
            "Complementario": 430120004
        }
        
        # 1. Crear el programa base en Dataverse
        payload_programa = {
            "cr6a3_nombre": datos["nombre"].strip(),
            "cr6a3_version": datos["version"].strip(),
            "cr6a3_nivel": map_nivel.get(datos["nivel"], 430120001)
        }
        
        programa_creado = await crear_registro_dataverse("cr6a3_programases", payload_programa)
        
        # Extraer dinámicamente la llave primaria (puede llamarse cr6a3_programaid o cr6a3_programasid)
        programa_id_key = next((k for k in programa_creado.keys() if k.startswith("cr6a3_") and k.endswith("id")), "cr6a3_programasid")
        programa_id = programa_creado.get(programa_id_key)
        
        if not programa_id:
            print(f"Error: Dataverse no devolvió un ID reconocido. Respuesta: {programa_creado}")
            raise HTTPException(status_code=500, detail="El programa se creó pero no se pudo obtener su ID interno.")
        
        # 2. Iterar y crear las competencias maestras asociadas
        for comp in datos["competencias"]:
            payload_comp = {
                "cr6a3_nombre": comp["nombre"].strip(),
                "cr6a3_tipo": comp["tipo"],
                "cr6a3_horas": comp["horas"],
                "cr6a3_ProgramaId@odata.bind": f"/cr6a3_programases({programa_id})"
            }
            await crear_registro_dataverse("cr6a3_competenciasprogramas", payload_comp)
            
        return {
            "id": programa_id,
            "nombre": datos["nombre"].strip(),
            "version": datos["version"].strip(),
            "nivel": datos["nivel"],
            "total_horas": sum(comp["horas"] for comp in datos["competencias"]),
            "competencias": datos["competencias"]
        }
        
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        for p in db["programas"]:
            if (p["nombre"].strip().lower() == datos["nombre"].strip().lower()
                    and p["version"].strip().lower() == datos["version"].strip().lower()):
                raise HTTPException(
                    status_code=409,
                    detail=f"El programa '{datos['nombre']}' versión {datos['version']} ya está en el catálogo.",
                )
        programa = {
            "id": f"prog-{uuid.uuid4().hex[:8]}",
            "nombre": datos["nombre"].strip(),
            "version": datos["version"].strip(),
            "nivel": datos["nivel"],
            "competencias": [
                {"nombre": c["nombre"].strip(), "tipo": c["tipo"], "horas": c["horas"]}
                for c in datos["competencias"]
            ],
        }
        db["programas"].append(programa)
        _guardar_db(db)
        return _resumen_programa(programa)


# ─────────────────────────────────────────────────────────────────────────────
# ALTA DE FICHAS Y EDICIÓN DEL DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────────────────
async def crear_ficha(datos: dict) -> dict:
    """Crea una ficha titulada copiando la matriz de competencias del programa
    elegido en el catálogo (así la ficha nace con su diagnóstico registrado)."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse, crear_registro_dataverse
        
        programa_id = datos["programa_id"]
        # 1. Obtener el programa para sacar su nombre y nivel (y verificar que existe)
        try:
            programa_db = await consultar_dataverse(f"cr6a3_programases({programa_id})")
        except Exception:
            raise HTTPException(status_code=404, detail="El programa seleccionado no existe en el catálogo.")
            
        map_jornada = {
            "Mañana": 430120000,
            "Tarde": 430120001,
            "Noche": 430120002
        }
        
        # 2. Crear la ficha
        payload_ficha = {
            "cr6a3_numero_ficha": datos["codigo"].strip(),
            "cr6a3_nombre_programa": programa_db.get("cr6a3_nombre", ""),
            "cr6a3_jornada": map_jornada.get(datos["jornada"], 430120000),
            "cr6a3_fecha_inicio": datos["fecha_inicio"],
            "cr6a3_fecha_fin": datos["fecha_fin"],
            "cr6a3_fecha_inicio_practicas": datos.get("fecha_inicio_practicas"),
            "cr6a3_fecha_fin_practicas": datos.get("fecha_fin_practicas"),
            "cr6a3_municipio": datos["municipio"].strip(),
            "cr6a3_vocero": (datos.get("vocero") or "").strip(),
            "cr6a3_horas_programa_formacion": datos.get("horas_programa_formacion", 0),
            "cr6a3_ProgramaId@odata.bind": f"/cr6a3_programases({programa_id})"
        }
        
        # Opcional: si hay instructor titular
        instructor_id = datos.get("instructor_titular_id")
        if instructor_id:
            payload_ficha["cr6a3_InstructorAsignado@odata.bind"] = f"/cr6a3_instructors({instructor_id})"
            
        try:
            ficha_creada = await crear_registro_dataverse("cr6a3_fichas", payload_ficha)
            ficha_nueva_id = ficha_creada.get("id_from_header") or ficha_creada.get("cr6a3_fichasid") or ficha_creada.get("cr6a3_fichaid")
            if not ficha_nueva_id:
                raise HTTPException(status_code=500, detail="Ficha creada pero no se pudo leer su ID de Dataverse.")
        except HTTPException as e:
            if "duplicate" in str(e.detail).lower() or e.status_code == 409:
                raise HTTPException(status_code=409, detail=f"Ya existe una ficha con el código {datos['codigo']}. Verifique el número en Sofía Plus.")
            raise e
            
        # 3. Obtener competencias del catálogo
        res_comps = await consultar_dataverse(f"cr6a3_competenciasprogramas?$filter=_cr6a3_programaid_value eq '{programa_id}'")
        competencias_programa = res_comps.get("value", [])
        
        # 4. Clonarlas hacia cr6a3_competenciafichas
        for comp in competencias_programa:
            payload_comp = {
                "cr6a3_nombre": comp.get("cr6a3_nombre"),
                "cr6a3_tipo": comp.get("cr6a3_tipo"),
                "cr6a3_horas": comp.get("cr6a3_horas"),
                "cr6a3_FichaId@odata.bind": f"/cr6a3_fichas({ficha_nueva_id})"
            }
            await crear_registro_dataverse("cr6a3_competenciafichas", payload_comp)
            
        return await obtener_ficha(ficha_nueva_id)


    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        if any(f["codigo"] == datos["codigo"].strip() for f in db["fichas"]):
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una ficha con el código {datos['codigo']}. Verifique el número en Sofía Plus.",
            )
        programa = _buscar(db["programas"], datos["programa_id"], "El programa del catálogo")
        if datos.get("instructor_titular_id"):
            _buscar(db["instructores"], datos["instructor_titular_id"], "El instructor titular")
        if _fecha(datos["fecha_fin"]) < _fecha(datos["fecha_inicio"]):
            raise HTTPException(
                status_code=409,
                detail="La fecha de fin de la etapa lectiva no puede ser anterior a la de inicio.",
            )
        if datos.get("fecha_inicio_practicas") and datos.get("fecha_fin_practicas"):
            if _fecha(datos["fecha_fin_practicas"]) < _fecha(datos["fecha_inicio_practicas"]):
                raise HTTPException(
                    status_code=409,
                    detail="La fecha de fin de la etapa de prácticas no puede ser anterior a la de inicio.",
                )

        ficha_id = f"fic-{uuid.uuid4().hex[:8]}"
        ficha = {
            "id": ficha_id,
            "codigo": datos["codigo"].strip(),
            "programa": programa["nombre"],
            "nivel": programa["nivel"],
            "jornada": datos["jornada"],
            "municipio": datos["municipio"].strip(),
            "vocero": (datos.get("vocero") or "").strip(),
            "instructor_titular_id": datos.get("instructor_titular_id") or "",
            "fecha_inicio": datos["fecha_inicio"],
            "fecha_fin": datos["fecha_fin"],
            "fecha_inicio_practicas": datos.get("fecha_inicio_practicas", ""),
            "fecha_fin_practicas": datos.get("fecha_fin_practicas", ""),
            "numero_aprendices": datos["numero_aprendices"],
            "horas_programa_formacion": datos.get("horas_programa_formacion", 0),
            # El diagnóstico nace copiado del catálogo (con ids propios de la ficha)
            "competencias": [
                {"id": f"c-{uuid.uuid4().hex[:8]}", "nombre": c["nombre"], "tipo": c["tipo"], "horas": c["horas"]}
                for c in programa.get("competencias", [])
            ],
            "archivos": [],
        }
        db["fichas"].append(ficha)
        _guardar_db(db)
    return await obtener_ficha(ficha_id)

async def actualizar_titular_ficha(ficha_id: str, instructor_id: str | None) -> dict:
    if not _es_demo():
        from services.dataverse import actualizar_registro_dataverse
        payload = {}
        if instructor_id:
            payload["cr6a3_InstructorAsignado@odata.bind"] = f"/cr6a3_instructors({instructor_id})"
        else:
            # Dataverse V9.2 a veces permite null en bind o desvincular requiere DELETE
            # Para esta demo simplificamos, asumiendo que envian siempre uno o no se hace unbind
            pass
            
        if payload:
            await actualizar_registro_dataverse("cr6a3_fichas", ficha_id, payload)
        return {"success": True}

    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
        if instructor_id:
            _buscar(db["instructores"], instructor_id, "El instructor titular")
        ficha["instructor_titular_id"] = instructor_id or ""
        _guardar_db(db)
    return await obtener_ficha(ficha_id)



# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO DEL INSTRUCTOR (la "matriz por instructor" del Excel)
# ─────────────────────────────────────────────────────────────────────────────
async def calendario_instructor(instructor_id: str | None = None, correo: str | None = None) -> dict:
    """Programación completa de un instructor (por id o por correo institucional):
    lo que cada instructor consulta en su propia matriz."""
    if _es_demo():
        if not instructor_id and not correo:
            raise HTTPException(status_code=422, detail="Indique el instructor (instructor_id o correo).")
        db = _cargar_db()

        instructor = None
        if instructor_id:
            instructor = next((i for i in db["instructores"] if i["id"] == instructor_id), None)
        elif correo:
            instructor = next(
                (i for i in db["instructores"] if i.get("correo", "").lower() == correo.strip().lower()), None)
        if not instructor:
            raise HTTPException(
                status_code=404,
                detail="No se encontró un instructor con esos datos en la programación de tituladas.",
            )

        propias = sorted(
            (a for a in db["asignaciones"] if a["instructor_id"] == instructor["id"]),
            key=lambda a: a["fecha_inicio"],
        )
        return {
            "modo_demo": True,
            "instructor": {
                **_resumen_instructor(instructor),
                "correo": instructor.get("correo", ""),
                "tipo_vinculacion": instructor.get("tipo_vinculacion", ""),
                "fin_contrato": instructor.get("fin_contrato", ""),
                "perfil": instructor.get("perfil", []),
                "limite_mensual": LIMITES_MENSUALES.get(instructor.get("tipo_vinculacion"), 160),
            },
            "asignaciones": [_enriquecer_asignacion(a, db) for a in propias],
        }
    else:
        from services.dataverse import consultar_dataverse
        
        if not instructor_id and not correo:
            raise HTTPException(status_code=422, detail="Indique el instructor (instructor_id o correo).")
            
        res_inst = None
        if instructor_id:
            res_raw = await consultar_dataverse(f"cr6a3_instructors({instructor_id})")
            if res_raw:
                res_inst = res_raw
        elif correo:
            q = f"cr6a3_instructors?$filter=cr6a3_correo eq '{correo.strip()}'"
            res_list = await consultar_dataverse(q)
            if res_list and res_list.get("value"):
                res_inst = res_list["value"][0]

        if not res_inst:
            raise HTTPException(status_code=404, detail="No se encontró el instructor en Dataverse.")
            
        real_instructor_id = res_inst.get("cr6a3_instructorid")
        tipo_vinculacion = "Planta" if res_inst.get("cr6a3_tipo_vinculacion") == 430120000 else "Contratista"
        
        instructor_dict = {
            "id": real_instructor_id,
            "nombre": res_inst.get("cr6a3_nombre_completo", "Instructor Asignado"),
            "iniciales": res_inst.get("cr6a3_iniciales", ""),
            "color": res_inst.get("cr6a3_color_hex", "#cccccc"),
            "correo": res_inst.get("cr6a3_correo", ""),
            "tipo_vinculacion": tipo_vinculacion,
            "fin_contrato": res_inst.get("cr6a3_fin_contrato", ""),
            "perfil": res_inst.get("cr6a3_perfil", "").split(",") if res_inst.get("cr6a3_perfil") else [],
            "limite_mensual": LIMITES_MENSUALES.get(tipo_vinculacion, 160),
        }
        
        query_asig = (
            f"cr6a3_asignacioneses?$filter=_cr6a3_instructorid_value eq '{real_instructor_id}'"
            f"&$expand=cr6a3_FichaId($select=cr6a3_numero_ficha,cr6a3_nombre_programa,cr6a3_jornada),cr6a3_AmbienteId($select=cr6a3_nombre_ambiente,_cr6a3_sede_value),cr6a3_CompetenciaFichaId($select=cr6a3_nombre,cr6a3_tipo)"
        )
        res_asig = await consultar_dataverse(query_asig)
        asignaciones_db = res_asig.get("value", [])
        
        map_jornada_inv = {430120000: "Mañana", 430120001: "Tarde", 430120002: "Noche"}

        asignaciones_mapped = []
        for a in asignaciones_db:
            ficha = a.get("cr6a3_FichaId", {}) or {}
            ambiente = a.get("cr6a3_AmbienteId", {}) or {}
            competencia = a.get("cr6a3_CompetenciaFichaId", {}) or {}
            
            sede_formatted = ambiente.get("_cr6a3_sede_value@OData.Community.Display.V1.FormattedValue", "CAAA")
            
            asignaciones_mapped.append({
                "id": a.get("cr6a3_asignacionid"),
                "fecha_inicio": a.get("cr6a3_fecha_inicio"),
                "fecha_fin": a.get("cr6a3_fecha_fin"),
                "horas": a.get("cr6a3_horas", 0),
                "jornada": map_jornada_inv.get(ficha.get("cr6a3_jornada"), "Mañana"),
                "ficha_codigo": ficha.get("cr6a3_numero_ficha", ""),
                "ficha_programa": ficha.get("cr6a3_nombre_programa", ""),
                "instructor": {
                    "id": instructor_dict["id"], "nombre": instructor_dict["nombre"],
                    "iniciales": instructor_dict["iniciales"], "color": instructor_dict["color"]
                },
                "competencia": {
                    "id": competencia.get("cr6a3_competenciafichaid"),
                    "nombre": competencia.get("cr6a3_nombre", "Competencia"),
                    "tipo": "Técnica" if competencia.get("cr6a3_tipo") == 430120000 else "Transversal"
                } if competencia and competencia.get("cr6a3_competenciafichaid") else None,
                "ambiente": {
                    "id": ambiente.get("cr6a3_ambiente_formacionid"),
                    "nombre": ambiente.get("cr6a3_nombre_ambiente", "Ambiente"),
                    "sede": sede_formatted
                } if ambiente and ambiente.get("cr6a3_ambiente_formacionid") else None
            })
            
        asignaciones_mapped.sort(key=lambda x: x["fecha_inicio"] or "")
        
        return {
            "modo_demo": False,
            "instructor": instructor_dict,
            "asignaciones": asignaciones_mapped
        }


# ─────────────────────────────────────────────────────────────────────────────
# RESPALDO DE ARCHIVOS (los Excel históricos de cada ficha, solo lectura)
# ─────────────────────────────────────────────────────────────────────────────
def _nombre_seguro(valor: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", valor or "archivo")


def _carpeta_ficha(ficha_id: str) -> Path:
    carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


async def agregar_archivo_ficha(ficha_id: str, nombre: str, contenido: bytes) -> list:
    """Guarda un archivo histórico de la ficha (no se modifica: solo respaldo
    descargable) y registra sus metadatos. Devuelve la lista actualizada."""
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
        archivo_id = f"arch-{uuid.uuid4().hex[:8]}"
        nombre_limpio = _nombre_seguro(nombre)
        (_carpeta_ficha(ficha_id) / f"{archivo_id}__{nombre_limpio}").write_bytes(contenido)
        ficha.setdefault("archivos", []).append({
            "id": archivo_id,
            "nombre": nombre,
            "tamano": len(contenido),
            "fecha": datetime.now(_ZONA_BOGOTA).strftime("%Y-%m-%d %H:%M"),
        })
        _guardar_db(db)
        return ficha["archivos"]


def obtener_archivo_ficha(ficha_id: str, archivo_id: str) -> tuple:
    """Devuelve (ruta, nombre_original) del archivo pedido, o 404."""
    db = _cargar_db()
    ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
    meta = next((a for a in ficha.get("archivos", []) if a["id"] == archivo_id), None)
    carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
    coincidencias = sorted(carpeta.glob(f"{_nombre_seguro(archivo_id)}__*")) if carpeta.exists() else []
    if not meta or not coincidencias:
        raise HTTPException(status_code=404, detail="El archivo solicitado no existe en el servidor.")
    return coincidencias[0], meta["nombre"]


async def eliminar_archivo_ficha(ficha_id: str, archivo_id: str) -> dict:
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
        archivos = ficha.get("archivos", [])
        if not any(a["id"] == archivo_id for a in archivos):
            raise HTTPException(status_code=404, detail="El archivo indicado no existe en la ficha.")
        carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
        for ruta in carpeta.glob(f"{_nombre_seguro(archivo_id)}__*"):
            ruta.unlink(missing_ok=True)
        ficha["archivos"] = [a for a in archivos if a["id"] != archivo_id]
        _guardar_db(db)
        return {"mensaje": "Archivo eliminado del respaldo.", "archivos": ficha["archivos"]}


async def actualizar_diagnostico(ficha_id: str, competencias: list) -> dict:
    """Reemplaza la matriz de competencias de la ficha. Las competencias que ya
    tienen asignaciones en el calendario no se pueden eliminar (409)."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse, crear_registro_dataverse, eliminar_registro_dataverse, actualizar_registro_dataverse
        
        # 1. Obtener competencias actuales
        res_comps = await consultar_dataverse(f"cr6a3_competenciafichas?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        actuales = res_comps.get("value", [])
        
        # 2. Obtener asignaciones de la ficha para ver qué competencias están en uso
        res_asig = await consultar_dataverse(f"cr6a3_asignacioneses?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        asignaciones = res_asig.get("value", [])
        comps_en_uso = {a.get("_cr6a3_competenciafichaid_value") for a in asignaciones if a.get("_cr6a3_competenciafichaid_value")}
        
        ids_nuevos = {c.get("id") for c in competencias if c.get("id")}
        
        # Verificar eliminadas en uso
        eliminadas_en_uso = []
        for c in actuales:
            cid = c.get("cr6a3_competenciafichaid")
            if cid and cid not in ids_nuevos and cid in comps_en_uso:
                eliminadas_en_uso.append(c.get("cr6a3_nombre", "Desconocida"))
                
        if eliminadas_en_uso:
            raise HTTPException(
                status_code=409,
                detail=f"No se pueden eliminar competencias que ya tienen asignaciones: {', '.join(eliminadas_en_uso)}"
            )
            
        # Ejecutar eliminaciones
        for c in actuales:
            cid = c.get("cr6a3_competenciafichaid")
            if cid and cid not in ids_nuevos:
                await eliminar_registro_dataverse(f"cr6a3_competenciafichas({cid})")
                
        # Ejecutar creaciones y actualizaciones
        for c in competencias:
            payload_comp = {
                "cr6a3_nombre": comp.get("cr6a3_nombre"),
                "cr6a3_tipo": comp.get("cr6a3_tipo"),
                "cr6a3_horas": comp.get("cr6a3_horas"),
                "cr6a3_FichaId@odata.bind": f"/cr6a3_fichas({ficha_nueva_id})"
            }
            await crear_registro_dataverse("cr6a3_competenciafichas", payload_comp)
            
        return await obtener_ficha(ficha_nueva_id)


    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        if any(f["codigo"] == datos["codigo"].strip() for f in db["fichas"]):
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una ficha con el código {datos['codigo']}. Verifique el número en Sofía Plus.",
            )
        programa = _buscar(db["programas"], datos["programa_id"], "El programa del catálogo")
        if datos.get("instructor_titular_id"):
            _buscar(db["instructores"], datos["instructor_titular_id"], "El instructor titular")
        if _fecha(datos["fecha_fin"]) < _fecha(datos["fecha_inicio"]):
            raise HTTPException(
                status_code=409,
                detail="La fecha de fin de la etapa lectiva no puede ser anterior a la de inicio.",
            )

        ficha_id = f"fic-{uuid.uuid4().hex[:8]}"
        ficha = {
            "id": ficha_id,
            "codigo": datos["codigo"].strip(),
            "programa": programa["nombre"],
            "nivel": programa["nivel"],
            "jornada": datos["jornada"],
            "sede": datos["sede"].strip(),
            "municipio": (datos.get("municipio") or "").strip(),
            "instructor_titular_id": datos.get("instructor_titular_id") or "",
            "fecha_inicio": datos["fecha_inicio"],
            "fecha_fin": datos["fecha_fin"],
            "numero_aprendices": datos["numero_aprendices"],
            # El diagnóstico nace copiado del catálogo (con ids propios de la ficha)
            "competencias": [
                {"id": f"c-{uuid.uuid4().hex[:8]}", "nombre": c["nombre"], "tipo": c["tipo"], "horas": c["horas"]}
                for c in programa.get("competencias", [])
            ],
            "archivos": [],
        }
        db["fichas"].append(ficha)
        _guardar_db(db)
    return await obtener_ficha(ficha_id)


# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO DEL INSTRUCTOR (la "matriz por instructor" del Excel)
# ─────────────────────────────────────────────────────────────────────────────





# ─────────────────────────────────────────────────────────────────────────────
# RESPALDO DE ARCHIVOS (los Excel históricos de cada ficha, solo lectura)
# ─────────────────────────────────────────────────────────────────────────────
def _nombre_seguro(valor: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", valor or "archivo")


def _carpeta_ficha(ficha_id: str) -> Path:
    carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


async def agregar_archivo_ficha(ficha_id: str, nombre: str, contenido: bytes) -> list:
    """Guarda un archivo histórico de la ficha (no se modifica: solo respaldo
    descargable) y registra sus metadatos. Devuelve la lista actualizada."""
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
        archivo_id = f"arch-{uuid.uuid4().hex[:8]}"
        nombre_limpio = _nombre_seguro(nombre)
        (_carpeta_ficha(ficha_id) / f"{archivo_id}__{nombre_limpio}").write_bytes(contenido)
        ficha.setdefault("archivos", []).append({
            "id": archivo_id,
            "nombre": nombre,
            "tamano": len(contenido),
            "fecha": datetime.now(_ZONA_BOGOTA).strftime("%Y-%m-%d %H:%M"),
        })
        _guardar_db(db)
        return ficha["archivos"]


def obtener_archivo_ficha(ficha_id: str, archivo_id: str) -> tuple:
    """Devuelve (ruta, nombre_original) del archivo pedido, o 404."""
    db = _cargar_db()
    ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
    meta = next((a for a in ficha.get("archivos", []) if a["id"] == archivo_id), None)
    carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
    coincidencias = sorted(carpeta.glob(f"{_nombre_seguro(archivo_id)}__*")) if carpeta.exists() else []
    if not meta or not coincidencias:
        raise HTTPException(status_code=404, detail="El archivo solicitado no existe en el servidor.")
    return coincidencias[0], meta["nombre"]


async def eliminar_archivo_ficha(ficha_id: str, archivo_id: str) -> dict:
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")
        archivos = ficha.get("archivos", [])
        if not any(a["id"] == archivo_id for a in archivos):
            raise HTTPException(status_code=404, detail="El archivo indicado no existe en la ficha.")
        carpeta = _RUTA_STORAGE / _nombre_seguro(ficha_id)
        for ruta in carpeta.glob(f"{_nombre_seguro(archivo_id)}__*"):
            ruta.unlink(missing_ok=True)
        ficha["archivos"] = [a for a in archivos if a["id"] != archivo_id]
        _guardar_db(db)
        return {"mensaje": "Archivo eliminado del respaldo.", "archivos": ficha["archivos"]}


async def actualizar_diagnostico(ficha_id: str, competencias: list) -> dict:
    """Reemplaza la matriz de competencias de la ficha. Las competencias que ya
    tienen asignaciones en el calendario no se pueden eliminar (409)."""
    if not _es_demo():
        from services.dataverse import consultar_dataverse, crear_registro_dataverse, eliminar_registro_dataverse, actualizar_registro_dataverse
        
        # 1. Obtener competencias actuales
        res_comps = await consultar_dataverse(f"cr6a3_competenciafichas?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        actuales = res_comps.get("value", [])
        
        # 2. Obtener asignaciones de la ficha para ver qué competencias están en uso
        res_asig = await consultar_dataverse(f"cr6a3_asignacioneses?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        asignaciones = res_asig.get("value", [])
        comps_en_uso = {a.get("_cr6a3_competenciafichaid_value") for a in asignaciones if a.get("_cr6a3_competenciafichaid_value")}
        
        ids_nuevos = {c.get("id") for c in competencias if c.get("id")}
        
        # Verificar eliminadas en uso
        eliminadas_en_uso = []
        for c in actuales:
            cid = c.get("cr6a3_competenciafichaid")
            if cid and cid not in ids_nuevos and cid in comps_en_uso:
                eliminadas_en_uso.append(c.get("cr6a3_nombre", "Desconocida"))
                
        if eliminadas_en_uso:
            raise HTTPException(
                status_code=409,
                detail=f"No se pueden eliminar competencias que ya tienen asignaciones: {', '.join(eliminadas_en_uso)}"
            )
            
        # Ejecutar eliminaciones
        for c in actuales:
            cid = c.get("cr6a3_competenciafichaid")
            if cid and cid not in ids_nuevos:
                await eliminar_registro_dataverse(f"cr6a3_competenciafichas({cid})")
                
        # Ejecutar creaciones y actualizaciones
        for c in competencias:
            payload = {
                "cr6a3_nombre": str(c["nombre"]).strip(),
                "cr6a3_tipo": str(c["tipo"]),
                "cr6a3_horas": int(c["horas"])
            }
            if c.get("id"):
                await actualizar_registro_dataverse("cr6a3_competenciafichas", c["id"], payload)
            else:
                payload["cr6a3_FichaId@odata.bind"] = f"/cr6a3_fichas({ficha_id})"
                await crear_registro_dataverse("cr6a3_competenciafichas", payload)
                
        return await obtener_ficha(ficha_id)
        
    _exigir_demo()
