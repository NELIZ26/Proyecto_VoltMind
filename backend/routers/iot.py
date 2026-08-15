# backend/routers/iot.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import threading
import time
import serial
import serial.tools.list_ports
import logging
import os
from typing import Dict

router = APIRouter(prefix="/api/iot", tags=["IoT"])
logger = logging.getLogger("voltmind")
from services.redis_client import get_redis_client
import json

# Determinamos si estamos en la nube (Azure App Service) o en local
IS_CLOUD_MODE = bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("ENTORNO") == "produccion")

# Global states (Solo se usan en modo local, en nube usamos Redis)
telemetry_data = {
    "3": 0.0, "4": 0.0, "5": 0.0, "6": 0.0, "7": 0.0, "8": 0.0
}
clima_data = {
    "temperatura": None, "humedad": None
}

relay_states = {
    "R3": 0, "R4": 0, "R5": 0, "R6": 0, "R7": 0, "R8": 0
}

pending_commands = []

ser_conn = None
ser_lock = threading.Lock()
running = True

class RelayControl(BaseModel):
    relay_id: str  # "R3", "R4", "R5", "R6", "R7", "R8"
    status: int    # 1 for ON, 0 for OFF

class MasterControl(BaseModel):
    status: int    # 1 for ON, 0 for OFF

def auto_detect_port():
    ports = list(serial.tools.list_ports.comports())
    # Prioridad 1: Puertos de Arduino, CH340 o USB directos (excluyendo Bluetooth)
    for p in ports:
        desc = p.description.lower()
        if "bluetooth" in desc:
            continue
        if "arduino" in desc or "ch340" in desc or "usb" in desc:
            return p.device
            
    # Prioridad 2: Cualquier puerto serie genérico (excluyendo Bluetooth)
    for p in ports:
        desc = p.description.lower()
        if "bluetooth" in desc:
            continue
        if "serial" in desc or "uart" in desc:
            return p.device
            
    if ports:
        # Fallback al primero disponible si no hay match
        return ports[0].device
    return None

def serial_reader_thread():
    global ser_conn, running
    last_port = None
    
    while running:
        if ser_conn is None:
            port = auto_detect_port()
            if port:
                if port != last_port:
                    logger.info(f" Intentando conectar al puerto Serial: {port}")
                    last_port = port
                try:
                    # ⚠️ Ojo: Abrimos el puerto fuera del cerrojo para no colgar el hilo principal si la llamada del SO se bloquea
                    temp_conn = serial.Serial(port, 9600, timeout=1)
                    with ser_lock:
                        ser_conn = temp_conn
                    logger.info(f" Conexión Serial establecida con éxito en {port}")
                except Exception as e:
                    logger.error(f" Error al abrir puerto serial {port}: {e}")
                    ser_conn = None
                    time.sleep(5)
                    continue
            else:
                logger.warning("⚠️ No se detectaron puertos seriales activos. Reintentando...")
                time.sleep(5)
                continue

        try:
            # Leer datos usando adquisición de cerrojo con timeout defensivo
            acquired = ser_lock.acquire(timeout=1.0)
            if acquired:
                try:
                    if ser_conn and ser_conn.is_open:
                        if ser_conn.in_waiting > 0:
                            line = ser_conn.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                logger.debug(f"[Serial In] {line}")
                                parts = line.split(':')
                                if len(parts) == 2:
                                    sensor_id = parts[0]
                                    try:
                                        val = float(parts[1])
                                        if sensor_id in telemetry_data:
                                            telemetry_data[sensor_id] = val
                                            # Intentar guardar en Redis en un hilo asíncrono si fuera necesario,
                                            # pero en modo local la variable global es suficiente.
                                    except ValueError:
                                        pass
                finally:
                    ser_lock.release()
            
            time.sleep(0.1)
        except Exception as e:
            logger.error(f" Error leyendo del puerto serial: {e}")
            acquired = ser_lock.acquire(timeout=1.0)
            if acquired:
                try:
                    if ser_conn:
                        try:
                            ser_conn.close()
                        except:
                            pass
                        ser_conn = None
                finally:
                    ser_lock.release()
            time.sleep(2)

