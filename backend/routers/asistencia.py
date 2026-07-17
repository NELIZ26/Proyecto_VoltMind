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
from services.asistencia_service import procesar_cierre_y_persistencia, obtener_asistencia_semanal_dataverse
# 🟢 Asegúrate de tener el manager importado en la parte superior de tu archivo asistencia.py
from services.websocket_manager import manager

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True, protocol=2)

router = APIRouter(prefix="/api/asistencia", tags=["Asistencia"])

@router.post("/guardar-firma")
async def guardar_firma_temporal(datos: FirmaCreate):
    
    # 1. ¿La clase sigue abierta?
    clase_activa = await redis_client.exists(f"sesion:{datos.sesion_id}:ambiente")
    if not clase_activa:
        raise HTTPException(
            status_code=400,
            detail="La clase ya ha finalizado. No se reciben más firmas."
        )

    # 2. 🔒 CANDADO DOBLE: Validar que no intente inyectar otra firma por HTTP POST directo
    clave_firmados = f"sesion:{datos.sesion_id}:firmados"
    ya_firmado = await redis_client.sismember(clave_firmados, str(datos.documento_aprendiz))
    if ya_firmado:
        raise HTTPException(
            status_code=403,
            detail="Ya existe una firma registrada para este documento."
        )

    clave_redis = f"firmas_sesion:{datos.sesion_id}"
    firma_data = {
        "nombre": datos.nombre_aprendiz,
        "documento": datos.documento_aprendiz,
        "firma_b64": datos.firma_base64
    }
    
    # Almacenar en la lista estructural para el PDF final
    await redis_client.rpush(clave_redis, json.dumps(firma_data))
    await redis_client.expire(clave_redis, 43200) 

    # 🟢 MARCAR COMO FIRMADO: Añadir al set de control para bloquear futuros intentos
    await redis_client.sadd(clave_firmados, str(datos.documento_aprendiz))
    await redis_client.expire(clave_firmados, 43200)

    # Notificar al Dashboard por WebSocket
    try:
        ambiente_id = await redis_client.get(f"sesion:{datos.sesion_id}:ambiente")
        if ambiente_id:
            await manager.broadcast_to_ambiente(ambiente_id, {
                "tipo": "APRENDIZ_FIRMA",
                "documento": str(datos.documento_aprendiz)
            })
            log.info(f"📢 [WebSocket] Firma transmitida al Dashboard para aprendiz: {datos.documento_aprendiz}")
    except Exception as e:
        log.error(f"❌ Error al propagar evento APRENDIZ_FIRMA por WebSocket: {e}")

    return {"mensaje": "Firma almacenada con éxito y bloqueada contra re-firmas."}

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
        
        # 3. Limpieza de la caché de firmas
        await redis_client.delete(clave_redis)
        
        # 📢 4. WEBSOCKET Y LIMPIEZA MAESTRA: Avisar a la Tablet para que se bloquee
        ambiente_id = await redis_client.get(f"sesion:{datos.sesion_id}:ambiente")
        if ambiente_id:
            await manager.broadcast_to_ambiente(ambiente_id, {
                "tipo": "SESION_FINALIZADA"
            })
            log.info(f"📢 [WebSocket] Orden de apagado enviada a la Tablet del ambiente {ambiente_id}")
            
            # Limpiamos los rastros estructurales de la sesión para evitar bloqueos futuros
            await redis_client.delete(f"sesion:{datos.sesion_id}:ambiente")
            await redis_client.delete(f"sesion:{datos.sesion_id}:salida_activa")
            await redis_client.delete(f"sesion:{datos.sesion_id}:ingresos")

    except Exception as e:
        log.error(f"Error crítico en la persistencia de asistencia al cerrar aula: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="No se pudo procesar el cierre de asistencia en la base de datos."
        )

    return {"mensaje": "Asistencias guardadas exitosamente, caché liberada y Kiosco reiniciado."}


