# schemas/fichas.py
from pydantic import BaseModel

class FichaResponse(BaseModel):
    numero_ficha: str
    nombre_programa: str

class AprendizResponse(BaseModel):
    documento_identidad: str
    nombre_completo: str
    correo_electronico: str