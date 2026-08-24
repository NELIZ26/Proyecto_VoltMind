# schemas/tituladas.py
# Modelos Pydantic del módulo de Fichas Tituladas y Asignación de Ambientes
# (digitaliza las matrices de Excel de la programación académica del coordinador).
from datetime import date
from pydantic import BaseModel, Field, field_validator

# Jornadas institucionales SENA: bloques fijos de 6 horas
JORNADAS_TITULADAS = ["Mañana", "Tarde", "Noche"]

# Clasificación de las competencias del diagnóstico (colores en el frontend)
TIPOS_COMPETENCIA = ["Técnica", "Básica", "Transversal", "Inducción"]

# Niveles de formación titulada (catálogo de programas)
NIVELES_FORMACION = ["Operario", "Auxiliar", "Técnico", "Tecnólogo"]


def _validar_fecha_obligatoria(valor: str, campo: str) -> str:
    """La fecha debe ser real y en formato YYYY-MM-DD (422 si no)."""
    try:
        date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{valor}' no es una fecha válida para {campo} (formato esperado YYYY-MM-DD).")
    return valor


class AsignacionTituladaCreate(BaseModel):
    """Una asignación = un rango de días en los que un instructor dicta una
    competencia de la ficha en un ambiente (equivale a pintar celdas en el Excel)."""
    ficha_id: str = Field(min_length=1)
    instructor_id: str = Field(min_length=1)
    competencia_id: str = Field(min_length=1)
    ambiente_id: str = Field(min_length=1)
    fecha_inicio: str
    fecha_fin: str

    @field_validator("fecha_inicio", "fecha_fin")
    @classmethod
    def validar_fechas(cls, v: str, info) -> str:
        return _validar_fecha_obligatoria(v, info.field_name)


class AsignacionTituladaUpdate(BaseModel):
    instructor_id: str | None = None
    competencia_id: str | None = None
    ambiente_id: str | None = None
    fecha_inicio: str | None = None
    fecha_fin: str | None = None

    @field_validator("fecha_inicio", "fecha_fin")
    @classmethod
    def validar_fechas(cls, v: str | None, info) -> str | None:
        if v is None:
            return v
        return _validar_fecha_obligatoria(v, info.field_name)


class CompetenciaDiagnostico(BaseModel):
    """Una fila de la matriz de diagnóstico: competencia + horas + clasificación.
    El `id` solo viene al editar (permite conservar las asignaciones existentes)."""
    id: str | None = None
    nombre: str = Field(min_length=3)
    tipo: str
    horas: int = Field(gt=0, le=2000)

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_COMPETENCIA:
            raise ValueError(f"'{v}' no es un tipo de competencia válido ({', '.join(TIPOS_COMPETENCIA)}).")
        return v

class DiagnosticoUpdate(BaseModel):
    """Payload para actualizar la matriz de competencias (diagnóstico) de la ficha."""
    competencias: list[CompetenciaDiagnostico] = Field(min_length=1)


class ProgramaCreate(BaseModel):
    """Programa del catálogo: al crear una ficha, su diagnóstico se genera desde aquí."""
    nombre: str = Field(min_length=3)
    version: str = Field(min_length=1)
    nivel: str
    competencias: list[CompetenciaDiagnostico] = Field(min_length=1)

    @field_validator("nivel")
    @classmethod
    def validar_nivel(cls, v: str) -> str:
        if v not in NIVELES_FORMACION:
            raise ValueError(f"'{v}' no es un nivel de formación válido ({', '.join(NIVELES_FORMACION)}).")
        return v


class FichaTituladaCreate(BaseModel):
    """Alta de una ficha titulada: el programa (y su matriz de competencias)
    sale del catálogo, cumpliendo el flujo real 'primero el diagnóstico'."""
    codigo: str = Field(min_length=4, max_length=12)
    programa_id: str = Field(min_length=1)
    jornada: str
    sede: str = Field(min_length=3)
    municipio: str = ""
    instructor_titular_id: str | None = None
    fecha_inicio: str
    fecha_fin: str
    numero_aprendices: int = Field(ge=1, le=60)

    @field_validator("jornada")
    @classmethod
    def validar_jornada(cls, v: str) -> str:
        if v not in JORNADAS_TITULADAS:
            raise ValueError(f"'{v}' no es una jornada válida ({', '.join(JORNADAS_TITULADAS)}).")
        return v

    @field_validator("fecha_inicio", "fecha_fin")
    @classmethod
    def validar_fechas(cls, v: str, info) -> str:
        return _validar_fecha_obligatoria(v, info.field_name)
