from services.dataverse import cliente_dataverse
from fastapi import HTTPException
import json # Importamos json para formatear la respuesta

async def consultar_aprendices_por_ficha(numero_ficha: str) -> list:
    numero_limpio = numero_ficha.strip()
    
    print("\n================ DEBUG DATAVERSE ================")
    print(f"1. Buscando ficha exacta: '{numero_limpio}'")

    async with await cliente_dataverse() as client:
        # --- PASO 1 ---
        url_ficha = f"cr6a3_fichas?$filter=cr6a3_numero_ficha eq '{numero_limpio}'"
        print(f"2. URL generada: {url_ficha}")

        res_ficha = await client.get(url_ficha)
        print(f"3. Código de Estado Dataverse (Ficha): {res_ficha.status_code}")

        if res_ficha.status_code != 200:
            print(f"   ❌ ERROR DE DATAVERSE: {res_ficha.text}")
            raise HTTPException(status_code=res_ficha.status_code, detail="Error en consulta")

        datos_ficha = res_ficha.json().get("value", [])
        print(f"4. Fichas encontradas: {len(datos_ficha)}")

        if len(datos_ficha) == 0:
            print("   💥 DATAVERSE DEVOLVIÓ VACÍO. (El número no coincide o la columna se llama distinto)")
            print("=================================================\n")
            raise HTTPException(status_code=404, detail="La ficha no existe.")

        ficha_id = datos_ficha[0].get("cr6a3_fichaid")
        print(f"5. ID interno de la ficha (GUID): {ficha_id}")

        # --- PASO 2 ---
        columnas = "cr6a3_documento_de_identidad,cr6a3_correo_electronico,cr6a3_nombre_completo"
        url_aprendices = f"cr6a3_aprendizs?$filter=_cr6a3_fichavinculad_value eq '{ficha_id}'&$select={columnas}"
        print(f"6. Buscando aprendices vinculados...")

        res_aprendices = await client.get(url_aprendices)
        print(f"7. Código de Estado Dataverse (Aprendices): {res_aprendices.status_code}")
        
        datos_aprendices = res_aprendices.json().get("value", [])
        print(f"8. Total de aprendices hallados: {len(datos_aprendices)}")
        print("=================================================\n")

        return [
            {
                "documento": ap.get("cr6a3_documento_de_identidad"),
                "correo": ap.get("cr6a3_correo_electronico"),
                "nombre": ap.get("cr6a3_nombre_completo")
            }
            for ap in datos_aprendices
        ]