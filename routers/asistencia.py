# routers/asistencia.py
import os
import uuid
import random
import json
import redis.asyncio as redis 
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from datetime import datetime, timedelta
from core.logger import log
from schemas.asistencia import FirmaCreate, CierreSesion, PinCreate, PinValidate, QrGenerate, QrValidate
from services.asistencia_service import procesar_cierre_y_persistencia, obtener_asistencia_semanal_dataverse,obtener_historial_aprendiz

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True, protocol=2)

router = APIRouter(prefix="/api/asistencia", tags=["Asistencia"])

@router.post("/guardar-firma")
async def guardar_firma_temporal(datos: FirmaCreate):
    clave_redis = f"firmas_sesion:{datos.sesion_id}"
    firma_data = {
        "nombre": datos.nombre_aprendiz,
        "documento": datos.documento_aprendiz,
        "firma_b64": datos.firma_base64
    }
    await redis_client.rpush(clave_redis, json.dumps(firma_data))
    await redis_client.expire(clave_redis, 43200) 
    return {"mensaje": "Firma almacenada en bóveda temporal (Redis)."}

@router.post("/cerrar-asistencia")
async def cerrar_asistencia_diaria(datos: CierreSesion):
    """
    Se ejecuta inmediatamente al apagar el aula desde la interfaz. 
    ÚNICAMENTE guarda las firmas y estados en Dataverse y limpia Redis. NO genera PDFs.
    """
    clave_redis = f"firmas_sesion:{datos.sesion_id}"
    
    # 1. Traer los escaneos temporales almacenados en memoria
    firmas_crudas = await redis_client.lrange(clave_redis, 0, -1)
    lista_firmas_hoy = [json.loads(firma) for firma in firmas_crudas]
    lista_firmas_segura = list(lista_firmas_hoy)

    try:
        # 2. Persistencia total en las tablas de Dataverse y almacenamiento de imágenes
        await procesar_cierre_y_persistencia(datos.sesion_id, datos.numero_ficha, lista_firmas_segura)
        
        # 3. Limpieza absoluta de la caché de la sesión actual
        await redis_client.delete(clave_redis)
    except Exception as e:
        log.error(f"Error crítico en la persistencia de asistencia al cerrar aula: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="No se pudo procesar el cierre de asistencia en la base de datos."
        )

    return {"mensaje": "Asistencias guardadas exitosamente en Dataverse y caché temporal liberada."}

@router.post("/generar-pin")
async def generar_pin(datos: PinCreate):
    # Validar que el documento de identidad contenga solo caracteres seguros
    doc_seguro = "".join(filter(str.isalnum, datos.documento_aprendiz))
    while True:
        nuevo_pin = str(random.randint(1000, 9999))
        if not await redis_client.exists(f"pin:{nuevo_pin}"):
            break

    await redis_client.setex(name=f"pin:{nuevo_pin}", time=65, value=doc_seguro)
    return {"pin": nuevo_pin}

@router.post("/validar-pin")
async def validar_pin(datos: PinValidate):
    clave_pin = f"pin:{datos.pin}"
    doc_aprendiz = await redis_client.get(clave_pin)

    if not doc_aprendiz:
        log.warning(f"Intento fallido o expirado de PIN: {datos.pin}")
        raise HTTPException(status_code=400, detail="PIN incorrecto o ha expirado.")
    
    clave_ingresos = f"sesion:{datos.sesion_id}:ingresos"
    ya_ingreso = await redis_client.sismember(clave_ingresos, doc_aprendiz)

    if not ya_ingreso:
        await redis_client.sadd(clave_ingresos, doc_aprendiz)
        await redis_client.expire(clave_ingresos, 43200)
        await redis_client.delete(clave_pin)
        
        log.info(f"Ingreso registrado para aprendiz {doc_aprendiz} en sesión {datos.sesion_id}")
        return {
            "accion": "ingreso_exitoso", 
            "mensaje": "Ingreso a clase registrado. ¡Bienvenido!",
            "documento_aprendiz": doc_aprendiz
        }
    else:
        clave_salida = f"sesion:{datos.sesion_id}:salida_activa"
        if not await redis_client.exists(clave_salida):
            log.warning(f"Aprendiz {doc_aprendiz} intentó salir antes de tiempo.")
            raise HTTPException(
                status_code=403, 
                detail="Aún se encuentran en clases. Espera a que el instructor habilite la firma."
            )
        
        await redis_client.delete(clave_pin)
        return {
            "accion": "requiere_firma", 
            "mensaje": "Clase finalizada. Por favor registra tu firma.",
            "documento_aprendiz": doc_aprendiz
        }

