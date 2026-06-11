
import os
import uuid
import random
import json
import redis.asyncio as redis 
from services.asistencia_service import procesar_cierre_y_persistencia, obtener_asistencia_semanal_dataverse
from core.logger import log
from schemas.asistencia import FirmaCreate, CierreSesion, PinCreate, PinValidate, QrGenerate, QrValidate
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
from services.dataverse import consultar_dataverse
from services.reportes_service import ensamblar_y_enviar_pdf

load_dotenv()

# ==========================================
# 🧠 CONEXIÓN A REDIS
# ==========================================
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True, protocol=2)


router = APIRouter(prefix="/api/asistencia", tags=["Asistencia"])

@router.post("/guardar-firma")
async def guardar_firma_temporal(datos: FirmaCreate):
    # Usamos el sesion_id como llave para agrupar las firmas en Redis
    clave_redis = f"firmas_sesion:{datos.sesion_id}"
    
    firma_data = {
        "nombre": datos.nombre_aprendiz,
        "documento": datos.documento_aprendiz,
        "firma_b64": datos.firma_base64
    }
    
    # 🚀 rpush: Añade el elemento a una lista en Redis
    await redis_client.rpush(clave_redis, json.dumps(firma_data))
    
    # Opcional pero recomendado: Darle un tiempo de vida (TTL) de 12 horas a la lista 
    # por si el instructor olvida apagar el aula y la sesión queda huérfana
    await redis_client.expire(clave_redis, 43200) 
    
    return {"mensaje": "Firma almacenada en bóveda temporal (Redis)."}


@router.post("/generar-reporte")
async def generar_reporte_asistencia(datos: CierreSesion, background_tasks: BackgroundTasks):
    clave_redis = f"firmas_sesion:{datos.sesion_id}"
    
    # 1. TRAER LOS ESCANEOS TEMPORALES DE HOY (Desde Redis)
    firmas_crudas = await redis_client.lrange(clave_redis, 0, -1)
    lista_firmas_hoy = [json.loads(firma) for firma in firmas_crudas]
    
    try:
        # 2. PERSISTENCIA TOTAL (Lógica de Deserción y Base de Datos)
        # Procesamos a TODOS los alumnos de la ficha (asistieron o no),
        # guardamos sus firmas como .png en el servidor y creamos las filas en Dataverse.
        await procesar_cierre_y_persistencia(datos.sesion_id, datos.numero_ficha, lista_firmas_hoy)
        
        # 3. LIMPIEZA DEL CACHÉ TEMPORAL
        # Ya que los datos están seguros en Dataverse y las imágenes en el disco, borramos Redis
        await redis_client.delete(clave_redis)
        
    except Exception as e:
        log.error(f"Error crítico en la persistencia de asistencia: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="No se pudo procesar el cierre de asistencia en la base de datos."
        )

    # 4. RECOPILES DE LA SEMANA ACTUAL (Matemáticas de Calendario)
    # Calculamos el rango de fechas de Lunes a Viernes de esta semana
    hoy = datetime.now()
    lunes_esta_semana = (hoy - timedelta(days=hoy.weekday())).replace(hour=0, minute=0, second=0)
    viernes_esta_semana = lunes_esta_semana + timedelta(days=4, hours=23, minutes=59)

    # 5. CONSULTA ACUMULATIVA A DATAVERSE
    # Traemos el historial de asistencia de TODA la semana para esta ficha operativa
    asistencia_semanal = await obtener_asistencia_semanal_dataverse(
        datos.numero_ficha, 
        lunes_esta_semana, 
        viernes_esta_semana
    )

    # 6. DISPARAR ENVIÓ DEL PDF EN SEGUNDO PLANO
    # Le pasamos los datos del calendario y la asistencia acumulada al generador
    # Lanzar la generación de PDF y correo en segundo plano
    background_tasks.add_task(
            ensamblar_y_enviar_pdf,
            datos.sesion_id,              # 1
            datos.numero_ficha,           # 2
            datos.nombre_programa,        # 3
            datos.nombre_instructor,      # 4
            datos.correo_destino,         # 5 (¡Aquí debe caer el correo!)
            datos.competencia,            # 6
            datos.resultado_aprendizaje,  # 7
            lista_firmas_hoy              # 8
        )
    
    return {"mensaje": "Sesión clausurada. El reporte semanal acumulado está siendo procesado."}

