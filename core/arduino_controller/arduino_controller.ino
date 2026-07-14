// Pines de los relés (Salidas Digitales)
const int rele1 = 7;
const int rele2 = 8;
const int rele3 = 6;

// Pines de los sensores de corriente ACS712 (Entradas Analógicas)
const int sensor1 = A0; // Sensor 1 (ej: Iluminación)
const int sensor2 = A1; // Sensor 2 (ej: Bancos de Cómputo)
const int sensor3 = A2; // Sensor 3 (ej: Equipos Auxiliares)

// Constantes para el cálculo de potencia
const float VOLTAJE_RED = 120.0; // Cambiar a 220.0 si es necesario
const float SENSIBILIDAD_ACS712 = 0.185; // 185mV/A para modelo de 5A (0.100 para 20A, 0.066 para 30A)

unsigned long tiempoAnterior = 0;
const long intervaloEnvio = 2000; // Enviar lecturas cada 2 segundos

void setup() {
  // Inicializar comunicación serial a 9600 baudios
  Serial.begin(9600);

  // Configurar pines de relés como salidas
  pinMode(rele1, OUTPUT);
  pinMode(rele2, OUTPUT);
  pinMode(rele3, OUTPUT);

  // ESTADO INICIAL: APAGADO
  // Como los relés se activan en LOW, el estado inicial apagado debe ser HIGH
  digitalWrite(rele1, HIGH);
  digitalWrite(rele2, HIGH);
  digitalWrite(rele3, HIGH);
}

void loop() {
  // 1. Escuchar comandos desde la Raspberry Pi
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim(); // Eliminar espacios o saltos de línea extra

    int separadorIndex = comando.indexOf(':');
    if (separadorIndex != -1) {
      String idStr = comando.substring(0, separadorIndex);
      String estadoStr = comando.substring(separadorIndex + 1);

      int estado = estadoStr.toInt(); // '1' para ENCENDER, '0' para APAGAR
      // Lógica Inversa: Si estado es 1 (Encender), escribimos LOW. Si es 0 (Apagar), escribimos HIGH.
      int valorPin = (estado == 1) ? LOW : HIGH;

      if (idStr == "L1") {
        digitalWrite(rele1, valorPin);
      } else if (idStr == "L2") {
        digitalWrite(rele2, valorPin);
      } else if (idStr == "L3") {
        digitalWrite(rele3, valorPin);
      } else if (idStr == "M") {
        // Master: Aplica el comando a todos
        digitalWrite(rele1, valorPin);
        digitalWrite(rele2, valorPin);
        digitalWrite(rele3, valorPin);
      }
    }
  }

  // 2. Leer consumo y enviar telemetría
  unsigned long tiempoActual = millis();
  if (tiempoActual - tiempoAnterior >= intervaloEnvio) {
    tiempoAnterior = tiempoActual;

    // Calcular watts para los sensores
    float watts1 = calcularWatts(sensor1);
    float watts2 = calcularWatts(sensor2);
    float watts3 = calcularWatts(sensor3);
    
    // Enviar por serial en formato ID:WATTS
    Serial.print("1:");
    Serial.println(watts1);
    Serial.print("2:");
    Serial.println(watts2);
    Serial.print("3:");
    Serial.println(watts3);
  }
}

float calcularWatts(int pinSensor) {
  // Función básica para obtener el consumo RMS de un ACS712
  // Toma varias muestras para encontrar el valor máximo y mínimo y calcular la onda
  int valorMinimo = 1024;
  int valorMaximo = 0;
  
  unsigned long inicioMuestreo = millis();
  while (millis() - inicioMuestreo < 50) { // Muestrear por 50ms (aprox. 3 ciclos de 60Hz)
    int valorLeido = analogRead(pinSensor);
    if (valorLeido < valorMinimo) valorMinimo = valorLeido;
    if (valorLeido > valorMaximo) valorMaximo = valorLeido;
  }
  
  // Calcular la amplitud pico a pico en voltios
  float voltajePicoPico = ((valorMaximo - valorMinimo) * 5.0) / 1024.0;
  
  // Calcular voltaje RMS
  float voltajeRMS = voltajePicoPico / 2.0 * 0.707;
  
  // Calcular corriente RMS
  float corrienteRMS = voltajeRMS / SENSIBILIDAD_ACS712;
  
  // (Filtro de ruido removido temporalmente para que veas que el sensor sí lee)
  // if (corrienteRMS < 0.15) corrienteRMS = 0.0;
  
  // Calcular Watts
  float watts = corrienteRMS * VOLTAJE_RED;
  
  return watts;
}