@router.post("/generar-pin")
async def generar_pin(datos: PinCreate):
    # 1. Generamos el PIN numérico único de 4 dígitos
    import random
    while True:
        nuevo_pin = str(random.randint(1000, 9999))
        if not await redis_client.exists(f"pin:{nuevo_pin}"):
            break

    # 2. Armamos el payload dependiendo del rol
    if datos.rol == "instructor":
        if not datos.identificador:
            raise HTTPException(status_code=400, detail="Falta el identificador del instructor.")
        
        payload_redis = json.dumps({"rol": "instructor", "id": datos.identificador})
        log.info(f"PIN maestro generado para instructor: {datos.identificador}")
        
    else:
        if not datos.documento_aprendiz:
            raise HTTPException(status_code=400, detail="Falta el documento del aprendiz.")
        
        # Limpieza de seguridad
        doc_seguro = "".join(filter(str.isalnum, datos.documento_aprendiz))
        
        # 🟢 ATRAPAMOS EL NOMBRE DESDE EL MODELO Y LO METEMOS AL JSON
        nombre_seguro = datos.nombre if hasattr(datos, 'nombre') and datos.nombre else "Aprendiz"
        
        payload_redis = json.dumps({
            "rol": "aprendiz", 
            "id": doc_seguro,
            "nombre": nombre_seguro # 🟢 ¡LA PIEZA CLAVE PARA EL LIENZO!
        })
        log.info(f"PIN de asistencia generado para aprendiz doc: {doc_seguro}")

    # 3. Guardamos en Redis (65 segundos)
    await redis_client.setex(name=f"pin:{nuevo_pin}", time=65, value=payload_redis)
    return {"pin": nuevo_pin}


