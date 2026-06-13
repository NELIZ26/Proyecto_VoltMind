import os
import base64
from datetime import datetime
from fastapi import HTTPException, status
import httpx
# 🟢 ESTA ES LA ÚNICA LÍNEA DE LOG QUE DEBES USAR:
from core.logger import log

# Configuración de la ruta de almacenamiento físico
CARPETA_FIRMAS = os.path.join("storage", "firmas")
os.makedirs(CARPETA_FIRMAS, exist_ok=True)

async def procesar_cierre_y_persistencia(sesion_id: str, numero_ficha: str, lista_firmas_hoy: list):
    """
    Procesa la asistencia total de la clase, guarda las firmas en disco 
    y actualiza el estado de deserción y faltas en Dataverse.
    """
    # 1. OBTENER TODOS LOS APRENDICES DE ESTA FICHA DESDE DATAVERSE
    # Necesitamos la lista completa para saber quiénes NO asistieron hoy.
    aprendices_totales = await obtener_aprendices_por_ficha_dataverse(numero_ficha)
    
    if not aprendices_totales:
        log.warning(f"No se encontraron aprendices matriculados en la ficha {numero_ficha}")
        return

    # Mapeamos las firmas de hoy por documento para búsquedas ultra rápidas O(1)
    dict_firmas_hoy = {str(f["documento"]): f for f in lista_firmas_hoy}

    # 2. ITERAR LA LISTA MAESTRA DE APRENDICES
    for aprendiz in aprendices_totales:
        documento = str(aprendiz["documento"])
        id_aprendiz_dataverse = aprendiz["id_dataverse"] # El GUID de la fila del aprendiz
        
        faltas_totales = aprendiz.get("faltas_totales", 0)
        faltas_consecutivas = aprendiz.get("faltas_consecutivas", 0)
        
        asistio = documento in dict_firmas_hoy

        if asistio:
            # 🟢 CASO A: EL APRENDIZ ASISTIÓ
            datos_firma = dict_firmas_hoy[documento]
            
            # 🚀 AQUÍ ESTÁ EL FIX: Usamos la llave exacta de Redis
            base64_crudo = datos_firma["firma_b64"] 
            
            # Convertir Base64 a archivo físico .png
            nombre_archivo_firma = f"Ficha_{numero_ficha}_{documento}_{datetime.now().strftime('%Y%m%d')}.png"
            ruta_fisica = os.path.join(CARPETA_FIRMAS, nombre_archivo_firma)
            
            try:
                if "," in base64_crudo:
                    base64_crudo = base64_crudo.split(",")[1]
                
                with open(ruta_fisica, "wb") as fh:
                    fh.write(base64.b64decode(base64_crudo))
                    
                nombre_registro_firma = nombre_archivo_firma
            except Exception as e:
                log.error(f"Error guardando archivo de firma para {documento}: {e}")
                nombre_registro_firma = "ERROR_AL_GUARDAR"

            # 🚀 FIX DATAVERSE: Usamos el código de la Opción "Presente"
            estado_asistencia = 430120000 
            nuevas_faltas_consecutivas = 0
            nuevas_faltas_totales = faltas_totales

        else:
            # 🔴 CASO B: EL APRENDIZ FALTÓ (AUSENTE)
            # 🚀 FIX DATAVERSE: Usamos el código de la Opción "Ausente"
            estado_asistencia = 430120001 
            nombre_registro_firma = "X" 
            
            nuevas_faltas_consecutivas = (faltas_consecutivas or 0) + 1
            nuevas_faltas_totales = (faltas_totales or 0) + 1
            
            await evaluar_alertas_desercion(aprendiz, nuevas_faltas_consecutivas, numero_ficha)

        # 3. GUARDAR EL REGISTRO DE ASISTENCIA DIARIO EN DATAVERSE
        payload_asistencia = {
            # Datos nativos de la tabla de asistencia
            "cr6a3_registro_de_asistencia": estado_asistencia, 
            "cr6a3_firma_digital": nombre_registro_firma,
            "cr6a3_hora_firma": datetime.now().isoformat(),
            "cr6a3_Aprendiz@odata.bind": f"/cr6a3_aprendizs({id_aprendiz_dataverse})",
            "cr6a3_Sesiones_de_Clase@odata.bind": f"/cr6a3_sesiones_de_clases({sesion_id})"
        }
        await registrar_fila_asistencia_dataverse(payload_asistencia)

        if nuevas_faltas_consecutivas != faltas_consecutivas or nuevas_faltas_totales != faltas_totales:
            payload_aprendiz = {
                "cr6a3_faltas_totales": nuevas_faltas_totales,
                "cr6a3_faltas_consecutivas": nuevas_faltas_consecutivas
            }
            await actualizar_contadores_aprendiz_dataverse(id_aprendiz_dataverse, payload_aprendiz)


