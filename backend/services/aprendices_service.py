from services.dataverse import obtener_cliente, sanitizar_odata
from fastapi import HTTPException
from core.logger import log  # 🟢 Importamos el logger profesional

async def consultar_aprendices_por_ficha(numero_ficha: str) -> list:
    # 🛡️ Aplicamos el escudo OData
    numero_limpio = sanitizar_odata(numero_ficha.strip())

    log.info(f"Iniciando consulta para la ficha exacta: '{numero_limpio}'")

    client = obtener_cliente()

    url_ficha = (
        f"cr6a3_fichas?"
        f"$filter=cr6a3_numero_ficha eq '{numero_limpio}'"
        f"&$select=cr6a3_fichaid,cr6a3_numero_ficha,cr6a3_nombre_programa,cr6a3_fecha_inicio,cr6a3_fecha_fin,cr6a3_fecha_inicio_practicas,cr6a3_fecha_fin_practicas,cr6a3_jornada,_cr6a3_instructorasignado_value"
    )

    # Usamos debug para URLs o datos técnicos que solo importan al rastrear un fallo
    log.debug(f"URL generada para consulta de ficha: {url_ficha}")

    res_ficha = await client.get(url_ficha)

    if res_ficha.status_code != 200:
        log.error(f"Error de Dataverse al consultar ficha '{numero_limpio}'. Status: {res_ficha.status_code}. Detalle: {res_ficha.text}")
        raise HTTPException(
            status_code=res_ficha.status_code,
            detail="Error en consulta de la ficha en Dataverse"
        )

    datos_ficha = res_ficha.json().get("value", [])

    if not datos_ficha:
        # Un 404 esperado es un warning, no un error de caída del servidor
        log.warning(f"Dataverse devolvió vacío. La ficha '{numero_limpio}' no existe en el sistema.")
        raise HTTPException(
            status_code=404,
            detail="La ficha no existe."
        )

    ficha_id = datos_ficha[0]["cr6a3_fichaid"]
    log.debug(f"Ficha encontrada. ID interno (GUID): {ficha_id}")

    columnas = (
        "cr6a3_documento_de_identidad,"
        "cr6a3_correo_electronico,"
        "cr6a3_numero_celular,"
        "cr6a3_nombre_completo,"
        "cr6a3_faltas_totales,"
        "cr6a3_faltas_consecutivas"
    )

    url_aprendices = (
        f"cr6a3_aprendizs?"
        f"$filter=_cr6a3_fichavinculad_value eq '{ficha_id}'"
        f"&$select={columnas}"
    )

    log.info(f"Buscando aprendices vinculados a la ficha '{numero_limpio}'...")

    res_aprendices = await client.get(url_aprendices)

    if res_aprendices.status_code != 200:
        log.error(f"Error al consultar aprendices para ficha '{numero_limpio}'. Status: {res_aprendices.status_code}. Detalle: {res_aprendices.text}")
        raise HTTPException(
            status_code=res_aprendices.status_code,
            detail="Error consultando aprendices vinculados"
        )

    datos_aprendices = res_aprendices.json().get("value", [])

    log.info(f"Consulta exitosa. Total de aprendices hallados: {len(datos_aprendices)}")

    from datetime import datetime
    ahora = datetime.utcnow().date()

    def calcular_etapa(inicio_prac, fin_prac, inicio_lect, fin_lect) -> str:
        def parse_fecha(f_str):
            if not f_str: return None
            try: return datetime.fromisoformat(f_str.split('T')[0]).date()
            except: return None

        ip = parse_fecha(inicio_prac)
        fp = parse_fecha(fin_prac)
        il = parse_fecha(inicio_lect)
        fl = parse_fecha(fin_lect)

        if ip and fp:
            if ip <= ahora <= fp: return "Práctica"
            elif ahora > fp: return "Finalizada"
        if il and fl:
            if il <= ahora <= fl: return "Lectiva"
            elif ahora < il: return "Por iniciar"
        if fl and ahora > fl and (not ip or ahora < ip):
            return "Transición a Práctica"
        return "Lectiva"
        
    programa_nombre = datos_ficha[0].get("cr6a3_nombre_programa", "Sin Programa")
    f_inicio = datos_ficha[0].get("cr6a3_fecha_inicio")
    f_fin = datos_ficha[0].get("cr6a3_fecha_fin")
    fp_inicio = datos_ficha[0].get("cr6a3_fecha_inicio_practicas")
    fp_fin = datos_ficha[0].get("cr6a3_fecha_fin_practicas")

    etapa_calculada = calcular_etapa(fp_inicio, fp_fin, f_inicio, f_fin)
    instructor_nombre = datos_ficha[0].get("_cr6a3_instructorasignado_value@OData.Community.Display.V1.FormattedValue") or datos_ficha[0].get("_cr6a3_instructorasignado_value") or "No asignado"
    jornada = datos_ficha[0].get("cr6a3_jornada@OData.Community.Display.V1.FormattedValue") or "Sin Jornada"

    return [
        {
            "documento": ap.get("cr6a3_documento_de_identidad"),
            "correo": ap.get("cr6a3_correo_electronico"),
            "telefono": ap.get("cr6a3_numero_celular"),
            "nombre": ap.get("cr6a3_nombre_completo"),
            "ficha": numero_limpio,
            "programa": programa_nombre,
            "instructor": instructor_nombre,
            "jornada": jornada,
            "etapa": etapa_calculada,
            "faltas_totales": ap.get("cr6a3_faltas_totales") or 0,
            "faltas_consecutivas": ap.get("cr6a3_faltas_consecutivas") or 0
        }
        for ap in datos_aprendices
    ]

