// =================================================================
// VoltMind - Arduino Controller (Relay & ACS712 Telemetry)
// =================================================================

// Pines de los relés (Salidas Digitales)
const int rele3 = 7; // Banco 1
const int rele4 = 6; // Banco 2
const int rele5 = 5; // Zona 1
const int rele6 = 4; // Zona 2
const int rele7 = 3; // Zona 3
const int rele8 = 2; // Zona 4

// Pines de los sensores de corriente ACS712 (Entradas Analógicas)
const int sensor3 = A4; // Medidor Banco 1
const int sensor4 = A5; // Medidor Banco 2
const int sensor5 = A3; // Medidor Zona 1
const int sensor6 = A1; // Medidor Zona 2
const int sensor7 = A2; // Medidor Zona 3
const int sensor8 = A0; // Medidor Zona 4

// Constantes para el cálculo de potencia
const float VOLTAJE_RED = 120.0; // Voltaje RMS nominal de la red en Colombia (cambiar si es necesario)
const float SENSIBILIDAD_ACS712 = 0.185; // 185mV/A para modelo de 5A. 0.100 para 20A, 0.066 para 30A.

unsigned long tiempoAnterior = 0;
const long intervaloEnvio = 2000; // Enviar lecturas cada 2 segundos

void setup() {
  // Inicializar comunicación serial a 9600 baudios
  Serial.begin(9600);

  // Configurar pines de relés como salidas
  pinMode(rele3, OUTPUT);
  pinMode(rele4, OUTPUT);
  pinMode(rele5, OUTPUT);
  pinMode(rele6, OUTPUT);
  pinMode(rele7, OUTPUT);
  pinMode(rele8, OUTPUT);

  // ESTADO INICIAL: APAGADO (Lógica Inversa: HIGH apaga el flujo eléctrico en módulos comerciales de relés)
  digitalWrite(rele3, HIGH);
  digitalWrite(rele4, HIGH);
  digitalWrite(rele5, HIGH);
  digitalWrite(rele6, HIGH);
  digitalWrite(rele7, HIGH);
  digitalWrite(rele8, HIGH);
}

void loop() {
  // 1. Escuchar comandos desde la Raspberry Pi (o PC por Serial USB)
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    int separadorIndex = comando.indexOf(':');
    if (separadorIndex != -1) {
      String idStr = comando.substring(0, separadorIndex);
      String estadoStr = comando.substring(separadorIndex + 1);

      int estado = estadoStr.toInt(); // '1' para ENCENDER (LOW), '0' para APAGAR (HIGH)
      int valorPin = (estado == 1) ? LOW : HIGH;

      if (idStr == "R3") {
        digitalWrite(rele3, valorPin);
      } else if (idStr == "R4") {
        digitalWrite(rele4, valorPin);
      } else if (idStr == "R5") {
        digitalWrite(rele5, valorPin);
      } else if (idStr == "R6") {
        digitalWrite(rele6, valorPin);
      } else if (idStr == "R7") {
        digitalWrite(rele7, valorPin);
      } else if (idStr == "R8") {
        digitalWrite(rele8, valorPin);
      } else if (idStr == "M") {
        // Comando Master: Afecta a todos los relés configurados
        digitalWrite(rele3, valorPin);
        digitalWrite(rele4, valorPin);
        digitalWrite(rele5, valorPin);
        digitalWrite(rele6, valorPin);
        digitalWrite(rele7, valorPin);
        digitalWrite(rele8, valorPin);
      }
    }
  }

  // 2. Medir consumo y enviar telemetría en formato ID:WATTS
  unsigned long tiempoActual = millis();
  if (tiempoActual - tiempoAnterior >= intervaloEnvio) {
    tiempoAnterior = tiempoActual;

    float watts3 = calcularWatts(sensor3);
    float watts4 = calcularWatts(sensor4);
    float watts5 = calcularWatts(sensor5);
    float watts6 = calcularWatts(sensor6);
    float watts7 = calcularWatts(sensor7);
    float watts8 = calcularWatts(sensor8);

    // Enviar datos por serial
    Serial.print("3:"); Serial.println(watts3);
    Serial.print("4:"); Serial.println(watts4);
    Serial.print("5:"); Serial.println(watts5);
    Serial.print("6:"); Serial.println(watts6);
    Serial.print("7:"); Serial.println(watts7);
    Serial.print("8:"); Serial.println(watts8);
  }
}

// Función básica para obtener el consumo RMS de un ACS712
float calcularWatts(int pinSensor) {
  int valorMinimo = 1024;
  int valorMaximo = 0;
  
  unsigned long inicioMuestreo = millis();
  // Muestrear por 50ms para capturar al menos 3 ciclos completos a 60Hz
  while (millis() - inicioMuestreo < 50) {
    int valorLeido = analogRead(pinSensor);
    if (valorLeido < valorMinimo) valorMinimo = valorLeido;
    if (valorLeido > valorMaximo) valorMaximo = valorLeido;
  }
  
  // Convertir a voltaje pico a pico (0 a 5V en ADC de 10 bits)
  float voltajePicoPico = ((valorMaximo - valorMinimo) * 5.0) / 1024.0;
  
  // Voltaje RMS = (Vpp / 2) * 0.707
  float voltajeRMS = (voltajePicoPico / 2.0) * 0.707;
  
  // Corriente RMS = Vrms / Sensibilidad
  float corrienteRMS = voltajeRMS / SENSIBILIDAD_ACS712;
  
  // Filtro de ruido básico: si es menor a 150mA consideramos que no hay carga
  if (corrienteRMS < 0.15) corrienteRMS = 0.0;
  
  // Potencia activa en Watts = I_rms * V_red
  float watts = corrienteRMS * VOLTAJE_RED;
  
  return watts;
}
