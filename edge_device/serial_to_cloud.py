import serial
import serial.tools.list_ports
import time
import json
import requests
import logging
import os
import sqlite3
from datetime import datetime
from dht22_sensor import leer_clima

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("EdgeDevice")

# Configuración del Backend Local/Desplegado
AZURE_API_BASE_URL = os.getenv("AZURE_API_BASE_URL", "https://voltmind2-fmh3b5esa0htdxf8.centralus-01.azurewebsites.net")
TELEMETRY_URL = f"{AZURE_API_BASE_URL}/api/iot/telemetry/push"
COMMANDS_URL = f"{AZURE_API_BASE_URL}/api/iot/commands/pending"

# Lista blanca de sensores válidos
VALID_SENSORS = ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5", "Sensor 6", "Sensor 7", "Sensor 8"]

def init_local_db():
    try:
        conn = sqlite3.connect("voltmind_local.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_local (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sensor_id TEXT,
                promedio_watts REAL,
                consumo_kwh REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clima_local (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperatura REAL,
                humedad REAL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("🗄️ Base de datos local (SQLite) inicializada correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al inicializar SQLite: {e}")

def get_serial_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "rfcomm" in p.device.lower():
            return p.device
    for p in ports:
        hwid = str(p.hwid).upper()
        if "USB" in hwid or "ACM" in p.device or "USB" in p.device:
            return p.device
        if "ARDUINO" in str(p.description).upper():
            return p.device
    for p in ports:
        if "BTHENUM" not in str(p.hwid).upper():
            return p.device
    return None

def calcular_y_enviar_consumos(session_id, hora_limite_sql):
    try:
        conn = sqlite3.connect("voltmind_local.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sensor_id FROM consumo_local")
        sensores = cursor.fetchall()
        hilas_data = []
        for (sensor_id,) in sensores:
            cursor.execute("SELECT SUM(consumo_kwh) FROM consumo_local WHERE sensor_id = ? AND timestamp <= ?", (sensor_id, hora_limite_sql))
            clase_val = cursor.fetchone()[0] or 0.0
            cursor.execute("SELECT SUM(consumo_kwh) FROM consumo_local WHERE sensor_id = ? AND timestamp > ?", (sensor_id, hora_limite_sql))
            extra_val = cursor.fetchone()[0] or 0.0
            hilas_data.append({
                "sensor_id": str(sensor_id),
                "consumo_clase": round(clase_val, 6),
                "consumo_extra": round(extra_val, 6)
            })
        
        # Sacar el promedio y los registros de clima
        cursor.execute("SELECT AVG(temperatura), AVG(humedad) FROM clima_local WHERE timestamp <= ?", (hora_limite_sql,))
        clima_promedio = cursor.fetchone()
        
        cursor.execute("SELECT timestamp, temperatura, humedad FROM clima_local WHERE timestamp <= ?", (hora_limite_sql,))
        clima_historial = cursor.fetchall()
        
        clima_data = {
            "promedio_temperatura": round(clima_promedio[0], 2) if clima_promedio[0] else None,
            "promedio_humedad": round(clima_promedio[1], 2) if clima_promedio[1] else None,
            "historial": [
                {"timestamp": c[0], "temperatura": c[1], "humedad": c[2]} for c in clima_historial
            ]
        }
            
        # Enviar al backend para que registre en Dataverse
        payload = {
            "session_id": session_id,
            "hilas": hilas_data,
            "clima": clima_data
        }
        
        close_url = f"{AZURE_API_BASE_URL}/api/iot/session/close"
        response = requests.post(close_url, json=payload, timeout=5.0)
        
        if response.status_code == 200:
            logger.info("✅ [SQLite] Consumos y Clima calculados y enviados al backend exitosamente.")
            # Limpiar datos para la próxima clase
            cursor.execute("DELETE FROM consumo_local")
            cursor.execute("DELETE FROM clima_local")
            conn.commit()
        else:
            logger.error(f"❌ [Azure] Falló el envío de consumos de cierre: {response.text}")
        conn.close()
    except Exception as e:
        logger.error(f"❌ Error calculando consumos en SQLite: {e}")

def main():
    logger.info(f"🚀 Iniciando Edge Device. Enviando datos a: {TELEMETRY_URL}")
    init_local_db()
    ser = None
    telemetry_data = {}
    last_push_time = time.time()
    last_db_save_time = time.time()
    PUSH_INTERVAL = 2.0
    DB_SAVE_INTERVAL = 300.0
    # Diccionario para ir acumulando los Watts de cada sensor durante los 5 minutos
    power_accumulators = {} 
    
    clima_accumulator = {'temp_sum': 0.0, 'hum_sum': 0.0, 'count': 0}
    
    # TAREA CADA 5 MINUTOS: Guardar Consumo Local (SQLite)
    def flush_accumulators_to_db(interval_seconds):
        nonlocal power_accumulators, clima_accumulator
        if not power_accumulators:
            return
        try:
            conn = sqlite3.connect("voltmind_local.db")
            cursor = conn.cursor()
            for sensor_pin, data in power_accumulators.items():
                if data['count'] > 0:
                    avg_watts = data['sum'] / data['count']
                    horas = interval_seconds / 3600.0
                    kwh_consumido = (avg_watts / 1000.0) * horas
                    cursor.execute('''
                        INSERT INTO consumo_local (sensor_id, promedio_watts, consumo_kwh)
                        VALUES (?, ?, ?)
                    ''', (sensor_pin, round(avg_watts, 2), round(kwh_consumido, 6)))
                    
            if clima_accumulator['count'] > 0:
                avg_temp = clima_accumulator['temp_sum'] / clima_accumulator['count']
                avg_hum = clima_accumulator['hum_sum'] / clima_accumulator['count']
                cursor.execute('''
                    INSERT INTO clima_local (temperatura, humedad)
                    VALUES (?, ?)
                ''', (round(avg_temp, 2), round(avg_hum, 2)))
                
            conn.commit()
            conn.close()
            logger.info("💾 [SQLite] Consumo y clima local guardado exitosamente.")
        except Exception as e:
            logger.error(f"❌ [SQLite] Error guardando en BD local: {e}")
        power_accumulators = {}
        clima_accumulator = {'temp_sum': 0.0, 'hum_sum': 0.0, 'count': 0}

    while True:
        if not ser or not ser.is_open:
            port = get_serial_port()
            if port:
                try:
                    ser = serial.Serial(port, 9600, timeout=1)
                    logger.info(f"✅ Conectado al Arduino en el puerto {port}")
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
                parts = decoded_line.split(":")
                
                if len(parts) == 2:
                    pin_arduino = parts[0].strip() # Aquí llega el "3", "4", "RFID", etc.
                    val = parts[1].strip()
                    
                    if pin_arduino == "RFID":
                        uid = val
                        logger.info(f"🔑 Tarjeta RFID detectada: {uid}")
                        try:
                            res = requests.post(f"{AZURE_API_BASE_URL}/api/iot/rfid", json={"uid": uid}, timeout=3)
                            if res.status_code == 200 and res.json().get("success"):
                                logger.info("✅ Acceso Concedido")
                                if ser: ser.write(b"BUZZER:1\n")
                            else:
                                logger.warning("❌ Acceso Denegado")
                                if ser: ser.write(b"BUZZER:0\n")
                        except Exception as e:
                            logger.error(f"Error validando RFID: {e}")
                            if ser: ser.write(b"BUZZER:0\n")
                        continue # Salta el resto de lógica
                    
                    # --- AQUÍ ESTÁ LA MAGIA ---
                    # Transformamos el "3" del Arduino en "Sensor 3" para que coincida con Dataverse
                    pin_formateado = f"Sensor {pin_arduino}"

                    if pin_formateado in VALID_SENSORS:
                        try:
                            watts = float(val)
                            telemetry_data[pin_formateado] = watts
                            if pin_formateado not in power_accumulators:
                                power_accumulators[pin_formateado] = {'sum': 0.0, 'count': 0}
                            power_accumulators[pin_formateado]['sum'] += watts
                            power_accumulators[pin_formateado]['count'] += 1
                        except ValueError:
                            pass
                    else:
                        pass # Ignorar ruido
                        
                    if pin_formateado in VALID_SENSORS:
                        try:
                            watts = float(val)
                            telemetry_data[pin_formateado] = watts
                            if pin_formateado not in power_accumulators:
                                power_accumulators[pin_formateado] = {'sum': 0.0, 'count': 0}
                            power_accumulators[pin_formateado]['sum'] += watts
                            power_accumulators[pin_formateado]['count'] += 1
                        except ValueError:
                            pass
                    else:
                        pass # Ignorar ruido

            current_time = time.time()
            
            # TAREA CADA 2 SEGUNDOS: Actualizar Frontend en Azure
            if current_time - last_push_time >= PUSH_INTERVAL:
                # 🌡️ Integrar la lectura de Clima
                temp, hum = leer_clima()
                clima_payload = None
                if temp is not None:
                    clima_payload = {"temperatura": temp, "humedad": hum}
                    clima_accumulator['temp_sum'] += temp
                    clima_accumulator['hum_sum'] += hum
                    clima_accumulator['count'] += 1
                
                if telemetry_data or clima_payload:
                    payload = {"telemetry": telemetry_data}
                    if clima_payload:
                        payload["clima"] = clima_payload
                        
                    try:
                        response = requests.post(TELEMETRY_URL, json=payload, timeout=3.0)
                        if response.status_code != 200:
                            logger.warning(f"☁️ [Azure Push] Falló con status {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as req_err:
                        logger.error(f"☁️ [Azure Push] Error de red: {req_err}")
                
                # Pull de comandos
                try:
                    cmd_res = requests.get(COMMANDS_URL, timeout=3.0)
                    if cmd_res.status_code == 200:
                        data = cmd_res.json()
                        commands = data.get("commands", [])
                        for cmd in commands:
                            logger.info(f"⚡ [Azure Pull] Ejecutando comando recibido: {cmd}")
                            if cmd.startswith("CLOSE_SESSION:"):
                                parts = cmd.split(":", 2)
                                if len(parts) == 3:
                                    _, session_id, hora_limite_iso = parts
                                    hora_limite_sql = hora_limite_iso.replace("T", " ")[:19] 
                                    if ser and ser.is_open:
                                        ser.write("M:0\n".encode('utf-8'))
                                    
                                    # Guardar consumo acumulado antes de cerrar
                                    elapsed_since_last_save = current_time - last_db_save_time
                                    flush_accumulators_to_db(elapsed_since_last_save)
                                    last_db_save_time = current_time
                                    
                                    calcular_y_enviar_consumos(session_id, hora_limite_sql)
                            else:
                                if ser and ser.is_open:
                                    ser.write(f"{cmd}\n".encode('utf-8'))
                    else:
                        logger.warning(f"☁️ [Azure Pull] Falló con status {cmd_res.status_code}")
                except requests.exceptions.RequestException as req_err:
                    logger.error(f"☁️ [Azure Pull] Error de red: {req_err}")
                    
                last_push_time = current_time

            # TAREA CADA 5 MINUTOS: Guardar Consumo Local (SQLite)
            if current_time - last_db_save_time >= DB_SAVE_INTERVAL:
                flush_accumulators_to_db(DB_SAVE_INTERVAL)
                last_db_save_time = current_time

        except serial.SerialException as se:
            logger.error(f"🔌 Desconexión del puerto serial: {se}")
            ser = None
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()