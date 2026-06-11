from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

import httpx
from services.dataverse import DATAVERSE_URL, obtener_cliente # Importamos solo el cliente global

# ==========================================
# 🚀 MAPEOS DE DATAVERSE (Elimina Números Mágicos)
# ==========================================
class EstadoSesion(int, Enum):
    ACTIVA = 430120000
    FINALIZADA = 430120002

class Jornada(int, Enum):
    MANANA = 430120000
    TARDE = 430120001
    NOCHE = 430120002

async def registrar_inicio_sesion(ficha: str, email: str, ambiente_id: str = None) -> dict:
    # Llamamos al Singleton
    client = obtener_cliente()
        
    # 1. BUSCAR EL ID DEL INSTRUCTOR
    email_busqueda = email.lower()
    url_instructor = f"cr6a3_instructors?$filter=cr6a3_correo_institucional eq '{email_busqueda}'&$select=cr6a3_instructorid"
    
    # Aseguramos usar 'client' en todo el bloque
    resp_instructor = await client.get(url_instructor)
    datos_instructor = resp_instructor.json()
    
    if not datos_instructor.get("value") or len(datos_instructor["value"]) == 0:
        raise Exception(f"No se encontró al instructor con el correo: {email_busqueda}")
        
    instructor_id = datos_instructor["value"][0]["cr6a3_instructorid"]

    # 2. BUSCAR EL ID DE LA FICHA
    url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{ficha}'&$select=cr6a3_fichaid"
    resp_ficha = await client.get(url_ficha)
    datos_ficha = resp_ficha.json()

    if not datos_ficha.get("value") or len(datos_ficha["value"]) == 0:
        raise Exception(f"No se encontró la ficha {ficha} en la base de datos.")

    ficha_id = datos_ficha["value"][0]["cr6a3_fichaid"]

    # 3. PREPARAR DATOS (Hora de Colombia)
    zona_colombia = ZoneInfo("America/Bogota")
    hora_entrada_iso = datetime.now(zona_colombia).isoformat()
    
    datos_nueva_sesion = {
        "cr6a3_hora_entrada": hora_entrada_iso,
        "cr6a3_estado_de_sesion": EstadoSesion.ACTIVA.value, # Uso del Enum
        "cr6a3_consumo_clase_kwh": 0.0,
        "cr6a3_consumo_extra_kwh": 0.0,
        
        # 4. LOS PUENTES RELACIONALES BÁSICOS
        "cr6a3_Instructor@odata.bind": f"/cr6a3_instructors({instructor_id})",
        "cr6a3_Ficha@odata.bind": f"/cr6a3_fichas({ficha_id})"
    }

    # 🟢 NUEVO: TERCER PUENTE RELACIONAL (Ambiente de Formación)
    # Se enlaza dinámicamente si el ID del ambiente fue seleccionado en la UI
    if ambiente_id:
        datos_nueva_sesion["cr6a3_Ambiente_Formacion@odata.bind"] = f"/cr6a3_ambiente_formacions({ambiente_id})"

    # 5. CREAR LA SESIÓN
    respuesta_sesion = await client.post("cr6a3_sesiones_de_clases", json=datos_nueva_sesion)
    
    if respuesta_sesion.status_code == 204: 
        # Extraemos el GUID de la cabecera OData-EntityId
        entity_id_url = respuesta_sesion.headers.get("OData-EntityId", "")
        sesion_guid = entity_id_url.split("(")[-1].replace(")", "") if "(" in entity_id_url else ""

        return {
            "mensaje": "Sesión iniciada con éxito", 
            "hora_entrada": hora_entrada_iso,
            "sesion_id": sesion_guid
        }

async def registrar_fin_sesion(sesion_id: str) -> dict:
    client = obtener_cliente()
        
    # 1. OBTENER LA FICHA VINCULADA A ESTA SESIÓN
    url_sesion = f"cr6a3_sesiones_de_clases({sesion_id})?$select=_cr6a3_ficha_value"
    resp_sesion = await client.get(url_sesion)
    datos_sesion = resp_sesion.json()
    ficha_id = datos_sesion.get("_cr6a3_ficha_value")

    if not ficha_id:
        raise Exception("No se pudo identificar la ficha vinculada a esta sesión.")

    # 2. CONSULTAR LA JORNADA DE ESA FICHA
    url_ficha = f"cr6a3_fichas({ficha_id})?$select=cr6a3_jornada"
    resp_ficha = await client.get(url_ficha)
    datos_ficha = resp_ficha.json()
    jornada_valor = datos_ficha.get("cr6a3_jornada")

    # 3. PREPARAR HORAS Y CALCULAR TIEMPO EXTRA
    zona_colombia = ZoneInfo("America/Bogota")
    ahora = datetime.now(zona_colombia)
    hora_salida_iso = ahora.isoformat()
    
    minutos_extra = 0
    
    # Solo calculamos si la ficha tiene una jornada asignada
    if jornada_valor:
        hora_limite = ahora
        
        # 🟢 Aplicamos reglas de negocio leyendo el Enum
        if jornada_valor == Jornada.MANANA.value: 
            hora_limite = ahora.replace(hour=12, minute=0, second=0, microsecond=0)
        elif jornada_valor == Jornada.TARDE.value: 
            hora_limite = ahora.replace(hour=17, minute=0, second=0, microsecond=0)
        elif jornada_valor == Jornada.NOCHE.value: 
            hora_limite = ahora.replace(hour=23, minute=0, second=0, microsecond=0)

        # Matemáticas: Si apagaron después del límite, sacamos los minutos de diferencia
        if ahora > hora_limite:
            diferencia = ahora - hora_limite
            minutos_extra = int(diferencia.total_seconds() / 60)

    # 4. GUARDAR EN DATAVERSE
    datos_cierre = {
        "cr6a3_hora_salida": hora_salida_iso,
        "cr6a3_estado_de_sesion": EstadoSesion.FINALIZADA.value, # 🟢 Uso del Enum
        "cr6a3_tiempo_extra_minutos": minutos_extra
    }

    # ACTUALIZAR LA FILA
    resp_cierre = await client.patch(f"cr6a3_sesiones_de_clases({sesion_id})", json=datos_cierre)
    
    if resp_cierre.status_code == 204: 
        return {
            "mensaje": "Sesión finalizada con éxito", 
            "hora_salida": hora_salida_iso,
            "tiempo_extra": f"{minutos_extra} min" 
        }
    else:
        raise Exception(f"Error al cerrar la sesión en Dataverse: {resp_cierre.text}")
    
async def obtener_ambientes():
    """Consulta la tabla Ambiente_Formacion en Dataverse y devuelve la lista."""
    # 1. Usamos tu Singleton (igual que en registrar_inicio_sesion)
    client = obtener_cliente()
    
    # 2. Como el cliente ya tiene el BASE_URL y los headers, solo ponemos la ruta relativa
    # ⚠️ Ajusta 'cr6a3_ambiente_formacions' si Dataverse lo pluralizó diferente
    url_ambientes = "cr6a3_ambiente_formacions?$select=cr6a3_ambiente_formacionid,cr6a3_nombre_ambiente"
    
    # 3. Hacemos la petición
    resp = await client.get(url_ambientes)
    
    if resp.status_code == 200:
        datos = resp.json()
        ambientes = datos.get("value", [])
        return [{"id": a["cr6a3_ambiente_formacionid"], "nombre": a["cr6a3_nombre_ambiente"]} for a in ambientes]
    else:
        raise Exception(f"Fallo al consultar ambientes: {resp.text}")