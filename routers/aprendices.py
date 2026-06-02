# routers/aprendices.py
from fastapi import APIRouter, HTTPException
from services.aprendices_service import consultar_aprendices_por_ficha

router = APIRouter(
    prefix="/api/fichas",
    tags=["Gestión de Fichas y Aprendices"]
)

@router.get("/{numero_ficha}/aprendices")
async def obtener_relacion_aprendices(numero_ficha: str):
    """
    Endpoint para recuperar el listado de aprendices vinculados a una ficha específica
    al interactuar con la interfaz del frontend.
    """
    try:
        return await consultar_aprendices_por_ficha(numero_ficha)
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        print("ERROR CONTROLADO EN ROUTER:", str(e))
        raise HTTPException(status_code=500, detail="Ocurrió un error inesperado en el servidor.")