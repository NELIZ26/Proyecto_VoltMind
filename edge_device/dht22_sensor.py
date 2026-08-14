import time
import board
import adafruit_dht

# Inicializamos el dispositivo fuera de la función para no instanciarlo repetidamente.
# board.D4 corresponde al GPIO 4 (Pin físico 7).
# Si adafruit_dht no está disponible en entorno de desarrollo, capturamos el error
# para que no falle todo el sistema si se ejecuta en una PC de prueba.
try:
    sensor_dht = adafruit_dht.DHT22(board.D4)
    sensor_disponible = True
except Exception as e:
    print(f"⚠️ No se pudo inicializar DHT22 (¿Estás en la Raspberry?): {e}")
    sensor_disponible = False

def leer_clima(max_reintentos=3):
    """
    Lee la temperatura y humedad del sensor DHT22.
    """
    if not sensor_disponible:
        return None, None
        
    for intento in range(max_reintentos):
        try:
            temperatura = sensor_dht.temperature
            humedad = sensor_dht.humidity
            
            if temperatura is not None and humedad is not None:
                return round(temperatura, 1), round(humedad, 1)
                
        except RuntimeError:
            # Errores comunes de timing en lectura
            time.sleep(2.0)
            continue
        except Exception as e:
            print(f"❌ Error fatal leyendo el DHT22: {e}")
            break
            
    return None, None
