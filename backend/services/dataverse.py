# services/dataverse.py
import os
import msal
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Asignar los valores llamando a las variables exactas de tu .env
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID") 
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
DATAVERSE_URL = os.getenv("DATAVERSE_URL")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = [f"{DATAVERSE_URL}/.default"]

app_msal = msal.ConfidentialClientApplication(
    CLIENT_ID, 
    authority=AUTHORITY, 
    client_credential=CLIENT_SECRET
)

def obtener_token_dataverse() -> str:
    """Obtiene el token de acceso de forma silenciosa o por cliente."""
    resultado = app_msal.acquire_token_silent(SCOPES, account=None)
    if not resultado:
        resultado = app_msal.acquire_token_for_client(scopes=SCOPES)
        
    if "access_token" in resultado:
        return resultado["access_token"]
    else:
        error_msg = resultado.get('error_description', 'Error desconocido de MSAL')
        raise Exception(f"Fallo al obtener el token: {error_msg}")

async def cliente_dataverse() -> httpx.AsyncClient:
    """Retorna un cliente HTTP asíncrono con las cabeceras globales de Dataverse."""
    token = obtener_token_dataverse()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": 'odata.include-annotations="*"'
    }
    return httpx.AsyncClient(base_url=f"{DATAVERSE_URL}/api/data/v9.2/", headers=headers)