async def evaluar_alertas_desercion(aprendiz: dict, faltas_consecutivas: int, numero_ficha: str):
    """
    Analiza el historial del aprendiz en tiempo real y emite notificaciones
    preventivas o críticas si se vulnera la continuidad formativa.
    """
    nombre = aprendiz.get("nombre", "Aprendiz Desconocido")
    
    if faltas_consecutivas == 3:
        # Alerta Preventiva: Se carga al recuadro del Dashboard del instructor
        payload_alerta = {
            "cr6a3_severidad": "warning",
            "cr6a3_mensaje": f"Alerta Preventiva: {nombre} acumula 3 faltas consecutivas.",
            "cr6a3_ficha": numero_ficha,
            "cr6a3_origen": "Asistencia Automatizada"
        }
        await crear_alerta_en_dataverse(payload_alerta)
        log.info(f"Alerta amarilla emitida para {nombre} de la ficha {numero_ficha}")

    elif faltas_consecutivas >= 4:
        # Alerta Crítica: El aprendiz ha superado el límite permitido por reglamento
        payload_alerta = {
            "cr6a3_severidad": "critical",
            "cr6a3_mensaje": f"Deserción Detectada: {nombre} tiene {faltas_consecutivas} faltas consecutivas. Proceso de comité requerido.",
            "cr6a3_ficha": numero_ficha,
            "cr6a3_origen": "Asistencia Automatizada"
        }
        await crear_alerta_en_dataverse(payload_alerta)
        log.error(f"Alerta roja crítica emitida para {nombre}. Proceso de deserción activado.")



# Asumimos que tienes una función base para hacer peticiones HTTP a Dataverse
# from core.dataverse_client import consultar_dataverse 


