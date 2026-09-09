from pydantic import BaseModel
from typing import Optional

class AprendizCreate(BaseModel):
    cr6a3_tipodocumento: str
    cr6a3_nombres: str
    cr6a3_apellidos: str
    cr6a3_nombre_completo: Optional[str] = None
    cr6a3_documento_de_identidad: str
    cr6a3_correo_electronico: str
    cr6a3_numero_celular: Optional[str] = None
    cr6a3_numero_ficha: str  # Enviamos el número de ficha para buscar su GUID
