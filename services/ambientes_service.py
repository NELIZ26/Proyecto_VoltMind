from services.dataverse import (
    consultar_dataverse, 
    crear_registro_dataverse, 
    actualizar_registro_dataverse, 
    eliminar_registro_dataverse
)
from schemas.ambientes import AmbienteCreate, AmbienteUpdate

from datetime import datetime

TABLA_AMBIENTES = "cr6a3_ambiente_formacions"

async def get_all_ambientes():
    query = f"{TABLA_AMBIENTES}?$expand=cr6a3_sede($select=cr6a3_sedeid,cr6a3_nombre,cr6a3_municipio)&$orderby=cr6a3_nombre_ambiente asc"
    data = await consultar_dataverse(query)
    
    # Obtener asignaciones activas
    today_str = datetime.now().strftime('%Y-%m-%d')
    query_asig = f"cr6a3_asignacioneses?$filter=cr6a3_fecha_inicio le '{today_str}' and cr6a3_fecha_fin ge '{today_str}'&$expand=cr6a3_FichaId($select=cr6a3_jornada)"
    data_asig = await consultar_dataverse(query_asig)
    
    map_jornada_inv = {430120000: "manana", 430120001: "tarde", 430120002: "noche"}
    
    # Crear un diccionario de ambiente_id -> {manana: fecha_fin, tarde: fecha_fin, noche: fecha_fin}
    ambientes_ocupados = {}
    for asig in data_asig.get("value", []):
        amb_id = asig.get("_cr6a3_ambienteid_value")
        fecha_fin = asig.get("cr6a3_fecha_fin")
        ficha = asig.get("cr6a3_FichaId") or {}
        jornada_code = ficha.get("cr6a3_jornada")
        jornada_str = map_jornada_inv.get(jornada_code)
        
        if amb_id and jornada_str:
            if amb_id not in ambientes_ocupados:
                ambientes_ocupados[amb_id] = {"manana": None, "tarde": None, "noche": None}
            
            actual_fin = ambientes_ocupados[amb_id][jornada_str]
            if not actual_fin or fecha_fin > actual_fin:
                ambientes_ocupados[amb_id][jornada_str] = fecha_fin
    
    resultados = []
    for am in data.get("value", []):
        sede_obj = am.get("cr6a3_sede") or {}
        amb_id = am.get("cr6a3_ambiente_formacionid")
        
        ocupacion = ambientes_ocupados.get(amb_id, {"manana": None, "tarde": None, "noche": None})
        
        resultados.append({
            "cr6a3_ambiente_formacionid": amb_id,
            "cr6a3_nombre_ambiente": am.get("cr6a3_nombre_ambiente"),
            "cr6a3_cantidad_nodos_electricos": am.get("cr6a3_cantidad_nodos_electricos"),
            "cr6a3_capacidad_aprendices": am.get("cr6a3_capacidad_aprendices"),
            "cr6a3_direccion_ip_maestra": am.get("cr6a3_direccion_ip_maestra"),
            "cr6a3_Estado_Ambiente": am.get("cr6a3_estado_ambiente"),
            "sede_nombre": sede_obj.get("cr6a3_nombre"),
            "sede_municipio": sede_obj.get("cr6a3_municipio"),
            "sede_id": sede_obj.get("cr6a3_sedeid") or am.get("_cr6a3_sede_value"),
            "ocupacion": ocupacion
        })
    return resultados

async def create_ambiente(ambiente: AmbienteCreate):
    payload = ambiente.dict(exclude_unset=True, exclude={"sede_id"})
    if "cr6a3_Estado_Ambiente" in payload:
        payload["cr6a3_estado_ambiente"] = payload.pop("cr6a3_Estado_Ambiente")
    
    if ambiente.sede_id:
        # Binding en OData para relaciones lookup
        payload["cr6a3_sede@odata.bind"] = f"/cr6a3_sedes({ambiente.sede_id})"
        
    resultado = await crear_registro_dataverse(TABLA_AMBIENTES, payload)
    return resultado

async def update_ambiente(ambiente_id: str, ambiente: AmbienteUpdate):
    payload = ambiente.dict(exclude_unset=True, exclude={"sede_id"})
    if "cr6a3_Estado_Ambiente" in payload:
        payload["cr6a3_estado_ambiente"] = payload.pop("cr6a3_Estado_Ambiente")
    
    if ambiente.sede_id is not None:
        if ambiente.sede_id:
            payload["cr6a3_sede@odata.bind"] = f"/cr6a3_sedes({ambiente.sede_id})"
        else:
            # Para desvincular (si la BD lo permite)
            pass
            
    resultado = await actualizar_registro_dataverse(TABLA_AMBIENTES, ambiente_id, payload)
    return resultado

async def delete_ambiente(ambiente_id: str):
    await eliminar_registro_dataverse(TABLA_AMBIENTES, ambiente_id)
    return {"message": "Ambiente eliminado con Ǹxito"}

async def get_all_sedes():
    query = "cr6a3_sedes?$select=cr6a3_sedeid,cr6a3_nombre,cr6a3_municipio&$orderby=cr6a3_nombre asc"
    data = await consultar_dataverse(query)
    return data.get("value", [])

from schemas.ambientes import SedeCreate

async def create_sede(sede: SedeCreate):
    payload = sede.dict(exclude_unset=True)
    resultado = await crear_registro_dataverse("cr6a3_sedes", payload)
    return resultado