async def obtener_asistencia_semanal_dataverse(numero_ficha: str, lunes_inicio: datetime, viernes_fin: datetime):
    """
    Consulta el histórico de Dataverse de una semana específica y
    construye una matriz de asistencia agrupada por aprendiz.
    """
    
    # 1. FORMATEO DE FECHAS PARA DATAVERSE (OData ISO 8601)
    fecha_inicio_iso = lunes_inicio.strftime("%Y-%m-%dT00:00:00Z")
    fecha_fin_iso = viernes_fin.strftime("%Y-%m-%dT23:59:59Z")
    
    log.info(f"Consultando matriz semanal para ficha {numero_ficha} desde {fecha_inicio_iso} hasta {fecha_fin_iso}")

    # 2. CONSULTA A DATAVERSE
    # (Ajusta los nombres de las tablas y columnas según cómo las tengas en Dataverse)
    # Aquí pedimos la asistencia, expandiendo los datos del Aprendiz y de la Sesión para saber la fecha.
    query = (
        f"cr6a3_registro_asistencias?"
        f"$expand=cr6a3_Aprendiz($select=cr6a3_documento,cr6a3_nombre),"
        f"cr6a3_Sesiones_de_Clase($select=cr6a3_fecha_hora_inicio)&$filter="
        f"(cr6a3_Sesiones_de_Clase/cr6a3_ficha eq '{numero_ficha}' and "
        f"cr6a3_Sesiones_de_Clase/cr6a3_fecha_hora_inicio ge {fecha_inicio_iso} and "
        f"cr6a3_Sesiones_de_Clase/cr6a3_fecha_hora_inicio le {fecha_fin_iso})"
    )
    
    # respuesta_dataverse = await consultar_dataverse("GET", query)
    # registros_crudos = respuesta_dataverse.get("value", [])
    
    # ⚠️ SIMULACIÓN DE DATOS (Mientras conectas tu cliente HTTP real)
    registros_crudos = [] 

    # 3. CONSTRUCCIÓN DE LA MATRIZ (El "Cerebro" del PDF)
    # Estructura: { "100234": { "nombre": "Juan", "Lunes": "X", "Martes": "firma.png", ... } }
    matriz_aprendices = {}
    
    # Diccionario para traducir el número del día de Python al texto del PDF
    dias_semana = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes"}

    for fila in registros_crudos:
        # Extraemos la información de la fila
        doc_aprendiz = fila["cr6a3_Aprendiz"]["cr6a3_documento"]
        nombre_aprendiz = fila["cr6a3_Aprendiz"]["cr6a3_nombre"]
        estado_asistencia = fila["cr6a3_Estado_Asistencia"] # 1: Presente, 2: Ausente
        firma = fila["cr6a3_Firma_Digital"] # Nombre del archivo PNG o "X"
        
        # Averiguamos qué día de la semana fue esta clase
        fecha_sesion_str = fila["cr6a3_Sesiones_de_Clase"]["cr6a3_fecha_hora_inicio"]
        fecha_sesion_obj = datetime.fromisoformat(fecha_sesion_str.replace("Z", "+00:00"))
        nombre_dia = dias_semana.get(fecha_sesion_obj.weekday())

        # Ignorar si por alguna razón extraña hubo clase sábado o domingo (5 y 6)
        if not nombre_dia:
            continue

        # Si el aprendiz no existe en nuestra matriz, lo creamos con todos los días vacíos
        if doc_aprendiz not in matriz_aprendices:
            matriz_aprendices[doc_aprendiz] = {
                "documento": doc_aprendiz,
                "nombre": nombre_aprendiz,
                "Lunes": "",
                "Martes": "",
                "Miércoles": "",
                "Jueves": "",
                "Viernes": ""
            }

        # Llenamos la celda del día correspondiente
        # Si estuvo presente, mandamos el nombre de la imagen; si faltó, mandamos una X
        if estado_asistencia == 1 and firma:
            matriz_aprendices[doc_aprendiz][nombre_dia] = firma 
        else:
            matriz_aprendices[doc_aprendiz][nombre_dia] = "X"

    # 4. DEVOLVER LA MATRIZ COMO LISTA
    # Convertimos el diccionario a una lista limpia para que el generador de PDF la pueda recorrer
    lista_final_pdf = list(matriz_aprendices.values())
    
    # Ordenamos alfabéticamente por nombre, tal como lo exige el SENA
    lista_final_pdf.sort(key=lambda x: x["nombre"])

    return lista_final_pdf


# ==========================================
# 🔌 CONECTORES CON LA API DE DATAVERSE
# ==========================================

# 🟢 IMPORTAMOS TU CLIENTE GLOBAL DIRECTAMENTE
from services.dataverse import obtener_cliente


