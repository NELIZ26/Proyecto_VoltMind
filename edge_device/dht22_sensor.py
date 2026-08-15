import time
import board
import adafruit_dht

try:
    import sysv_ipc
    SYSV_IPC_EXISTS = True
except ImportError:
    SYSV_IPC_EXISTS = False

def init_sensor():
    global sensor_dht, sensor_disponible
    try:
        if 'sensor_dht' in globals() and sensor_dht is not None:
            try:
                sensor_dht.exit()
            except Exception:
                pass
        sensor_dht = adafruit_dht.DHT22(board.D4)
        sensor_disponible = True
    except Exception as e:
        print(f"⚠️ No se pudo inicializar DHT22 (¿Estás en la Raspberry?): {e}")
        sensor_disponible = False

init_sensor()

def leer_clima(max_reintentos=3):
    """
    Lee la temperatura y humedad del sensor DHT22 con auto-recuperación de colas IPC.
    """
    global sensor_disponible
    if not sensor_disponible:
        init_sensor()
        if not sensor_disponible:
            return None, None
        
    for intento in range(max_reintentos):
        try:
            temperatura = sensor_dht.temperature
            humedad = sensor_dht.humidity
            
            if temperatura is not None and humedad is not None:
                return round(temperatura, 1), round(humedad, 1)
                
        except RuntimeError:
            # Errores comunes de timing en microsegundos de Linux
            time.sleep(2.0)
            continue
        except Exception as e:
            # Captura ExistentialError de sysv_ipc y errores de pulso de hardware
            # Re-inicializamos el sensor para reconstruir la cola sin tumbar el script
            init_sensor()
            time.sleep(2.0)
            break
            
    return None, None


if __name__ == "__main__":
    print("🌡️ --- DIAGNÓSTICO EN VIVO: SENSOR DHT22 ---")
    print("Presiona Ctrl+C para salir.\n")
    while True:
        temp, hum = leer_clima()
        if temp is not None and hum is not None:
            print(f"✅ Lectura Exitosa -> Temperatura: {temp}°C | Humedad: {hum}%")
        else:
            print("⚠️ Error temporal de lectura, reintentando...")
        time.sleep(2.5)
