from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import serial
import threading
import time

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

# Inicializamos el puerto serial (lo intentamos abrir)
ser = None
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Conectado al Arduino en el puerto: {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Error abriendo el puerto USB {SERIAL_PORT}: {e}")

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
                                print(f"⚠️ PICO ALTO en Línea {sensor_id}: {watts}W. ¡Apagando Relé de emergencia!")
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
        print(f"🔧 MODO SIMULACIÓN: Comando enviado -> Relé {command.rele}: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
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
        print(f"🔧 MODO SIMULACIÓN: Comando enviado -> MASTER: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
        return {"status": "success", "message": f"[Simulado] Estado maestro configurado a {command.estado}"}
    
    # Enviar el comando M al Arduino (Ej: "M:1\n")
    comando_str = f"M:{command.estado}\n"
    ser.write(comando_str.encode('utf-8'))
    
    print(f"Comando enviado -> MASTER: {'ENCENDER' if command.estado == '1' else 'APAGAR'}")
    return {"status": "success", "message": f"Estado maestro configurado a {command.estado}"}

@router.get("/telemetry")
async def get_telemetry():
    """ Devuelve la última lectura de telemetría (consumo en Watts) """
    return telemetry_data
