# services/sesiones.py
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum
from services.dataverse import obtener_cliente, sanitizar_odata

class EstadoSesion(int, Enum):
    ACTIVA = 430120000
    FINALIZADA = 430120002

class Jornada(int, Enum):
    MANANA = 430120000
    TARDE = 430120001
    NOCHE = 430120002

async def obtener_sesion_activa_por_email(email: str) -> dict:
    client = obtener_cliente()
    email_seguro = sanitizar_odata(email.lower())
    
    # 1. Buscar el ID del instructor
    url_instructor = f"cr6a3_instructors?$filter=cr6a3_correo_institucional eq '{email_seguro}'&$select=cr6a3_instructorid"
    resp_instructor = await client.get(url_instructor)
    datos_instructor = resp_instructor.json()
    
    if not datos_instructor.get("value"):
        return {"activa": False, "mensaje": "Instructor no encontrado"}
        
    instructor_id = datos_instructor["value"][0]["cr6a3_instructorid"]
    
    # 2. Buscar si tiene una sesión ACTIVA
    # EstadoSesion.ACTIVA.value es 430120000
    url_sesion = (
        f"cr6a3_sesiones_de_clases?$filter=_cr6a3_instructor_value eq '{instructor_id}' "
        f"and cr6a3_estado_de_sesion eq {EstadoSesion.ACTIVA.value}"
        f"&$select=cr6a3_sesiones_de_claseid,cr6a3_hora_entrada,_cr6a3_ficha_value,_cr6a3_ambiente_formacion_value"
        f"&$expand=cr6a3_Ficha($select=cr6a3_numero_ficha)"
    )
    resp_sesion = await client.get(url_sesion)
    datos_sesion = resp_sesion.json()
    
    sesiones = datos_sesion.get("value", [])
    if not sesiones:
        return {"activa": False}
        
    sesion_activa = sesiones[0]
    ficha = sesion_activa.get("cr6a3_Ficha", {})
    
    return {
        "activa": True,
        "sesion_id": sesion_activa.get("cr6a3_sesiones_de_claseid"),
        "hora_entrada": sesion_activa.get("cr6a3_hora_entrada"),
        "ficha_numero": ficha.get("cr6a3_numero_ficha", "Sin Ficha"),
        "ambiente_id": sesion_activa.get("_cr6a3_ambiente_formacion_value", "")
    }

async def registrar_inicio_sesion(ficha: str, email: str, ambiente_id: str = None) -> dict:
    client = obtener_cliente()
    
    # 🛡️ Sanitización estricta de entradas de usuario externas
    email_seguro = sanitizar_odata(email.lower())
    ficha_segura = sanitizar_odata(ficha.strip())
    
    url_instructor = f"cr6a3_instructors?$filter=cr6a3_correo_institucional eq '{email_seguro}'&$select=cr6a3_instructorid"
    resp_instructor = await client.get(url_instructor)
    datos_instructor = resp_instructor.json()
    
    if not datos_instructor.get("value"):
        raise Exception(f"No se encontró al instructor con el correo proporcionado.")
        
    instructor_id = datos_instructor["value"][0]["cr6a3_instructorid"]

    url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{ficha_segura}'&$select=cr6a3_fichaid"
    resp_ficha = await client.get(url_ficha)
    datos_ficha = resp_ficha.json()

    if not datos_ficha.get("value"):
        raise Exception(f"No se encontró la ficha {ficha} en el sistema.")

    ficha_id = datos_ficha["value"][0]["cr6a3_fichaid"]

    zona_colombia = ZoneInfo("America/Bogota")
    hora_entrada_iso = datetime.now(zona_colombia).isoformat()
    
    datos_nueva_sesion = {
        "cr6a3_hora_entrada": hora_entrada_iso,
        "cr6a3_estado_de_sesion": EstadoSesion.ACTIVA.value,
        "cr6a3_consumo_clase_kwh": 0.0,
        "cr6a3_consumo_extra_kwh": 0.0,
        "cr6a3_Instructor@odata.bind": f"/cr6a3_instructors({instructor_id})",
        "cr6a3_Ficha@odata.bind": f"/cr6a3_fichas({ficha_id})"
    }

    if ambiente_id:
        datos_nueva_sesion["cr6a3_Ambiente_Formacion@odata.bind"] = f"/cr6a3_ambiente_formacions({sanitizar_odata(ambiente_id)})"

    respuesta_sesion = await client.post("cr6a3_sesiones_de_clases", json=datos_nueva_sesion)
    
    if respuesta_sesion.status_code == 204: 
        entity_id_url = respuesta_sesion.headers.get("OData-EntityId", "")
        sesion_guid = entity_id_url.split("(")[-1].replace(")", "") if "(" in entity_id_url else ""

        return {
            "mensaje": "Sesión iniciada con éxito", 
            "hora_entrada": hora_entrada_iso,
            "sesion_id": sesion_guid
        }
    else:
        raise Exception("Error al mapear la nueva sesión en Dataverse.")

