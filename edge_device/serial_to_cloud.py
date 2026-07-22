import serial
import serial.tools.list_ports
import time
import json
import requests
import logging
import os
import sqlite3  # <-- NUEVO: Para la base de datos local
from datetime import datetime # <-- NUEVO: Para las fechas de registro

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("EdgeDevice")

# Configuración del Backend Local/Desplegado
AZURE_API_BASE_URL = os.getenv("AZURE_API_BASE_URL", "https://voltmind-gxg9g6argxg5e9db.centralus-01.azurewebsites.net")
TELEMETRY_URL = f"{AZURE_API_BASE_URL}/api/iot/telemetry/push"
COMMANDS_URL = f"{AZURE_API_BASE_URL}/api/iot/commands/pending"

# --- NUEVA FUNCIÓN: Inicializar Base de Datos SQLite ---
def init_local_db():
    """Crea la base de datos local y la tabla si no existen."""
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
        conn.commit()
        conn.close()
        logger.info("🗄️ Base de datos local (SQLite) inicializada correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al inicializar SQLite: {e}")

def get_serial_port():
    """Busca el puerto del Arduino, ignorando puertos Bluetooth (BTHENUM)"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        hwid = str(p.hwid).upper()
        if "BTHENUM" in hwid:
            continue
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
        
        # Sacar los sensores únicos guardados
        cursor.execute("SELECT DISTINCT sensor_id FROM consumo_local")
        sensores = cursor.fetchall()
        
        hilas_data = []
        
        for (sensor_id,) in sensores:
            # Consumo de clase (<= hora limite)
            cursor.execute("SELECT SUM(consumo_kwh) FROM consumo_local WHERE sensor_id = ? AND timestamp <= ?", (sensor_id, hora_limite_sql))
            clase_val = cursor.fetchone()[0] or 0.0
            
            # Consumo extra (> hora limite)
            cursor.execute("SELECT SUM(consumo_kwh) FROM consumo_local WHERE sensor_id = ? AND timestamp > ?", (sensor_id, hora_limite_sql))
            extra_val = cursor.fetchone()[0] or 0.0
            
            hilas_data.append({
                "sensor_id": str(sensor_id),
                "consumo_clase": round(clase_val, 6),
                "consumo_extra": round(extra_val, 6)
            })
            
        # Enviar al backend para que registre en Dataverse
        payload = {
            "session_id": session_id,
            "hilas": hilas_data
        }
        
        close_url = f"{AZURE_API_BASE_URL}/api/iot/session/close"
        response = requests.post(close_url, json=payload, timeout=5.0)
        
        if response.status_code == 200:
            logger.info("✅ [SQLite] Consumos calculados y enviados al backend exitosamente.")
            # Limpiar datos para la próxima clase
            cursor.execute("DELETE FROM consumo_local")
            conn.commit()
        else:
            logger.error(f"❌ [Azure] Falló el envío de consumos de cierre: {response.text}")
            
        conn.close()
    except Exception as e:
        logger.error(f"❌ Error calculando consumos en SQLite: {e}")

def main():
    logger.info(f"🚀 Iniciando Edge Device. Enviando datos a: {TELEMETRY_URL}")
    
    # Preparamos la BD antes de empezar el ciclo
    init_local_db()
    
    ser = None
    telemetry_data = {}
    
    # Temporizadores
    last_push_time = time.time()
    last_db_save_time = time.time()
    
    PUSH_INTERVAL = 2.0     # Enviar a Azure cada 2 segundos (Frontend)
    DB_SAVE_INTERVAL = 300.0 # Guardar en SQLite cada 300 segundos (5 minutos)
    
    # Diccionario para ir acumulando los Watts de cada sensor durante los 5 minutos
    power_accumulators = {} 
    
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
                    pin = parts[0]
                    val = parts[1]
                    try:
                        watts = float(val)
                        telemetry_data[pin] = watts
                        
                        # --- NUEVA LÓGICA: Acumular para el promedio de 5 minutos ---
                        if pin not in power_accumulators:
                            power_accumulators[pin] = {'sum': 0.0, 'count': 0}
                        
                        power_accumulators[pin]['sum'] += watts
                        power_accumulators[pin]['count'] += 1
                        
                    except ValueError:
                        pass
            
            current_time = time.time()
            
            # =================================================================
            # 1. TAREA CADA 2 SEGUNDOS: Actualizar Frontend en Azure
            # =================================================================
            if current_time - last_push_time >= PUSH_INTERVAL:
                if telemetry_data:
                    payload = {"telemetry": telemetry_data}
                    try:
                        response = requests.post(TELEMETRY_URL, json=payload, timeout=3.0)
                        if response.status_code != 200:
                            logger.warning(f"☁️ [Azure Push] Falló con status {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as req_err:
                        logger.error(f"☁️ [Azure Push] Error de red: {req_err}")
                
                try:
                    cmd_res = requests.get(COMMANDS_URL, timeout=3.0)
                    if cmd_res.status_code == 200:
                        data = cmd_res.json()
                        commands = data.get("commands", [])
                        for cmd in commands:
                            logger.info(f"⚡ [Azure Pull] Ejecutando comando recibido: {cmd}")
                            
                            # --- NUEVA LÓGICA: Detección de Cierre de Sesión ---
                            if cmd.startswith("CLOSE_SESSION:"):
                                parts = cmd.split(":", 2)
                                if len(parts) == 3:
                                    _, session_id, hora_limite_iso = parts
                                    # Convertimos el ISO a string de SQLite (YYYY-MM-DD HH:MM:SS)
                                    hora_limite_sql = hora_limite_iso.replace("T", " ")[:19] 
                                    
                                    # Apagamos el Arduino
                                    if ser and ser.is_open:
                                        ser.write("M:0\n".encode('utf-8'))
                                        
                                    # Calculamos los consumos
                                    calcular_y_enviar_consumos(session_id, hora_limite_sql)
                            else:
                                if ser and ser.is_open:
                                    ser.write(f"{cmd}\n".encode('utf-8'))
                    else:
                        logger.warning(f"☁️ [Azure Pull] Falló con status {cmd_res.status_code}")
                except requests.exceptions.RequestException as req_err:
                    logger.error(f"☁️ [Azure Pull] Error de red: {req_err}")

                last_push_time = current_time

            # =================================================================
            # 2. TAREA CADA 5 MINUTOS: Guardar Consumo Local (SQLite)
            # =================================================================
            if current_time - last_db_save_time >= DB_SAVE_INTERVAL:
                try:
                    conn = sqlite3.connect("voltmind_local.db")
                    cursor = conn.cursor()
                    
                    for sensor_pin, data in power_accumulators.items():
                        if data['count'] > 0:
                            # Promedio de Watts en estos 5 minutos
                            avg_watts = data['sum'] / data['count']
                            
                            # Fórmula: kWh = (Watts / 1000) * Horas
                            # 5 minutos equivalen a (5 / 60) horas o (300 segundos / 3600)
                            horas = DB_SAVE_INTERVAL / 3600.0
                            kwh_consumido = (avg_watts / 1000.0) * horas
                            
                            cursor.execute('''
                                INSERT INTO consumo_local (sensor_id, promedio_watts, consumo_kwh)
                                VALUES (?, ?, ?)
                            ''', (sensor_pin, round(avg_watts, 2), round(kwh_consumido, 6)))
                            
                    conn.commit()
                    conn.close()
                    logger.info("💾 [SQLite] Lote de consumo de 5 minutos guardado exitosamente.")
                    
                except Exception as e:
                    logger.error(f"❌ [SQLite] Error guardando en BD local: {e}")
                
                # Reiniciar los acumuladores para los próximos 5 minutos
                power_accumulators = {}
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