@router.post("/generar-pin")
async def generar_pin(datos: PinCreate):
    # Generar nuevo PIN asegurándonos de que no exista ya en Redis
    while True:
        nuevo_pin = str(random.randint(1000, 9999))
        existe = await redis_client.exists(f"pin:{nuevo_pin}")
        if not existe:
            break

    # 🚀 setex (Set with Expiration): Guarda la variable y le dice a Redis 
    # que la DESTRUYA automáticamente en exactamente 65 segundos.
    await redis_client.setex(
        name=f"pin:{nuevo_pin}",
        time=65,
        value=datos.documento_aprendiz
    )
    
    return {"pin": nuevo_pin}

@router.post("/validar-pin")
async def validar_pin(datos: PinValidate):
    clave_pin = f"pin:{datos.pin}"
    
    # 1. Buscamos el pin en Redis
    doc_aprendiz = await redis_client.get(clave_pin)

    if not doc_aprendiz:
        log.warning(f"Intento fallido de PIN: {datos.pin}")
        raise HTTPException(status_code=400, detail="PIN incorrecto o ha expirado.")
    
    # 2. Consultamos el estado del aprendiz en esta sesión específica
    # Usamos un "Set" de Redis para guardar quiénes ya entraron
    clave_ingresos = f"sesion:{datos.sesion_id}:ingresos"
    ya_ingreso = await redis_client.sismember(clave_ingresos, doc_aprendiz)

    if not ya_ingreso:
        # 🟢 PRIMERA VEZ: Solo marcamos la entrada
        await redis_client.sadd(clave_ingresos, doc_aprendiz)
        await redis_client.expire(clave_ingresos, 43200) # Limpiamos la lista en 12h
        await redis_client.delete(clave_pin) # Quemamos el PIN usado
        
        log.info(f"Ingreso registrado para aprendiz {doc_aprendiz} en sesión {datos.sesion_id}")
        return {
            "accion": "ingreso_exitoso", 
            "mensaje": "Ingreso a clase registrado. ¡Bienvenido!",
            "documento_aprendiz": doc_aprendiz
        }
    else:
        # 🔴 SEGUNDA VEZ: Intenta salir, verificamos el interruptor del instructor
        clave_salida = f"sesion:{datos.sesion_id}:salida_activa"
        salida_habilitada = await redis_client.exists(clave_salida)

        if not salida_habilitada:
            # El profe aún no ha tocado el botón
            log.warning(f"Aprendiz {doc_aprendiz} intentó salir antes de tiempo en sesión {datos.sesion_id}")
            raise HTTPException(
                status_code=403, 
                detail="Aún se encuentran en clases. Espera a que el instructor habilite la firma."
            )
        
        # Si la salida está habilitada, procedemos con la firma
        await redis_client.delete(clave_pin) # Quemamos el PIN
        log.info(f"Salida autorizada para aprendiz {doc_aprendiz} en sesión {datos.sesion_id}")
        
        return {
            "accion": "requiere_firma", 
            "mensaje": "Clase finalizada. Por favor registra tu firma.",
            "documento_aprendiz": doc_aprendiz
        }

@router.post("/habilitar-salida/{sesion_id}")
async def habilitar_salida(sesion_id: str):
    """
    Endpoint para el instructor. Activa la bandera que permite a los 
    aprendices registrar su firma de salida.
    """
    # Creamos una bandera en Redis que durará 12 horas
    llave_salida = f"sesion:{sesion_id}:salida_activa"
    await redis_client.setex(llave_salida, 43200, "1")
    
    log.info(f"Salida y firmas habilitadas para la sesión {sesion_id}")
    return {"mensaje": "Salida habilitada. Los aprendices ya pueden firmar."}



