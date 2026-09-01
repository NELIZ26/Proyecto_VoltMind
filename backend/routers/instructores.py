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
    nombre_completo: str
    correo_institucional: str
    nro_documento: Optional[str] = None
    tipo_vinculacion: Optional[str] = "PLANTA"
    perfil_profesional: Optional[str] = None
    nro_telefono: Optional[str] = None
    municipio_contratacion: Optional[str] = None
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

        # Mapeo del payload incorporando solo las columnas existentes en Dataverse
        payload = {
            "cr6a3_nombre_completo": instructor.nombre_completo,
            "cr6a3_correo_institucional": instructor.correo_institucional,
            "cr6a3_nro_documento": instructor.nro_documento,
            "cr6a3_tipo_vinculacion": instructor.tipo_vinculacion,
            "cr6a3_perfil_profesional": instructor.perfil_profesional,
            "cr6a3_nro_telefono": instructor.nro_telefono,
            "cr6a3_municipio_contratacion": instructor.municipio_contratacion,
            "cra5c_fecha_inicio_contrato": instructor.fecha_inicio_contrato,
            "cra5c_fecha_fin_contrato": instructor.fecha_fin_contrato,
        }
        
        # Eliminar nulos antes de enviar a Dataverse (para evitar enviar campos vacíos innecesarios)
        payload = {k: v for k, v in payload.items() if v is not None and v != ""}

        async with httpx.AsyncClient() as client:
            # Verificar si ya existe el instructor
            filter_query = []
            if instructor.nro_documento:
                filter_query.append(f"cr6a3_nro_documento eq '{instructor.nro_documento}'")
            if instructor.correo_institucional:
                filter_query.append(f"cr6a3_correo_institucional eq '{instructor.correo_institucional}'")
            
            if filter_query:
                check_endpoint = f"{DATAVERSE_API_URL}/cr6a3_instructors?$filter={' or '.join(filter_query)}"
                check_response = await client.get(check_endpoint, headers={"Authorization": f"Bearer {token}"})
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    if check_data.get("value") and len(check_data["value"]) > 0:
                        raise HTTPException(
                            status_code=400,
                            detail="Ya existe un instructor registrado con este número de documento o correo institucional."
                        )

            response = await client.post(endpoint, headers=headers, json=payload)

        if response.status_code in [201, 200]:
            data = response.json()
            return data
        
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error de Dataverse al crear instructor: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear instructor en Dataverse: {str(e)}"
        )

# -------------------------------------------------------------
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