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

# Determinamos si estamos en la nube (Azure App Service) o en local
IS_CLOUD_MODE = bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("ENTORNO") == "produccion")

# Global states
telemetry_data = {
    "3": 0.0,  # Banco 1 Watts
    "4": 0.0,  # Banco 2 Watts
    "5": 0.0,  # Zona 1 Watts
    "6": 0.0,  # Zona 2 Watts
    "7": 0.0,  # Zona 3 Watts
    "8": 0.0,  # Zona 4 Watts
}

# Track virtual energized states of the relays
relay_states = {
    "R3": 0,
    "R4": 0,
    "R5": 0,
    "R6": 0,
    "R7": 0,
    "R8": 0
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
                    logger.info(f"🔌 Intentando conectar al puerto Serial: {port}")
                    last_port = port
                try:
                    # ⚠️ Ojo: Abrimos el puerto fuera del cerrojo para no colgar el hilo principal si la llamada del SO se bloquea
                    temp_conn = serial.Serial(port, 9600, timeout=1)
                    with ser_lock:
                        ser_conn = temp_conn
                    logger.info(f"🟢 Conexión Serial establecida con éxito en {port}")
                except Exception as e:
                    logger.error(f"❌ Error al abrir puerto serial {port}: {e}")
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
                                    except ValueError:
                                        pass
                finally:
                    ser_lock.release()
            
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"❌ Error leyendo del puerto serial: {e}")
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

def send_serial_command(command: str) -> bool:
    global ser_conn, pending_commands
    
    if IS_CLOUD_MODE:
        pending_commands.append(command)
        logger.info(f"☁️ [Cloud Mode] Comando '{command}' encolado. ({len(pending_commands)} pendientes)")
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
                logger.error(f"❌ Fallo al enviar comando serial: {e}")
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
def control_relay(payload: RelayControl):
    relay_id = payload.relay_id.upper()
    if relay_id not in ["R3", "R4", "R5", "R6", "R7", "R8"]:
        raise HTTPException(status_code=400, detail="ID de relé inválido. Usar R3-R8.")
    
    if payload.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="El estado debe ser 1 (ENCENDER) o 0 (APAGAR).")
    
    cmd = f"{relay_id}:{payload.status}"
    success = send_serial_command(cmd)
    
    # Sincronizamos el estado virtual interno
    relay_states[relay_id] = payload.status
    
    return {
        "relay_id": relay_id,
        "status": payload.status,
        "sent_to_hardware": success
    }

@router.post("/master")
def control_master(payload: MasterControl):
    if payload.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="El estado debe ser 1 (ENCENDER) o 0 (APAGAR).")
    
    cmd = f"M:{payload.status}"
    success = send_serial_command(cmd)
    
    # Sincronizar todos los estados virtuales
    for r in relay_states.keys():
        relay_states[r] = payload.status
        
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
def get_telemetry():
    return {
        "telemetry": telemetry_data,
        "relay_states": relay_states
    }

class TelemetryPushPayload(BaseModel):
    telemetry: dict
    # relay_states: dict (opcional, si el Edge device sincroniza los reles también, pero por ahora solo telemetría)

@router.post("/telemetry/push")
def push_telemetry(payload: TelemetryPushPayload):
    """
    Endpoint para que el Edge Device (Raspberry Pi) envíe los datos leídos del Arduino
    a la nube.
    """
    global telemetry_data
    for k, v in payload.telemetry.items():
        telemetry_data[str(k)] = float(v)
        
    return {"status": "ok"}

@router.get("/commands/pending")
def get_pending_commands():
    """
    Endpoint para que el Edge Device solicite los comandos encolados y los ejecute localmente.
    """
    global pending_commands
    commands_to_send = pending_commands.copy()
    pending_commands.clear()
    
    return {"commands": commands_to_send}