async def buscar_aprendices_global(criterio: str) -> list:
    log.info(f"Iniciando busqueda global de aprendiz con criterio: {criterio}")
    client = obtener_cliente()
    criterio_limpio = sanitizar_odata(criterio.strip())
    
    columnas = (
        "cr6a3_documento_de_identidad,"
        "cr6a3_correo_electronico,"
        "cr6a3_numero_celular,"
        "cr6a3_nombre_completo,"
        "cr6a3_faltas_totales,"
        "cr6a3_faltas_consecutivas"
    )
    
    # Buscar por documento exacto o que contenga el nombre
    filtro = f"cr6a3_documento_de_identidad eq '{criterio_limpio}' or contains(cr6a3_nombre_completo, '{criterio_limpio}')"
    url_aprendices = f"cr6a3_aprendizs?$filter={filtro}&$select={columnas}&$expand=cr6a3_FichaVinculad($select=cr6a3_numero_ficha,cr6a3_nombre_programa,cr6a3_fecha_inicio,cr6a3_fecha_fin,cr6a3_fecha_inicio_practicas,cr6a3_fecha_fin_practicas,cr6a3_jornada,_cr6a3_instructorasignado_value)"
    
    res_aprendices = await client.get(url_aprendices)
    if res_aprendices.status_code != 200:
        log.error(f"Error en busqueda global. Status: {res_aprendices.status_code}")
        raise HTTPException(status_code=res_aprendices.status_code, detail="Error buscando al aprendiz")

    datos_aprendices = res_aprendices.json().get("value", [])
    
    # Mapeo usando la logica de etapa ya establecida para todos (calculada globalmente)
    from datetime import datetime
    ahora = datetime.utcnow().date()
    def calcular_etapa_global(ap_ficha):
        if not ap_ficha: return "Desconocida"
        def parse_fecha(f_str):
            if not f_str: return None
            try: return datetime.fromisoformat(f_str.split('T')[0]).date()
            except: return None
        ip = parse_fecha(ap_ficha.get("cr6a3_fecha_inicio_practicas"))
        fp = parse_fecha(ap_ficha.get("cr6a3_fecha_fin_practicas"))
        il = parse_fecha(ap_ficha.get("cr6a3_fecha_inicio"))
        fl = parse_fecha(ap_ficha.get("cr6a3_fecha_fin"))

        if ip and fp:
            if ip <= ahora <= fp: return "Práctica"
            elif ahora > fp: return "Finalizada"
        if il and fl:
            if il <= ahora <= fl: return "Lectiva"
            elif ahora < il: return "Por iniciar"
        if fl and ahora > fl and (not ip or ahora < ip): return "Transición a Práctica"
        return "Lectiva"

    return [
        {
            "documento": ap.get("cr6a3_documento_de_identidad"),
            "correo": ap.get("cr6a3_correo_electronico"),
            "telefono": ap.get("cr6a3_numero_celular"),
            "nombre": ap.get("cr6a3_nombre_completo"),
            "ficha": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_numero_ficha", "N/A") if ap.get("cr6a3_FichaVinculad") else "N/A",
            "programa": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_nombre_programa", "Sin Programa") if ap.get("cr6a3_FichaVinculad") else "Sin Programa",
            "instructor": ap.get("cr6a3_FichaVinculad", {}).get("_cr6a3_instructorasignado_value@OData.Community.Display.V1.FormattedValue") or ap.get("cr6a3_FichaVinculad", {}).get("_cr6a3_instructorasignado_value") or "No asignado",
            "jornada": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_jornada@OData.Community.Display.V1.FormattedValue") or "Sin Jornada",
            "etapa": calcular_etapa_global(ap.get("cr6a3_FichaVinculad")),
            "faltas_totales": ap.get("cr6a3_faltas_totales") or 0,
            "faltas_consecutivas": ap.get("cr6a3_faltas_consecutivas") or 0
        }
        for ap in datos_aprendices
    ]

