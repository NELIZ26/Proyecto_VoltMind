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
    return date.fromisoformat(valor)


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
            "numero_aprendices": f.get("numero_aprendices", 0),
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
        "numero_aprendices": ficha.get("numero_aprendices", 0),
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
    _exigir_demo()
    return _cargar_db()["instructores"]


async def listar_ambientes() -> list:
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

    fichas_por_id = {f["id"]: f for f in db["fichas"]}
    jornada = ficha.get("jornada", "")

    def cruces_de(campo: str, valor: str) -> list:
        """Asignaciones en la MISMA jornada que se solapan con el rango pedido."""
        resultado = []
        for a in db["asignaciones"]:
            if a["id"] == excluir_asignacion or a[campo] != valor:
                continue
            if fichas_por_id.get(a["ficha_id"], {}).get("jornada") != jornada:
                continue
            if _solapan(inicio, fin, _fecha(a["fecha_inicio"]), _fecha(a["fecha_fin"])):
                resultado.append(a)
        return resultado

    # ¿La propia ficha ya tiene clase en esas fechas? (bloquea a todos)
    ocupada = [
        a for a in db["asignaciones"]
        if a["ficha_id"] == ficha_id and a["id"] != excluir_asignacion
        and _solapan(inicio, fin, _fecha(a["fecha_inicio"]), _fecha(a["fecha_fin"]))
    ]
    ficha_ocupada = None
    if ocupada:
        primera = _enriquecer_asignacion(ocupada[0], db)
        ficha_ocupada = {
            "detalle": f"La ficha ya tiene programado a "
                       f"{(primera['instructor'] or {}).get('nombre', 'un instructor')} del "
                       f"{_formatear(primera['fecha_inicio'])} al {_formatear(primera['fecha_fin'])}.",
        }

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
async def crear_asignacion(datos: dict) -> dict:
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
        return {"mensaje": "Asignaci├│n eliminada de Dataverse."}

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


async def listar_programas() -> list:
    _exigir_demo()
    return [_resumen_programa(p) for p in _cargar_db()["programas"]]


async def crear_programa(datos: dict) -> dict:
    """Registra un programa en el catálogo (nombre + versión únicos)."""
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


async def actualizar_diagnostico(ficha_id: str, competencias: list) -> dict:
    """Reemplaza la matriz de competencias de la ficha. Las competencias que ya
    tienen asignaciones en el calendario no se pueden eliminar (409)."""
    _exigir_demo()
    async with _demo_lock:
        db = _cargar_db()
        ficha = _buscar(db["fichas"], ficha_id, "La ficha titulada")

        ids_nuevos = {c.get("id") for c in competencias if c.get("id")}
        usadas = {a["competencia_id"] for a in db["asignaciones"] if a["ficha_id"] == ficha_id}
        eliminadas_en_uso = [
            c["nombre"] for c in ficha.get("competencias", [])
            if c["id"] in usadas and c["id"] not in ids_nuevos
        ]
        if eliminadas_en_uso:
            raise HTTPException(
                status_code=409,
                detail="No se pueden eliminar competencias que ya tienen asignaciones en el calendario: "
                       f"{', '.join(eliminadas_en_uso)}. Elimine primero esas asignaciones.",
            )

        ficha["competencias"] = [
            {
                "id": c.get("id") or f"c-{uuid.uuid4().hex[:8]}",
                "nombre": c["nombre"].strip(),
                "tipo": c["tipo"],
                "horas": c["horas"],
            }
            for c in competencias
        ]
        _guardar_db(db)
    return await obtener_ficha(ficha_id)


# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO DEL INSTRUCTOR (la "matriz por instructor" del Excel)
# ─────────────────────────────────────────────────────────────────────────────
async def calendario_instructor(instructor_id: str | None = None, correo: str | None = None) -> dict:
    """Programación completa de un instructor (por id o por correo institucional):
    lo que cada instructor consulta en su propia matriz."""
    _exigir_demo()
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
        "modo_demo": _es_demo(),
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
        
        # 2. Obtener asignaciones de la ficha para ver qu├® competencias est├ín en uso
        res_asig = await consultar_dataverse(f"cr6a3_asignacioneses?$filter=_cr6a3_fichaid_value eq '{ficha_id}'")
        asignaciones = res_asig.get("value", [])
        comps_en_uso = {a.get("_cr6a3_competenciaid_value") for a in asignaciones if a.get("_cr6a3_competenciaid_value")}
        
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
