import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import httpx
from services.dataverse import obtener_token_dataverse

BASE_DATAVERSE_URL = os.getenv("DATAVERSE_URL", "")
DATAVERSE_API_URL = f"{BASE_DATAVERSE_URL}/api/data/v9.2"

router = APIRouter(
    prefix="/api/instructores",
    tags=["Instructores"]
)

# Modelo Pydantic para recibir los datos del formulario Vue
class InstructorSchema(BaseModel):
    nombre: str
    correo: str
    documento: Optional[str] = None
    telefono: Optional[str] = None
    area_especialidad: Optional[str] = None
    tipo_vinculacion: Optional[str] = "PLANTA"
    max_horas_mensuales: Optional[int] = 160
    jornada: Optional[str] = "Mañana"
    # Se agregan los campos de fecha de contrato
    fecha_inicio_contrato: Optional[str] = None
    fecha_fin_contrato: Optional[str] = None

# -------------------------------------------------------------
# Endpoint GET para obtener la lista desde Dataverse
# -------------------------------------------------------------
@router.get("", status_code=status.HTTP_200_OK)
async def obtener_instructores():
    try:
        token = obtener_token_dataverse()
        endpoint = f"{DATAVERSE_API_URL}/cr6a3_instructors"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return data.get("value", [])
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar Dataverse: {str(e)}"
        )

# -------------------------------------------------------------
# Endpoint POST (Crear)
# -------------------------------------------------------------
# ---------------------------------------------------------
# Endpoint POST (Crear)
# ---------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_instructor(instructor: InstructorSchema):
    try:
        token = obtener_token_dataverse()
        endpoint = f"{DATAVERSE_API_URL}/cr6a3_instructors"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        payload = {
            "cr6a3_nombre_completo": instructor.nombre,
            "cr6a3_correo_institucional": instructor.correo,
            "cra5c_fecha_inicio_contrato": instructor.fecha_inicio_contrato,
            "cra5c_fecha_fin_contrato": instructor.fecha_fin_contrato,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload
            )

            print("STATUS DATAVERSE:", response.status_code)
            print("HEADERS DATAVERSE:", dict(response.headers))
            print("BODY DATAVERSE:", repr(response.text))

        if response.status_code in [200, 201]:
            try:
                data = response.json()
            except ValueError:
                data = {}

            return data

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error de Dataverse al crear instructor: {response.text}"
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear instructor en Dataverse: {str(e)}"
        )
        
# ----------------------------------------- --------------------
# Endpoint DELETE (Eliminar)
# -------------------------------------------------------------
@router.delete("/{instructor_id}", status_code=status.HTTP_200_OK)
async def eliminar_instructor(instructor_id: str):
    try:
        token = obtener_token_dataverse()
        endpoint = f"{DATAVERSE_API_URL}/cr6a3_instructors({instructor_id})"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "If-Match": "*"
        }

        async with httpx.AsyncClient() as client:
            response = await client.delete(endpoint, headers=headers)

            if response.status_code in [204, 200]:
                return {"status": "success", "message": f"Instructor {instructor_id} eliminado de Dataverse"}
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Instructor no encontrado en Dataverse")
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en Dataverse: {str(e)}"
        )