import serial
import serial.tools.list_ports
import time
import json
import requests
import logging
import os

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("EdgeDevice")

# Configuración del Backend Local/Desplegado
# Se puede sobreescribir con variable de entorno (Ejemplo: http://tu-ip-publica:8000)
AZURE_API_BASE_URL = os.getenv("AZURE_API_BASE_URL", "https://voltmind-gxg9g6argxg5e9db.centralus-01.azurewebsites.net")
TELEMETRY_URL = f"{AZURE_API_BASE_URL}/api/iot/telemetry/push"
COMMANDS_URL = f"{AZURE_API_BASE_URL}/api/iot/commands/pending"

def get_serial_port():
    """Busca el puerto del Arduino, ignorando puertos Bluetooth (BTHENUM)"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        hwid = str(p.hwid).upper()
        if "BTHENUM" in hwid:
            continue
        # Asumimos que el primer dispositivo USB que no sea Bluetooth es el Arduino
        if "USB" in hwid or "ACM" in p.device or "USB" in p.device:
            return p.device
        
        # En Windows podría ser simplemente COMx (Arduino Uno)
        if "ARDUINO" in str(p.description).upper():
            return p.device
            
    # Fallback al primer puerto disponible que no sea BT si no encontramos algo explícito
    for p in ports:
        if "BTHENUM" not in str(p.hwid).upper():
            return p.device
            
    return None

def main():
    logger.info(f"🚀 Iniciando Edge Device. Enviando datos a: {TELEMETRY_URL}")
    
    ser = None
    telemetry_data = {}
    last_push_time = time.time()
    PUSH_INTERVAL = 2.0  # Enviar datos al backend cada 2 segundos
    
    while True:
        if not ser or not ser.is_open:
            port = get_serial_port()
            if port:
                try:
                    ser = serial.Serial(port, 9600, timeout=1)
                    logger.info(f"✅ Conectado al Arduino en el puerto {port}")
                    # Reiniciar el Arduino a veces requiere una pequeña espera
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"❌ Error conectando a {port}: {e}")
                    time.sleep(5)
                    continue
            else:
                logger.warning("⚠️ No se detectó Arduino. Reintentando en 5s...")
                time.sleep(5)
                continue
                
        try:
            line = ser.readline()
            if line:
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                # Formato enviado por Arduino: pin:valor (Ejemplo: 3:120.50)
                parts = decoded_line.split(":")
                if len(parts) == 2:
                    pin = parts[0]
                    val = parts[1]
                    try:
                        telemetry_data[pin] = float(val)
                    except ValueError:
                        pass
            
            # Revisar si es momento de enviar los datos a Azure
            current_time = time.time()
            if current_time - last_push_time >= PUSH_INTERVAL:
                # 1. Enviar Telemetría (solo si hay datos)
                if telemetry_data:
                    payload = {"telemetry": telemetry_data}
                    try:
                        response = requests.post(TELEMETRY_URL, json=payload, timeout=3.0)
                        if response.status_code == 200:
                            pass # logger.info(f"☁️ [Azure Push] OK - {telemetry_data}")
                        else:
                            logger.warning(f"☁️ [Azure Push] Falló con status {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as req_err:
                        logger.error(f"☁️ [Azure Push] Error de red: {req_err}")
                
                # 2. Consultar Comandos Pendientes
                try:
                    cmd_res = requests.get(COMMANDS_URL, timeout=3.0)
                    if cmd_res.status_code == 200:
                        data = cmd_res.json()
                        commands = data.get("commands", [])
                        for cmd in commands:
                            logger.info(f"⚡ [Azure Pull] Ejecutando comando recibido: {cmd}")
                            if ser and ser.is_open:
                                ser.write(f"{cmd}\n".encode('utf-8'))
                    else:
                        logger.warning(f"☁️ [Azure Pull] Falló con status {cmd_res.status_code}")
                except requests.exceptions.RequestException as req_err:
                    logger.error(f"☁️ [Azure Pull] Error de red consultando comandos: {req_err}")

                last_push_time = current_time

        except serial.SerialException as se:
            logger.error(f"🔌 Desconexión del puerto serial: {se}")
            ser = None
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
