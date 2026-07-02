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
        f"&$select=cr6a3_fichaid,cr6a3_numero_ficha"
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
        "cr6a3_nombre_completo"
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

    return [
        {
            "documento": ap.get("cr6a3_documento_de_identidad"),
            "correo": ap.get("cr6a3_correo_electronico"),
            "nombre": ap.get("cr6a3_nombre_completo")
        }
        for ap in datos_aprendices
    ]