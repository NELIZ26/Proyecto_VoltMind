from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import serial
import threading
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/iot",
    tags=["iot"]
)

# Configuración del puerto serial
# IMPORTANTE: En Windows suele ser 'COM3', 'COM4', etc. 
# En Raspberry Pi suele ser '/dev/ttyACM0' o '/dev/ttyUSB0'.
# Cambiar si es necesario.
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

# Variable global para almacenar la última lectura de telemetría (Watts)
# Por defecto lo iniciamos en 0.0
telemetry_data = {
    "1": 0.0
}
relay_states = {}
pending_commands = []

# Inicializamos el puerto serial (lo intentamos abrir)
ser = None
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[OK] Conectado al Arduino en el puerto: {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Error abriendo el puerto USB {SERIAL_PORT}: {e}")

# Hilo en segundo plano para leer los datos del Arduino
def read_serial_data():
    global telemetry_data
    while True:
        if ser and ser.is_open:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    # Formato esperado: "1:25.40"
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) == 2:
                            sensor_id = parts[0]
                            watts = float(parts[1])
                            telemetry_data[sensor_id] = watts
                            
                            # Auto-apagado de emergencia simulado (si es necesario)
                            PICO_MAXIMO = 100.0
                            if watts > PICO_MAXIMO:
                                print(f"[WARNING] PICO ALTO en Línea {sensor_id}: {watts}W. ¡Apagando Relé de emergencia!")
                                # Enviar orden de apagado al Arduino
                                ser.write(f"{sensor_id}:0\n".encode('utf-8'))
            except Exception as e:
                print(f"Error leyendo del puerto serial: {e}")
        time.sleep(0.1)

# Iniciamos el hilo de lectura al arrancar
if ser:
    thread = threading.Thread(target=read_serial_data, daemon=True)
    thread.start()

# Modelos Pydantic para las solicitudes
class RelayCommand(BaseModel):
    rele: str
    estado: str # "1" para encender, "0" para apagar

class MasterCommand(BaseModel):
    estado: str # "1" para encender, "0" para apagar

@router.post("/relay")
async def toggle_relay(command: RelayCommand):
    """ Enciende o apaga un relé específico (1, 2, o 3) """
    if not ser or not ser.is_open:
        print(f"[SIMULATOR] MODO SIMULACIÓN: Comando enviado -> Relé {command.rele}: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
        return {"status": "success", "message": f"[Simulado] Relé {command.rele} configurado a {command.estado}"}
    
    # Enviar el comando al Arduino (Ej: "1:1\n")
    comando_str = f"{command.rele}:{command.estado}\n"
    ser.write(comando_str.encode('utf-8'))
    
    print(f"Comando enviado -> Relé {command.rele}: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
    return {"status": "success", "message": f"Relé {command.rele} configurado a {command.estado}"}

@router.post("/master")
async def toggle_master(command: MasterCommand):
    """ Enciende o apaga TODOS los relés """
    if not ser or not ser.is_open:
        print(f"[SIMULATOR] MODO SIMULACIÓN: Comando enviado -> MASTER: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
        return {"status": "success", "message": f"[Simulado] Estado maestro configurado a {command.estado}"}
    
    # Enviar el comando M al Arduino (Ej: "M:1\n")
    comando_str = f"M:{command.estado}\n"
    ser.write(comando_str.encode('utf-8'))
    
    print(f"Comando enviado -> MASTER: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
    return {"status": "success", "message": f"Estado maestro configurado a {command.estado}"}

@router.get("/telemetry")
async def get_telemetry():
    """ Devuelve la última lectura de telemetría (consumo en Watts) y los estados de relés """
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

def queue_buzzer_command(status: int):
    """
    Helper function to queue a buzzer command (1=Success, 0=Error) from other routers
    """
    global pending_commands
    command = f"BUZZER:{status}"
    pending_commands.append(command)
    logger.info(f"🔊 Comando de Buzzer encolado: {command}")

class RFIDPayload(BaseModel):
    uid: str

@router.post("/rfid")
async def validate_rfid(payload: RFIDPayload):
    """
    Endpoint para validar una tarjeta RFID física enviada por el Edge Device.
    Responde con success=True para hacer sonar el buzzer.
    """
    logger.info(f"💳 Solicitud de validación RFID recibida: UID={payload.uid}")
    
    # Aquí iría la lógica real contra Dataverse. Por ahora:
    # TODO: Implementar búsqueda en Dataverse y registro de asistencia.
    
    return {"success": True, "message": "Acceso concedido (Simulado)"}

class HilaConsumo(BaseModel):
    sensor_id: str
    consumo_clase: float
    consumo_extra: float

class SessionConsumptionPayload(BaseModel):
    session_id: str
    hilas: list[HilaConsumo]

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
    
    # Actualizar la sesión con los totales
    totales_sesion = {
        "cr6a3_consumo_clase_kwh": round(total_clase, 6),
        "cr6a3_consumo_extra_kwh": round(total_extra, 6),
        "cr6a3_consumo_energetico_total_kwh": round(total_clase + total_extra, 6)
    }
    await client.patch(f"cr6a3_sesiones_de_clases({payload.session_id})", json=totales_sesion)
    
    return {"status": "ok"}
