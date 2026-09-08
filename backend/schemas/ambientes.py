from pydantic import BaseModel, Field
from typing import Optional

class AmbienteBase(BaseModel):
    cr6a3_nombre_ambiente: str = Field(..., description="Nombre del ambiente")
    cr6a3_cantidad_nodos_electricos: Optional[int] = Field(None, description="Cantidad de nodos eléctricos")
    cr6a3_capacidad_aprendices: Optional[int] = Field(None, description="Capacidad de aprendices")
    cr6a3_direccion_ip_maestra: Optional[str] = Field(None, description="Dirección IP maestra")
    cr6a3_Estado_Ambiente: Optional[int] = Field(430120000, description="Estado: 430120000 (Activo), 430120001 (Mantenimiento), 430120002 (Inactivo)")
    
    # Campo para enlazar a la sede por ID (al crear/editar)
    sede_id: Optional[str] = Field(None, description="ID de la sede a relacionar")

class AmbienteCreate(AmbienteBase):
    pass

class AmbienteUpdate(AmbienteBase):
    cr6a3_nombre_ambiente: Optional[str] = None

class AmbienteResponse(AmbienteBase):
    cr6a3_ambiente_formacionid: str
    sede_nombre: Optional[str] = None
    sede_municipio: Optional[str] = None

    class Config:
        orm_mode = True

class SedeCreate(BaseModel):
    cr6a3_nombre: str = Field(..., description="Nombre de la sede")
    cr6a3_municipio: Optional[str] = Field(None, description="Municipio de la sede")
