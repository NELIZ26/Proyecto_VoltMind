from fastapi import APIRouter, HTTPException
# Importamos ÚNICAMENTE el cliente centralizado
from services.dataverse import cliente_dataverse 
# from schemas.fichas import FichaResponse # Descomenta si usas response_model

router = APIRouter(
    prefix="/api/fichas",
    tags=["Fichas y Aprendices"]
)

@router.get("/{correo_instructor}")
async def obtener_fichas_por_instructor(correo_instructor: str):
    try:
        # 🚀 AQUÍ ESTÁ LA MAGIA: Usamos el cliente que ya tiene Token, Headers y URL Base
        async with await cliente_dataverse() as client:
            
            # --- PASO 1: Buscar el instructor (Usando el plural en inglés correcto) ---
            url_instructor = f"cr6a3_instructors?$filter=cr6a3_correo_institucional eq '{correo_instructor}'&$select=cr6a3_instructorid,cr6a3_nombre_completo"
            
            res_instructor = await client.get(url_instructor)

            if res_instructor.status_code != 200:
                print("ERROR DATAVERSE PASO 1:", res_instructor.text)
                raise HTTPException(
                    status_code=res_instructor.status_code, 
                    detail="Error al buscar el instructor en Dataverse"
                )

            datos_instructor = res_instructor.json().get("value", [])

            if not datos_instructor:
                raise HTTPException(status_code=404, detail="Instructor no encontrado en el sistema")

            # Guardamos el ID único del instructor (GUID)
            instructor_id = datos_instructor[0]["cr6a3_instructorid"]

            # --- PASO 2: Buscar las fichas asociadas al instructor ---
            # Verifica en Dataverse si tu tabla de fichas termina en 's' (cr6a3_fichas)
            url_fichas = f"cr6a3_fichas?$filter=_cr6a3_instructorasignado_value eq '{instructor_id}'&$select=cr6a3_numero_ficha,cr6a3_nombre_programa"
            
            res_fichas = await client.get(url_fichas)

            if res_fichas.status_code != 200:
                print("ERROR DATAVERSE PASO 2:", res_fichas.text)
                raise HTTPException(
                    status_code=res_fichas.status_code, 
                    detail="Error al recuperar las fichas de Dataverse"
                )

            datos_fichas = res_fichas.json().get("value", [])

            # --- PASO 3: Formatear respuesta ---
            fichas_mapeadas = [
                {
                    "numero_ficha": ficha.get("cr6a3_numero_ficha"),
                    "nombre_programa": ficha.get("cr6a3_nombre_programa")
                }
                for ficha in datos_fichas
            ]

            return fichas_mapeadas

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        print("ERROR INESPERADO:", str(e))
        raise HTTPException(status_code=500, detail=str(e))