@router.post("/validar-pin")
async def validar_pin(datos: PinValidate):
    clave_pin = f"pin:{datos.pin}"
    datos_redis_str = await redis_client.get(clave_pin)

    if not datos_redis_str:
        log.warning(f"Intento fallido o expirado de PIN: {datos.pin}")
        raise HTTPException(status_code=400, detail="PIN incorrecto o ha expirado.")
    
    rol = "aprendiz"
    usuario_id = datos_redis_str
    nombre_usuario = "Aprendiz"

    try:
        datos_pin = json.loads(datos_redis_str)
        if isinstance(datos_pin, dict):
            rol = datos_pin.get("rol", "aprendiz")
            usuario_id = datos_pin.get("id")
            nombre_usuario = datos_pin.get("nombre", "Aprendiz")
        else:
            usuario_id = str(datos_pin)
    except Exception as e:
        log.debug(f"PIN parseado como texto plano o formato heredado: {e}")

    # ==========================================
    # RUTA 1: ES UN INSTRUCTOR (LLAVE MAESTRA)
    # ==========================================
    if rol == "instructor":
        await redis_client.delete(clave_pin)
        log.info(f"Instructor {usuario_id} validó PIN maestro.")
        return {
            "accion": "activar_aula",
            "mensaje": "Clave maestra aceptada. Iniciando ambiente...",
            "rol": "instructor",
            "identificador": usuario_id,
            "datos_clase": { "instructor": usuario_id }
        }

    # ==========================================
    # RUTA 2: ES UN APRENDIZ (ASISTENCIA)
    # ==========================================
    doc_aprendiz = str(usuario_id)

    # 🔒 CANDADO 1: ¿La clase sigue abierta?
    clase_activa = await redis_client.exists(f"sesion:{datos.sesion_id}:ambiente")
    if not clase_activa:
        raise HTTPException(
            status_code=400,
            detail="La sesión de clase ya ha finalizado. No se permiten más registros."
        )

    clave_ingresos = f"sesion:{datos.sesion_id}:ingresos"
    clave_salida = f"sesion:{datos.sesion_id}:salida_activa"
    clave_firmados = f"sesion:{datos.sesion_id}:firmados"  # 🆕 Estructura para control de firmas
    
    ya_ingreso = await redis_client.sismember(clave_ingresos, doc_aprendiz)
    salidas_habilitadas = await redis_client.exists(clave_salida)
    ya_firmado = await redis_client.sismember(clave_firmados, doc_aprendiz)

    # 🔒 CANDADO DE SEGURIDAD NUEVO: Evitar doble firma
    if ya_firmado:
        await redis_client.delete(clave_pin)
        raise HTTPException(
            status_code=403,
            detail="Ya has registrado tu firma de salida para esta clase. No puedes volver a firmar."
        )

    # 🔴 MODO SALIDAS (Firmas habilitadas)
    if salidas_habilitadas:
        if not ya_ingreso:
            raise HTTPException(
                status_code=403, 
                detail="Acceso denegado. No puedes firmar la salida si no registraste tu ingreso al iniciar la clase."
            )
            
        await redis_client.delete(clave_pin)
        log.info(f"Firma solicitada para aprendiz {doc_aprendiz} en sesión {datos.sesion_id}")
        
        return {
            "accion": "requiere_firma", 
            "mensaje": "Clase finalizada. Por favor registra tu firma.",
            "documento_aprendiz": doc_aprendiz,
            "nombre_aprendiz": nombre_usuario,
            "rol": "aprendiz"
        }

    # 🟢 MODO INGRESOS (Clase en curso o iniciando)
    else:
        if not ya_ingreso:
            # Registro inicial exitoso
            await redis_client.sadd(clave_ingresos, doc_aprendiz)
            await redis_client.expire(clave_ingresos, 43200)
            await redis_client.delete(clave_pin)
            
            log.info(f"Ingreso registrado para aprendiz {doc_aprendiz} en sesión {datos.sesion_id}")
            
            ambiente_id = await redis_client.get(f"sesion:{datos.sesion_id}:ambiente")
            if ambiente_id:
                await manager.broadcast_to_ambiente(ambiente_id, {
                    "tipo": "APRENDIZ_INGRESO",
                    "documento": doc_aprendiz,
                    "nombre": nombre_usuario
                })

            return {
                "accion": "ingreso_exitoso", 
                "mensaje": "Ingreso a clase registrado. ¡Bienvenido!",
                "documento_aprendiz": doc_aprendiz,
                "nombre_aprendiz": nombre_usuario,
                "rol": "aprendiz"
            }
        else:
            # 🔒 CORRECCIÓN CLAVE: Si ya ingresó y no es hora de salida, lo frena aquí
            await redis_client.delete(clave_pin)
            raise HTTPException(
                status_code=403,
                detail="Aún se encuentran en clases. Espera a que el instructor habilite la firma de salida."
            )

@router.post("/habilitar-salida/{sesion_id}")
async def habilitar_salida(sesion_id: str):
    await redis_client.setex(f"sesion:{sesion_id}:salida_activa", 43200, "1")
    
    # 📢 WEBSOCKET: Avisar a la Tablet (y Dashboard) que el modo salida empezó
    try:
        ambiente_id = await redis_client.get(f"sesion:{sesion_id}:ambiente")
        if ambiente_id:
            from services.websocket_manager import manager
            await manager.broadcast_to_ambiente(ambiente_id, {
                "tipo": "CAMBIO_ESTADO",
                "nuevo_estado": "MODO_SALIDA"
            })
            log.info(f"📢 [WebSocket] Estado MODO_SALIDA propagado al ambiente {ambiente_id}")
    except Exception as e:
        log.error(f"❌ Error al propagar MODO_SALIDA por WebSocket: {e}")

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



@router.get("/sesion/{sesion_id}/ingresos")
async def obtener_ingresos_activos(sesion_id: str):
    """
    Recupera los documentos de los aprendices que ya registraron su ingreso
    en la sesión actual desde la memoria caché (Redis) si el Dashboard se recarga.
    """
    clave = f"sesion:{sesion_id}:ingresos"
    
    try:
        # smembers devuelve todos los elementos del Set de Redis
        ingresos = await redis_client.smembers(clave)
        return {"ingresos": list(ingresos)}
    except Exception as e:
        log.error(f"Error recuperando ingresos activos para sesión {sesion_id}: {e}")
        return {"ingresos": []}