@router.post("/generar-qr")
async def generar_token_qr(datos: QrGenerate):
    """
    Genera un token único (UUID) para el proyector y lo guarda en Redis.
    Este token vivirá solo 7 segundos en memoria por seguridad antifraude.
    """
    # Generamos un código alfanumérico seguro (ej. VM-a1b2c3d4...)
    nuevo_token = f"VM-{uuid.uuid4().hex[:8].upper()}"
    clave_redis = f"qr:{nuevo_token}"
    
    # Lo guardamos en Redis apuntando al ID de la sesión actual
    await redis_client.setex(
        name=clave_redis,
        time=7,  # Le damos 7 segundos de vida (5 del proyector + 2 de gracia por latencia de red)
        value=datos.sesion_id
    )
    
    return {"token": nuevo_token}

@router.post("/validar-qr")
async def validar_qr(datos: QrValidate):
    clave_redis = f"qr:{datos.token_qr}"
    
    # 1. Buscamos si el token existe y sigue vivo en Redis
    sesion_id = await redis_client.get(clave_redis)
    
    if not sesion_id:
        log.warning(f"Intento de QR fallido o expirado: {datos.token_qr}")
        raise HTTPException(status_code=400, detail="El código QR ya expiró. Escanea el nuevo.")
    
    # 2. EVALUACIÓN DE ESTADO GLOBAL
    clave_ingresos = f"sesion:{sesion_id}:ingresos"
    clave_salida = f"sesion:{sesion_id}:salida_activa" # 🟢 Traemos esto al principio
    
    ya_ingreso = await redis_client.sismember(clave_ingresos, datos.documento_aprendiz)
    salida_habilitada = await redis_client.exists(clave_salida)

    if not ya_ingreso:
        # 🔴 EL NUEVO CANDADO: Si intenta entrar, pero la clase YA terminó, lo bloqueamos
        if salida_habilitada:
            raise HTTPException(
                status_code=403, 
                detail="La clase ya finalizó. No puedes registrar asistencia porque no marcaste tu ingreso inicial."
            )

        # 🟢 PRIMERA VEZ: Entrada normal (Solo si la clase sigue en curso)
        await redis_client.sadd(clave_ingresos, datos.documento_aprendiz)
        await redis_client.expire(clave_ingresos, 43200) 
        
        # Quemamos el QR y notificamos ingreso
        await redis_client.delete(clave_redis)
        payload_ingreso = {"documento": datos.documento_aprendiz, "accion": "ingreso_exitoso"}
        await redis_client.setex(f"ultimo_scan:{sesion_id}", 5, json.dumps(payload_ingreso))
        
        log.info(f"Ingreso por QR registrado para aprendiz {datos.documento_aprendiz}")
        return {
            "accion": "ingreso_exitoso", 
            "mensaje": "Ingreso a clase registrado. ¡Bienvenido!",
            "documento_aprendiz": datos.documento_aprendiz
        }
    else:
        # 🔴 SEGUNDA VEZ: Salida
        if not salida_habilitada:
            raise HTTPException(
                status_code=403, 
                detail="Aún se encuentran en clases. Espera a que el instructor habilite la salida."
            )
        
        # Quemamos el QR y notificamos firma
        await redis_client.delete(clave_redis)
        payload_salida = {"documento": datos.documento_aprendiz, "accion": "requiere_firma"}
        await redis_client.setex(f"ultimo_scan:{sesion_id}", 5, json.dumps(payload_salida))
        
        log.info(f"Salida por QR autorizada para aprendiz {datos.documento_aprendiz}")
        return {
            "accion": "requiere_firma", 
            "mensaje": "Clase finalizada. Procede a firmar en la tablet del instructor.",
            "documento_aprendiz": datos.documento_aprendiz
        }
    
@router.get("/ultimo-escaneo/{sesion_id}")
async def ultimo_escaneo(sesion_id: str):
    data = await redis_client.get(f"ultimo_scan:{sesion_id}")
    if data:
        await redis_client.delete(f"ultimo_scan:{sesion_id}") # Lo lee y borra la huella
        return json.loads(data)
    return {"documento": None}