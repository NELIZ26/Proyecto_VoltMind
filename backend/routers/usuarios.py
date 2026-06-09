from fastapi import APIRouter, HTTPException
from services.dataverse import DATAVERSE_URL, consultar_dataverse

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

@router.get("/perfil")
async def obtener_perfil_por_correo(email: str):
    # ✅ URL con el plural exacto exigido por Dataverse
    url = f"{DATAVERSE_URL}/api/data/v9.2/cr6a3_aprendizs?$filter=cr6a3_correo_electronico eq '{email}'"
    
    resultado = await consultar_dataverse(url)
    
    if not resultado or len(resultado.get("value", [])) == 0:
        raise HTTPException(
            status_code=404, 
            detail="El correo de Microsoft no está vinculado a ningún aprendiz en Dataverse."
        )
    
    # Extraemos los datos del aprendiz
    aprendiz_data = resultado["value"][0]
    
    # 🟢 2. Como la ficha es una llave foránea (relación), Dataverse nos devuelve 
    # el texto bonito (el número de ficha) dentro de esta propiedad especial 'FormattedValue'
    ficha_formateada = aprendiz_data.get("_cr6a3_fichavinculad_value@OData.Community.Display.V1.FormattedValue")
    
    # Por si acaso la cabecera FormattedValue falla, guardamos el ID como plan B
    if not ficha_formateada:
        ficha_formateada = aprendiz_data.get("_cr6a3_fichavinculad_value")
    
    return {
        "id": aprendiz_data.get("cr6a3_aprendizid"), 
        "full_name": aprendiz_data.get("cr6a3_nombre_completo"),
        "email": aprendiz_data.get("cr6a3_correo_electronico"),
        "documento": aprendiz_data.get("cr6a3_documento_de_identidad"), 
        "ficha": str(ficha_formateada)
    }