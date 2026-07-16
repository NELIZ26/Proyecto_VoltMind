# schemas/complementarias.py
# Modelos Pydantic del módulo de Fichas Complementarias
# (seguimiento de solicitudes de formación complementaria — reemplaza la matriz de Excel).
from datetime import date
from pydantic import BaseModel, Field, field_validator

# "Pendiente" = solicitud recién enviada por el instructor, aún sin gestión del admin
ESTADOS_SOLICITUD = ["Pendiente", "Publicada", "En Ejecución", "Cancelada"]


def _validar_fecha_opcional(valor: str, campo: str) -> str:
    """Acepta vacío o una fecha real YYYY-MM-DD; rechaza fechas imposibles (422)."""
    if not valor:
        return valor
    try:
        date.fromisoformat(valor)
    except ValueError:
        raise ValueError(f"'{valor}' no es una fecha válida para {campo} (formato esperado YYYY-MM-DD).")
    return valor


class SolicitudComplementariaCreate(BaseModel):
    # ── Solicitante (instructor) ──
    nombre_instructor: str = Field(min_length=3, max_length=120)
    correo_instructor: str = Field(default="", max_length=120)
    celular_instructor: str = Field(default="", max_length=20)

    # ── Programa ──
    codigo_programa: str = Field(min_length=1, max_length=20)
    version_programa: str = Field(default="1", max_length=10)
    nombre_programa: str = Field(min_length=3, max_length=180)
    duracion_horas: int = Field(default=0, ge=0, le=880)

    # ── Fechas ──
    fecha_inicio_inscripcion: str = ""
    fecha_cierre_inscripcion: str = ""
    fecha_inicio_formacion: str = ""
    fecha_fin_formacion: str = ""

    # ── Logística ──
    jornada: str = ""
    municipio: str = Field(default="", max_length=60)
    lugar_ejecucion: str = Field(default="", max_length=180)

    # ── Documentos (enlaces) ──
    enlace_carta_empresa: str = ""
    enlace_formato_solicitud: str = ""
    enlace_matriz_ficha: str = ""
    enlace_archivo_plano: str = ""
    enlaces_pdf: list[str] = []

    # ── Seguimiento ──
    codigo_empresa: str = Field(default="", max_length=30)
    codigo_ficha: str = Field(default="", max_length=15)
    publicacion: bool = False
    asignar_ficha: bool = False
    gestion_ficha: bool = False
    proceso_matricula: bool = False
    estado: str = "Publicada"
    enlace_lista_matriculados: str = ""
    observaciones: str = Field(default="", max_length=1000)

    # ── Inscritos ──
    cantidad_inscritos: int = Field(default=0, ge=0, le=500)

    # ── Archivos subidos (metadatos gestionados por el servidor) ──
    # Cada elemento: {"campo": "matriz"|"plano"|"adicional", "nombre": str, "tamano": int}
    archivos: list[dict] = []

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str) -> str:
        if v not in ESTADOS_SOLICITUD:
            raise ValueError(f"El estado '{v}' no es válido. Use uno de: {', '.join(ESTADOS_SOLICITUD)}.")
        return v

    @field_validator(
        "fecha_inicio_inscripcion", "fecha_cierre_inscripcion",
        "fecha_inicio_formacion", "fecha_fin_formacion",
    )
    @classmethod
    def validar_fechas(cls, v: str, info) -> str:
        return _validar_fecha_opcional(v, info.field_name)


class SolicitudComplementariaUpdate(BaseModel):
    nombre_instructor: str | None = None
    correo_instructor: str | None = None
    celular_instructor: str | None = None
    codigo_programa: str | None = None
    version_programa: str | None = None
    nombre_programa: str | None = None
    duracion_horas: int | None = Field(default=None, ge=0, le=880)
    fecha_inicio_inscripcion: str | None = None
    fecha_cierre_inscripcion: str | None = None
    fecha_inicio_formacion: str | None = None
    fecha_fin_formacion: str | None = None
    jornada: str | None = None
    municipio: str | None = None
    lugar_ejecucion: str | None = None
    enlace_carta_empresa: str | None = None
    enlace_formato_solicitud: str | None = None
    enlace_matriz_ficha: str | None = None
    enlace_archivo_plano: str | None = None
    enlaces_pdf: list[str] | None = None
    codigo_empresa: str | None = None
    codigo_ficha: str | None = None
    publicacion: bool | None = None
    asignar_ficha: bool | None = None
    gestion_ficha: bool | None = None
    proceso_matricula: bool | None = None
    estado: str | None = None
    enlace_lista_matriculados: str | None = None
    observaciones: str | None = None
    cantidad_inscritos: int | None = Field(default=None, ge=0, le=500)

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str | None) -> str | None:
        if v is not None and v not in ESTADOS_SOLICITUD:
            raise ValueError(f"El estado '{v}' no es válido. Use uno de: {', '.join(ESTADOS_SOLICITUD)}.")
        return v

    @field_validator(
        "fecha_inicio_inscripcion", "fecha_cierre_inscripcion",
        "fecha_inicio_formacion", "fecha_fin_formacion",
    )
    @classmethod
    def validar_fechas(cls, v: str | None, info) -> str | None:
        if v is None:
            return v
        return _validar_fecha_opcional(v, info.field_name)