async def consultar_todos_aprendices() -> list:
    log.info("Iniciando consulta de todos los aprendices")
    client = obtener_cliente()
    columnas = (
        "cr6a3_documento_de_identidad,"
        "cr6a3_correo_electronico,"
        "cr6a3_nombre_completo,"
        "cr6a3_faltas_totales,"
        "cr6a3_faltas_consecutivas"
    )
    url_aprendices = f"cr6a3_aprendizs?$select={columnas}&$expand=cr6a3_FichaVinculad($select=cr6a3_numero_ficha,cr6a3_nombre_programa,cr6a3_fecha_inicio,cr6a3_fecha_fin,cr6a3_fecha_inicio_practicas,cr6a3_fecha_fin_practicas,cr6a3_jornada,_cr6a3_instructorasignado_value)"
    res_aprendices = await client.get(url_aprendices)

    if res_aprendices.status_code != 200:
        log.error(f"Error al consultar todos los aprendices. Status: {res_aprendices.status_code}. Detalle: {res_aprendices.text}")
        raise HTTPException(status_code=res_aprendices.status_code, detail="Error consultando aprendices")

    datos_aprendices = res_aprendices.json().get("value", [])
    log.info(f"Consulta exitosa. Total de aprendices hallados: {len(datos_aprendices)}")

    from datetime import datetime, timezone
    # Utilizamos datetime actual en UTC u hora local según configuración, 
    # pero como es solo fecha compararemos el string ISO o lo parseamos
    ahora = datetime.utcnow().date()

    def calcular_etapa(ficha: dict) -> str:
        if not ficha:
            return "Desconocida"
        
        # Helper interno para parsear "YYYY-MM-DD" que devuelve Dataverse
        def parse_fecha(f_str):
            if not f_str:
                return None
            try:
                # Dataverse format: 2026-09-01 or 2026-09-01T...
                return datetime.fromisoformat(f_str.split('T')[0]).date()
            except:
                return None

        # Evaluamos prácticas primero, si estamos dentro del rango de prácticas
        inicio_prac = parse_fecha(ficha.get("cr6a3_fecha_inicio_practicas"))
        fin_prac = parse_fecha(ficha.get("cr6a3_fecha_fin_practicas"))

        if inicio_prac and fin_prac:
            if inicio_prac <= ahora <= fin_prac:
                return "Práctica"
            elif ahora > fin_prac:
                return "Finalizada"
        
        # Evaluamos lectiva si no estamos en práctica
        inicio_lect = parse_fecha(ficha.get("cr6a3_fecha_inicio"))
        fin_lect = parse_fecha(ficha.get("cr6a3_fecha_fin"))

        if inicio_lect and fin_lect:
            if inicio_lect <= ahora <= fin_lect:
                return "Lectiva"
            elif ahora < inicio_lect:
                return "Por iniciar"
        
        # Fallback si por alguna razón la fecha actual no cuadra exactamente
        if fin_lect and ahora > fin_lect and (not inicio_prac or ahora < inicio_prac):
            return "Transición a Práctica"

        return "Lectiva" # Default safe value

    return [
        {
            "documento": ap.get("cr6a3_documento_de_identidad"),
            "correo": ap.get("cr6a3_correo_electronico"),
            "nombre": ap.get("cr6a3_nombre_completo"),
            "ficha": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_numero_ficha", "N/A") if ap.get("cr6a3_FichaVinculad") else "N/A",
            "programa": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_nombre_programa", "Sin Programa") if ap.get("cr6a3_FichaVinculad") else "Sin Programa",
            "instructor": ap.get("cr6a3_FichaVinculad", {}).get("_cr6a3_instructorasignado_value@OData.Community.Display.V1.FormattedValue") or ap.get("cr6a3_FichaVinculad", {}).get("_cr6a3_instructorasignado_value") or "No asignado",
            "jornada": ap.get("cr6a3_FichaVinculad", {}).get("cr6a3_jornada@OData.Community.Display.V1.FormattedValue") or "Sin Jornada",
            "etapa": calcular_etapa(ap.get("cr6a3_FichaVinculad", {})),
            "faltas_totales": ap.get("cr6a3_faltas_totales") or 0,
            "faltas_consecutivas": ap.get("cr6a3_faltas_consecutivas") or 0
        }
        for ap in datos_aprendices
    ]