async def registrar_fin_sesion(sesion_id: str) -> dict:
    client = obtener_cliente()
    sesion_segura = sanitizar_odata(sesion_id)
        
    url_sesion = f"cr6a3_sesiones_de_clases({sesion_segura})?$select=_cr6a3_ficha_value"
    resp_sesion = await client.get(url_sesion)
    datos_sesion = resp_sesion.json()
    ficha_id = datos_sesion.get("_cr6a3_ficha_value")

    if not ficha_id:
        raise Exception("No se pudo identificar la ficha vinculada a esta sesión.")

    url_ficha = f"cr6a3_fichas( {ficha_id} )?$select=cr6a3_jornada"
    resp_ficha = await client.get(url_ficha)
    jornada_valor = resp_ficha.json().get("cr6a3_jornada")

    zona_colombia = ZoneInfo("America/Bogota")
    ahora = datetime.now(zona_colombia)
    hora_salida_iso = ahora.isoformat()
    
    minutos_extra = 0
    hora_limite = ahora
    if jornada_valor:
        if jornada_valor == Jornada.MANANA.value: 
            hora_limite = ahora.replace(hour=12, minute=0, second=0, microsecond=0)
        elif jornada_valor == Jornada.TARDE.value: 
            hora_limite = ahora.replace(hour=17, minute=0, second=0, microsecond=0)
        elif jornada_valor == Jornada.NOCHE.value: 
            hora_limite = ahora.replace(hour=23, minute=0, second=0, microsecond=0)

        if ahora > hora_limite:
            minutos_extra = int((ahora - hora_limite).total_seconds() / 60)

    hora_limite_utc = hora_limite.astimezone(ZoneInfo("UTC"))

    datos_cierre = {
        "cr6a3_hora_salida": hora_salida_iso,
        "cr6a3_estado_de_sesion": EstadoSesion.FINALIZADA.value,
        "cr6a3_tiempo_extra_minutos": minutos_extra
    }

    # NUEVO: Enviar comando a la Raspberry Pi con la hora límite en UTC para SQLite
    from routers.iot import send_serial_command
    comando_cierre = f"CLOSE_SESSION:{sesion_id}:{hora_limite_utc.strftime('%Y-%m-%d %H:%M:%S')}"
    send_serial_command(comando_cierre)

    resp_cierre = await client.patch(f"cr6a3_sesiones_de_clases({sesion_segura})", json=datos_cierre)
    if resp_cierre.status_code == 204: 
        return {
            "mensaje": "Sesión finalizada con éxito", 
            "hora_salida": hora_salida_iso,
            "tiempo_extra": f"{minutos_extra} min" 
        }
    else:
        raise Exception("Fallo al registrar la hora de salida de la sesión.")

async def obtener_ambientes():
    client = obtener_cliente()
    url_ambientes = "cr6a3_ambiente_formacions?$select=cr6a3_ambiente_formacionid,cr6a3_nombre_ambiente"
    resp = await client.get(url_ambientes)
    
    if resp.status_code == 200:
        ambientes = resp.json().get("value", [])
        return [{"id": a["cr6a3_ambiente_formacionid"], "nombre": a["cr6a3_nombre_ambiente"]} for a in ambientes]
    else:
        raise Exception("Fallo en la sincronización de espacios de formación.")