async def send_command_async(command: str) -> bool:
    global ser_conn, pending_commands
    
    if IS_CLOUD_MODE:
        try:
            r = await get_redis_client()
            await r.rpush("iot:pending_commands", command)
            logger.info(f"☁️ [Cloud Mode] Comando '{command}' encolado en Redis.")
            return True
        except Exception as e:
            logger.error(f"❌ Error encolando comando en Redis: {e}")
            pending_commands.append(command)
            return True

    # Intentamos adquirir el cerrojo con timeout de 2 segundos para evitar deadlocks en la API
    acquired = ser_lock.acquire(timeout=2.0)
    if not acquired:
        logger.warning(f"⚠️ Lock Contention: No se pudo adquirir el cerrojo serial para enviar el comando '{command}'")
        return False
        
    try:
        if ser_conn and ser_conn.is_open:
            try:
                msg = f"{command}\n"
                ser_conn.write(msg.encode('utf-8'))
                logger.info(f"✈️ [Serial Out] Enviado: {command}")
                return True
            except Exception as e:
                logger.error(f" Fallo al enviar comando serial: {e}")
        else:
            logger.warning(f"⚠️ Comando '{command}' no enviado: Puerto serial no conectado.")
    finally:
        ser_lock.release()
    return False

# Iniciar hilo de lectura serial en background al importar/iniciar
if IS_CLOUD_MODE:
    logger.info("INFO - Modo Nube: Lectura de puertos seriales deshabilitada. Esperando datos vía HTTP")
else:
    reader_t = threading.Thread(target=serial_reader_thread, daemon=True)
    reader_t.start()

@router.post("/relay")
async def control_relay(payload: RelayControl):
    relay_id = payload.relay_id.upper()
    if relay_id not in ["R3", "R4", "R5", "R6", "R7", "R8"]:
        raise HTTPException(status_code=400, detail="ID de relé inválido. Usar R3-R8.")
    
    if payload.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="El estado debe ser 1 (ENCENDER) o 0 (APAGAR).")
    
    cmd = f"{relay_id}:{payload.status}"
    success = await send_command_async(cmd)
    
    # Sincronizamos el estado virtual interno
    relay_states[relay_id] = payload.status
    if IS_CLOUD_MODE:
        r = await get_redis_client()
        await r.hset("iot:relay_states", relay_id, payload.status)
    
    return {
        "relay_id": relay_id,
        "status": payload.status,
        "sent_to_hardware": success
    }

@router.post("/master")
async def control_master(payload: MasterControl):
    if payload.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="El estado debe ser 1 (ENCENDER) o 0 (APAGAR).")
    
    cmd = f"M:{payload.status}"
    success = await send_command_async(cmd)
    
    # Sincronizar todos los estados virtuales
    r = await get_redis_client() if IS_CLOUD_MODE else None
    for r_id in relay_states.keys():
        relay_states[r_id] = payload.status
        if r:
            await r.hset("iot:relay_states", r_id, payload.status)
        
    return {
        "status": payload.status,
        "sent_to_hardware": success
    }

@router.get("/ports")
def list_detected_ports():
    ports = list(serial.tools.list_ports.comports())
    return {
        "ports": [
            {
                "device": p.device,
                "description": p.description,
                "hwid": p.hwid
            } for p in ports
        ]
    }

@router.get("/telemetry")
async def get_telemetry():
    if IS_CLOUD_MODE:
        r = await get_redis_client()
        stored_states = await r.hgetall("iot:relay_states")
        stored_tel = await r.hgetall("iot:telemetry")
        stored_clima = await r.hgetall("iot:clima")
        
        # Merge con default values para evitar KeyError en frontend
        for k, v in stored_states.items():
            relay_states[k] = int(v)
        for k, v in stored_tel.items():
            telemetry_data[k] = float(v)
        for k, v in stored_clima.items():
            clima_data[k] = float(v) if v != "None" else None
            
    return {
        "telemetry": telemetry_data,
        "relay_states": relay_states,
        "clima": clima_data
    }

from typing import Optional

class TelemetryPushPayload(BaseModel):
    telemetry: dict
    clima: Optional[dict] = None
    # relay_states: dict (opcional, si el Edge device sincroniza los reles también, pero por ahora solo telemetría)

@router.post("/telemetry/push")
async def push_telemetry(payload: TelemetryPushPayload):
    """
    Endpoint para que el Edge Device (Raspberry Pi) envíe los datos leídos del Arduino
    a la nube.
    """
    global telemetry_data, clima_data
    r = await get_redis_client() if IS_CLOUD_MODE else None
    
    # 1. Guardar Telemetría
    for k, v in payload.telemetry.items():
        telemetry_data[str(k)] = float(v)
        if r:
            await r.hset("iot:telemetry", str(k), float(v))
            
    # 2. Guardar Clima
    if payload.clima:
        for k, v in payload.clima.items():
            clima_data[k] = float(v) if v is not None else None
            if r:
                await r.hset("iot:clima", str(k), str(v))
        
    return {"status": "ok"}