@router.post("/habilitar-salida/{sesion_id}")
async def habilitar_salida(sesion_id: str):
    await redis_client.setex(f"sesion:{sesion_id}:salida_activa", 43200, "1")
    log.info(f"Salida y firmas habilitadas para la sesión {sesion_id}")
    return {"mensaje": "Salida habilitada. Los aprendices ya pueden firmar."}

@router.post("/generar-qr")
async def generar_token_qr(datos: QrGenerate):
    nuevo_token = f"VM-{uuid.uuid4().hex[:8].upper()}"
    await redis_client.setex(name=f"qr:{nuevo_token}", time=7, value=datos.sesion_id)
    return {"token": nuevo_token}

@router.post("/validar-qr")
async def validar_qr(datos: QrValidate):
    clave_redis = f"qr:{datos.token_qr}"
    sesion_id = await redis_client.get(clave_redis)
    
    if not sesion_id:
        raise HTTPException(status_code=400, detail="El código QR ya expiró. Escanea el nuevo.")
    
    clave_ingresos = f"sesion:{sesion_id}:ingresos"
    clave_salida = f"sesion:{sesion_id}:salida_activa"
    
    ya_ingreso = await redis_client.sismember(clave_ingresos, datos.documento_aprendiz)
    salida_habilitada = await redis_client.exists(clave_salida)

    if not ya_ingreso:
        if salida_habilitada:
            raise HTTPException(status_code=403, detail="La clase ya finalizó. No puedes registrar asistencia.")

        await redis_client.sadd(clave_ingresos, datos.documento_aprendiz)
        await redis_client.expire(clave_ingresos, 43200)
        await redis_client.delete(clave_redis)
        
        payload_ingreso = {"documento": datos.documento_aprendiz, "accion": "ingreso_exitoso"}
        await redis_client.setex(f"ultimo_scan:{sesion_id}", 5, json.dumps(payload_ingreso))
        return {"accion": "ingreso_exitoso", "documento_aprendiz": datos.documento_aprendiz}
    else:
        if not salida_habilitada:
            raise HTTPException(status_code=403, detail="Aún se encuentran en clases.")
        
        await redis_client.delete(clave_redis)
        payload_salida = {"documento": datos.documento_aprendiz, "accion": "requiere_firma"}
        await redis_client.setex(f"ultimo_scan:{sesion_id}", 5, json.dumps(payload_salida))
        return {"accion": "requiere_firma", "documento_aprendiz": datos.documento_aprendiz}

@router.get("/ultimo-escaneo/{sesion_id}")
async def ultimo_escaneo(sesion_id: str):
    data = await redis_client.get(f"ultimo_scan:{sesion_id}")
    if data:
        await redis_client.delete(f"ultimo_scan:{sesion_id}")
        return json.loads(data)
    return {"documento": None}

@router.post("/matriz-semanal")
async def generar_matriz_semanal(
    numero_ficha: str, 
    nombre_programa: str, 
    nombre_instructor: str,
    correo_destino: str,
    background_tasks: BackgroundTasks,
    sesion_activa: str = None,
    nombre_ambiente: str = "Por definir",
    horario: str = "Por definir"
):
    """
    Gatillo manual. Genera la sábana horizontal y la despacha por correo.
    Si hay una sesión activa, inyecta las firmas en vivo desde Redis.
    """
    from services.reportes_service import compilar_y_enviar_matriz_semanal
    
    firmas_en_vivo = []
    
    # 🟢 Si el aula está encendida, rescatamos las firmas de la RAM
    if sesion_activa:
        clave_redis = f"firmas_sesion:{sesion_activa}"
        firmas_crudas = await redis_client.lrange(clave_redis, 0, -1)
        firmas_en_vivo = [json.loads(f) for f in firmas_crudas]

    background_tasks.add_task(
        compilar_y_enviar_matriz_semanal,
        numero_ficha, 
        nombre_programa, 
        nombre_instructor,
        correo_destino,
        nombre_ambiente, 
        horario,
        firmas_en_vivo
    )
    
    return {"mensaje": "El reporte semanal se está ensamblando y llegará a tu correo en breve."}


    #NUEVO ENDPOINT#
@router.get("/historial/{documento}")
async def historial_aprendiz(documento: str):    #Devuelve el historial de asistencia y faltas de un aprendiz#
    return await obtener_historial_aprendiz(documento)