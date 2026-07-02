from fastapi import APIRouter, HTTPException
from services.dataverse import DATAVERSE_URL, consultar_dataverse, sanitizar_odata

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

@router.get("/perfil")
async def obtener_perfil_por_correo(email: str):
    # 1. Sanitizar la variable primero
    email_seguro = sanitizar_odata(email)
    
    # 2. Construir la URL completa una sola vez
    url = f"{DATAVERSE_URL}/api/data/v9.2/cr6a3_aprendizs?$filter=cr6a3_correo_electronico eq '{email_seguro}'"
    
    resultado = await consultar_dataverse(url)
    
    # 3. Validación más directa (estilo Pythonic)
    if not resultado or not resultado.get("value"):
        raise HTTPException(
            status_code=404, 
            detail="El correo de Microsoft no está vinculado a ningún aprendiz en Dataverse."
        )
    
    aprendiz_data = resultado["value"][0]
    
    # 4. Uso de "or" para asignar la ficha formateada o su ID de respaldo en una sola línea
    ficha_formateada = (
        aprendiz_data.get("_cr6a3_fichavinculad_value@OData.Community.Display.V1.FormattedValue") or 
        aprendiz_data.get("_cr6a3_fichavinculad_value")
    )
    
    return {
        "id": aprendiz_data.get("cr6a3_aprendizid"), 
        "full_name": aprendiz_data.get("cr6a3_nombre_completo"),
        "email": aprendiz_data.get("cr6a3_correo_electronico"),
        "documento": aprendiz_data.get("cr6a3_documento_de_identidad"), 
        # 5. Prevenir que str(None) devuelva el texto "None"
        "ficha": str(ficha_formateada) if ficha_formateada else None
    }