@router.get("/commands/pending")
async def get_pending_commands():
    """
    Endpoint para que el Edge Device solicite los comandos encolados y los ejecute localmente.
    """
    global pending_commands
    commands_to_send = []
    
    if IS_CLOUD_MODE:
        try:
            r = await get_redis_client()
            cmds = await r.lrange("iot:pending_commands", 0, -1)
            if cmds:
                await r.delete("iot:pending_commands")
                commands_to_send = [str(c) for c in cmds]
        except Exception as e:
            logger.error(f"❌ Error leyendo comandos de Redis: {e}")
            
    if pending_commands:
        commands_to_send.extend(pending_commands.copy())
        pending_commands.clear()
        
    return {"commands": commands_to_send}

async def queue_buzzer_command(status: int):
    """
    Helper function to queue a buzzer command (1=Success, 0=Error) from other routers
    """
    command = f"BUZZER:{status}"
    if IS_CLOUD_MODE:
        try:
            r = await get_redis_client()
            await r.rpush("iot:pending_commands", command)
        except Exception as e:
            logger.error(f"❌ Error encolando buzzer en Redis: {e}")
            pending_commands.append(command)
    else:
        pending_commands.append(command)
    logger.info(f" Comando de Buzzer encolado: {command}")


class RFIDPayload(BaseModel):
    uid: str

@router.post("/rfid")
async def validate_rfid(payload: RFIDPayload):
    """
    Endpoint para validar una tarjeta RFID física enviada por el Edge Device.
    Responde con success=True para hacer sonar el buzzer.
    """
    logger.info(f" Solicitud de validación RFID recibida: UID={payload.uid}")
    
    # Aquí iría la lógica real contra Dataverse. Por ahora:
    # TODO: Implementar búsqueda en Dataverse y registro de asistencia.
    
    return {"success": True, "message": "Acceso concedido (Simulado)"}

class HilaConsumo(BaseModel):
    sensor_id: str
    consumo_clase: float
    consumo_extra: float

class ClimaHistorial(BaseModel):
    timestamp: str
    temperatura: float
    humedad: float

class ClimaData(BaseModel):
    promedio_temperatura: Optional[float] = None
    promedio_humedad: Optional[float] = None
    historial: list[ClimaHistorial] = []

class SessionConsumptionPayload(BaseModel):
    session_id: str
    hilas: list[HilaConsumo]
    clima: Optional[ClimaData] = None

@router.post("/session/close")
async def save_session_consumption(payload: SessionConsumptionPayload):
    from services.dataverse import obtener_cliente
    client = obtener_cliente()
    
    total_clase = 0.0
    total_extra = 0.0
    
    for hila in payload.hilas:
        total_clase += hila.consumo_clase
        total_extra += hila.consumo_extra
        
        # Guardar en cr6a3_consumo_electrico
        datos_hila = {
            "cr6a3_identificador_medidor": hila.sensor_id,
            "cr6a3_lectura_acumulada_kwh": round(hila.consumo_clase + hila.consumo_extra, 6),
            "cr6a3_Codigo_Sesion@odata.bind": f"/cr6a3_sesiones_de_clases({payload.session_id})"
        }
        await client.post("cr6a3_consumo_electricos", json=datos_hila)
    
    # Guardar historial de clima cada 10/5 minutos
    if payload.clima and payload.clima.historial:
        for c_log in payload.clima.historial:
            datos_clima = {
                "cr6a3_temperatura": c_log.temperatura,
                "cr6a3_humedad": c_log.humedad,
                "cr6a3_timestamp": c_log.timestamp,
                "cr6a3_Codigo_Sesion@odata.bind": f"/cr6a3_sesiones_de_clases({payload.session_id})"
            }
            try:
                await client.post("cr6a3_registro_climas", json=datos_clima)
            except Exception as e:
                logger.error(f"Error guardando historial de clima en Dataverse: {e}")
    
    # Actualizar la sesión con los totales y el clima promedio
    totales_sesion = {
        "cr6a3_consumo_clase_kwh": round(total_clase, 6),
        "cr6a3_consumo_extra_kwh": round(total_extra, 6),
        "cr6a3_consumo_energetico_total_kwh": round(total_clase + total_extra, 6)
    }
    
    if payload.clima and payload.clima.promedio_temperatura is not None:
        totales_sesion["cr6a3_temperatura_promedio"] = payload.clima.promedio_temperatura
        totales_sesion["cr6a3_humedad_promedio"] = payload.clima.promedio_humedad

    await client.patch(f"cr6a3_sesiones_de_clases({payload.session_id})", json=totales_sesion)
    
    return {"status": "ok"}