async def obtener_aprendices_por_ficha_dataverse(numero_ficha: str) -> list:
    """
    Busca en Dataverse todos los aprendices matriculados en una ficha operativa.
    Usa la lógica de 2 pasos probada en producción.
    """
    client = obtener_cliente()
    numero_limpio = numero_ficha.strip()

    try:
        # PASO 1: Buscar el GUID interno de la ficha
        url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{numero_limpio}'&$select=cr6a3_fichaid"
        res_ficha = await client.get(url_ficha)
        res_ficha.raise_for_status()
        
        datos_ficha = res_ficha.json().get("value", [])
        if not datos_ficha:
            log.warning(f"La ficha {numero_limpio} no existe en Dataverse.")
            return []
            
        ficha_id = datos_ficha[0]["cr6a3_fichaid"]

        # PASO 2: Buscar los aprendices vinculados a esa ficha
        columnas = (
            "cr6a3_aprendizid," # El GUID interno (Lo necesitamos para el parche de faltas)
            "cr6a3_documento_de_identidad,"
            "cr6a3_nombre_completo,"
            "cr6a3_faltas_totales,"       # <-- ¡Asegúrate de que este nombre lógico sea así!
            "cr6a3_faltas_consecutivas"   # <-- ¡Asegúrate de que este nombre lógico sea así!
        )
        url_aprendices = f"cr6a3_aprendizs?$filter=_cr6a3_fichavinculad_value eq '{ficha_id}'&$select={columnas}"
        
        res_aprendices = await client.get(url_aprendices)
        res_aprendices.raise_for_status()
        datos_aprendices = res_aprendices.json().get("value", [])

        # Mapeamos los datos al formato que nuestro motor de asistencia entiende
        aprendices = []
        for ap in datos_aprendices:
            aprendices.append({
                "id_dataverse": ap.get("cr6a3_aprendizid"), 
                "documento": ap.get("cr6a3_documento_de_identidad"),
                "nombre": ap.get("cr6a3_nombre_completo"),
                "faltas_totales": ap.get("cr6a3_faltas_totales", 0),
                "faltas_consecutivas": ap.get("cr6a3_faltas_consecutivas", 0)
            })
        return aprendices

    except httpx.HTTPStatusError as exc:
        log.error(f"Error HTTP de Dataverse al buscar alumnos: {exc.response.text}")
        return []
    except Exception as e:
        log.error(f"Fallo inesperado consultando aprendices: {e}")
        return []

async def registrar_fila_asistencia_dataverse(payload: dict):
    """
    Crea un nuevo registro en la tabla intermedia de asistencias.
    """
    client = obtener_cliente()
    try:
        # 🚀 AQUI CORREGIMOS EL NOMBRE EXACTO (agregamos el "_de_")
        response = await client.post("cr6a3_registro_de_asistencias", json=payload)
        response.raise_for_status()
        log.info("✅ Registro de asistencia guardado en Dataverse con éxito.")
    except httpx.HTTPStatusError as exc:
        log.error(f"❌ Error Dataverse (Asistencia): {exc.response.text}")
    except Exception as e:
        log.error(f"❌ Fallo de red al registrar asistencia: {e}")


async def actualizar_contadores_aprendiz_dataverse(id_aprendiz: str, payload: dict):
    """
    Actualiza (PATCH) las faltas de un aprendiz específico.
    """
    client = obtener_cliente()
    try:
        # Apuntamos a la tabla de aprendices y al GUID específico
        endpoint = f"cr6a3_aprendizs({id_aprendiz})"
        response = await client.patch(endpoint, json=payload)
        response.raise_for_status()
        log.info(f"✅ Contadores actualizados para el aprendiz {id_aprendiz}.")
    except httpx.HTTPStatusError as exc:
        log.error(f"❌ Error Dataverse (Faltas): {exc.response.text}")
    except Exception as e:
        log.error(f"❌ Fallo de red al actualizar faltas: {e}")


async def crear_alerta_en_dataverse(payload: dict):
    """
    Registra una notificación en la tabla de alertas.
    """
    client = obtener_cliente()
    try:
        # Asumimos que el plural lógico es cr6a3_alertas_sistemas
        response = await client.post("cr6a3_alertas_sistemas", json=payload)
        response.raise_for_status()
        log.info("✅ Alerta de deserción registrada en Dataverse.")
    except httpx.HTTPStatusError as exc:
        log.error(f"❌ Error Dataverse (Alertas): {exc.response.text}")
    except Exception as e:
        log.error(f"❌ Fallo de red al registrar alerta: {e}")