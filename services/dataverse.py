# services/dataverse.py
from email.utils import quote
import os
import msal
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

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

# 🚀 NUEVO: Interceptor de Autenticación
class DataverseAuth(httpx.Auth):
    """Inyecta el token y las cabeceras requeridas en cada petición HTTP de forma dinámica."""
    def auth_flow(self, request: httpx.Request):
        token = obtener_token_dataverse()
        request.headers["Authorization"] = f"Bearer {token}"
        request.headers["Accept"] = "application/json"
        request.headers["OData-MaxVersion"] = "4.0"
        request.headers["OData-Version"] = "4.0"
        request.headers["Prefer"] = 'odata.include-annotations="*"'
        yield request

# 🚀 NUEVO: Cliente Singleton Global
# Se instancia una sola vez cuando arranca FastAPI
_cliente_dataverse_global = httpx.AsyncClient(
    base_url=f"{DATAVERSE_URL}/api/data/v9.2/",
    auth=DataverseAuth(),
    timeout=15.0  # Buena práctica: evitar que peticiones huérfanas bloqueen el servidor
)

def obtener_cliente() -> httpx.AsyncClient:
    """Retorna la instancia global del cliente HTTP."""
    return _cliente_dataverse_global

# Adaptación de la función existente
async def consultar_dataverse(query: str) -> dict:
    # Ahora usamos el cliente global sin cerrarlo
    client = obtener_cliente()
    try:
        response = await client.get(query)
        response.raise_for_status() 
        return response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Error HTTP de Dataverse al pedir {query}: {exc.response.text}")
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail="Fallo en la consulta a la base de datos de Dataverse."
        )
    except Exception as exc:
        print(f"Error inesperado conectando con Dataverse: {exc}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor al conectar con Dataverse."
        )

def sanitizar_odata(texto: str) -> str:
    """
    Limpia el texto ingresado por el usuario para evitar inyecciones OData.
    1. Duplica las comillas simples para neutralizarlas.
    2. Codifica el texto a formato URL (%20, etc.).
    """
    if not texto:
        return ""
        
    texto_limpio = texto.replace("'", "''")
    return quote(texto_limpio)