async def crear_aprendiz_service(aprendiz_data) -> dict:
    # aprendiz_data is of type AprendizCreate
    numero_limpio = sanitizar_odata(aprendiz_data.cr6a3_numero_ficha.strip())
    log.info(f"Buscando ficha para vincular al nuevo aprendiz: '{numero_limpio}'")
    
    client = obtener_cliente()
    url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{numero_limpio}'&$select=cr6a3_fichaid"
    res_ficha = await client.get(url_ficha)
    
    if res_ficha.status_code != 200:
        log.error(f"Error de Dataverse al buscar ficha para vinculación. Status: {res_ficha.status_code}")
        raise HTTPException(status_code=res_ficha.status_code, detail="Error al buscar la ficha en Dataverse")
        
    datos_ficha = res_ficha.json().get("value", [])
    if not datos_ficha:
        log.warning(f"Intento de crear aprendiz con ficha inexistente: '{numero_limpio}'")
        raise HTTPException(status_code=404, detail="La ficha especificada no existe.")
        
    ficha_id = datos_ficha[0]["cr6a3_fichaid"]
    
    payload = {
        "cr6a3_nombre_completo": aprendiz_data.cr6a3_nombre_completo,
        "cr6a3_documento_de_identidad": aprendiz_data.cr6a3_documento_de_identidad,
        "cr6a3_correo_electronico": aprendiz_data.cr6a3_correo_electronico,
        "cr6a3_numero_celular": aprendiz_data.cr6a3_numero_celular,
        "cr6a3_FichaVinculad@odata.bind": f"/cr6a3_fichas({ficha_id})"
    }
    
    log.info(f"Registrando nuevo aprendiz: {aprendiz_data.cr6a3_nombre_completo}")
    res_crear = await client.post("cr6a3_aprendizs", json=payload)
    
    if res_crear.status_code != 204: # Dataverse returns 204 on successful creation usually, or 201 with return representation
        log.error(f"Error al crear aprendiz. Status: {res_crear.status_code}. Detalle: {res_crear.text}")
        raise HTTPException(status_code=res_crear.status_code, detail="Error creando el aprendiz en Dataverse")
        
    log.info(f"Aprendiz {aprendiz_data.cr6a3_nombre_completo} creado exitosamente.")
    return {"mensaje": "Aprendiz creado exitosamente"}