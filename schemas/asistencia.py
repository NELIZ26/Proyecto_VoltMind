# schemas/asistencia.py
from typing import Optional
from pydantic import BaseModel

class PinCreate(BaseModel):
    rol: str = "aprendiz"
    documento_aprendiz: Optional[str] = None
    identificador: Optional[str] = None # Para el correo institucional del instructor
    nombre: str = "Aprendiz"

class PinValidate(BaseModel):
    pin: str
    sesion_id: str # Opcional: si el aula está apagada, la tablet enviará "N/A" o el ID del aula

class FirmaCreate(BaseModel):
    sesion_id: str
    documento_aprendiz: str
    nombre_aprendiz: str
    firma_base64: str

class CierreSesion(BaseModel):
    sesion_id: str
    numero_ficha: str
    nombre_programa: str
    nombre_instructor: str
    correo_destino: str
    competencia: Optional[str] = ""
    resultado_aprendizaje: Optional[str] = ""

class QrGenerate(BaseModel):
    sesion_id: str

class QrValidate(BaseModel):
    token_qr: str
    documento_aprendiz: str
    rol: str = "aprendiz" # Preparado para cuando implementes el QR