from datetime import datetime
from zoneinfo import ZoneInfo
from services.dataverse import cliente_dataverse

async def registrar_inicio_sesion(ficha: str, email: str) -> dict:
    
    async with await cliente_dataverse() as cliente:
        
        # 1. BUSCAR EL ID DEL INSTRUCTOR
        email_busqueda = email.lower()
        url_instructor = f"cr6a3_instructors?$filter=cr6a3_correo_institucional eq '{email_busqueda}'&$select=cr6a3_instructorid"
        resp_instructor = await cliente.get(url_instructor)
        datos_instructor = resp_instructor.json()
        
        if not datos_instructor.get("value") or len(datos_instructor["value"]) == 0:
            raise Exception(f"No se encontró al instructor con el correo: {email_busqueda}")
            
        instructor_id = datos_instructor["value"][0]["cr6a3_instructorid"]

        # 2. NUEVO: BUSCAR EL ID DE LA FICHA
        url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{ficha}'&$select=cr6a3_fichaid"
        resp_ficha = await cliente.get(url_ficha)
        datos_ficha = resp_ficha.json()

        if not datos_ficha.get("value") or len(datos_ficha["value"]) == 0:
            raise Exception(f"No se encontró la ficha {ficha} en la base de datos.")

        ficha_id = datos_ficha["value"][0]["cr6a3_fichaid"]

        # 3. PREPARAR DATOS (Hora de Colombia)
        zona_colombia = ZoneInfo("America/Bogota")
        hora_entrada_iso = datetime.now(zona_colombia).isoformat()
        
        datos_nueva_sesion = {
            "cr6a3_hora_entrada": hora_entrada_iso,
            "cr6a3_estado_de_sesion": 430120000, 
            "cr6a3_consumo_clase_kwh": 0.0,
            "cr6a3_consumo_extra_kwh": 0.0,
            
            # 4. LOS DOS PUENTES RELACIONALES (Instructor y Ficha)
            "cr6a3_Instructor@odata.bind": f"/cr6a3_instructors({instructor_id})",
            "cr6a3_Ficha@odata.bind": f"/cr6a3_fichas({ficha_id})"
        }

        # 5. CREAR LA SESIÓN
        respuesta_sesion = await cliente.post("cr6a3_sesiones_de_clases", json=datos_nueva_sesion)
        
        if respuesta_sesion.status_code == 204: 
            # Extraemos el GUID de la cabecera OData-EntityId
            entity_id_url = respuesta_sesion.headers.get("OData-EntityId", "")
            # Esto corta el texto para quedarse solo con lo que está dentro de los paréntesis: (...)
            sesion_guid = entity_id_url.split("(")[-1].replace(")", "") if "(" in entity_id_url else ""

            return {
                "mensaje": "Sesión iniciada con éxito", 
                "hora_entrada": hora_entrada_iso,
                "sesion_id": sesion_guid  # <-- LE ENVIAMOS EL ID REAL A VUE
            }

async def registrar_fin_sesion(sesion_id: str) -> dict:
    async with await cliente_dataverse() as cliente:
        
        # 1. OBTENER LA FICHA VINCULADA A ESTA SESIÓN
        url_sesion = f"cr6a3_sesiones_de_clases({sesion_id})?$select=_cr6a3_ficha_value"
        resp_sesion = await cliente.get(url_sesion)
        datos_sesion = resp_sesion.json()
        ficha_id = datos_sesion.get("_cr6a3_ficha_value")

        if not ficha_id:
            raise Exception("No se pudo identificar la ficha vinculada a esta sesión.")

        # 2. CONSULTAR LA JORNADA DE ESA FICHA
        url_ficha = f"cr6a3_fichas({ficha_id})?$select=cr6a3_jornada"
        resp_ficha = await cliente.get(url_ficha)
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
            
            # Aplicamos tus reglas de negocio basándonos en los valores numéricos
            if jornada_valor == 430120000: # Mañana (Límite 12:00 PM)
                hora_limite = ahora.replace(hour=12, minute=0, second=0, microsecond=0)
            elif jornada_valor == 430120001: # Tarde (Límite 5:00 PM / 17:00)
                hora_limite = ahora.replace(hour=17, minute=0, second=0, microsecond=0)
            elif jornada_valor == 430120002: # Noche (Límite 11:00 PM / 23:00)
                hora_limite = ahora.replace(hour=23, minute=0, second=0, microsecond=0)

            # Matemáticas: Si apagaron después del límite, sacamos los minutos de diferencia
            if ahora > hora_limite:
                diferencia = ahora - hora_limite
                minutos_extra = int(diferencia.total_seconds() / 60)

        # 4. GUARDAR EN DATAVERSE
        datos_cierre = {
            "cr6a3_hora_salida": hora_salida_iso,
            "cr6a3_estado_de_sesion": 430120002, 
            "cr6a3_tiempo_extra_minutos": minutos_extra # <-- Inyectamos el cálculo numérico
        }

        # ACTUALIZAR LA FILA
        resp_cierre = await cliente.patch(f"cr6a3_sesiones_de_clases({sesion_id})", json=datos_cierre)
        
        if resp_cierre.status_code == 204: 
            return {
                "mensaje": "Sesión finalizada con éxito", 
                "hora_salida": hora_salida_iso,
                "tiempo_extra": f"{minutos_extra} min" # Lo enviamos formateado para Vue
            }
        else:
            raise Exception(f"Error al cerrar la sesión en Dataverse: {resp_cierre.text}")