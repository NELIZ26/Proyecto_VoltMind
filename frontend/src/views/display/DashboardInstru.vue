<script setup>
import DarkModeToggle from '@/components/DarkModeToggle.vue';
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

// IMPORTACIÓN DE COMPONENTES MODULARES
import PinModal from "@/components/PinModal.vue";
import QrModal from "@/components/QrModal.vue";
import FirmaModal from "@/components/FirmaModal.vue";
import ProfileModal from "@/components/profileModal.vue";
import AttendanceModal from "@/components/attendanceModal.vue";
import ExitModal from "@/components/exitModal.vue";
import AlertPanel from "@/components/AlertPanel.vue";
import { useRole } from "@/composables/useRole";

// IMPORTACIÓN DE GRÁFICOS
import SpeedometerChart from "@/components/charts/SpeedometerChart.vue";
import DynamicMeterBar from "@/components/charts/DynamicMeterBar.vue";
import ThermometerChart from "@/components/ThermometerChart.vue";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const toast = useToast();
const router = useRouter();
const { hasRole, hasPermission } = useRole();

// --- ESTADOS REACTIVOS PRINCIPALES ---
const isPowerOn = ref(localStorage.getItem('isPowerOn') === 'true');
const salidaHabilitada = ref(localStorage.getItem('salidaHabilitada') === 'true'); 
const nfcScanning = ref(false);
const qrProjected = ref(false);
const showPinModal = ref(false);
const isValidatingPin = ref(false);
const currentTime = ref(new Date().toLocaleTimeString());
const isTogglingPower = ref(false);
const isFinishingClass = ref(false);

// --- ESTADOS DE LA SESIÓN ---
const ambienteSeleccionadoId = ref(localStorage.getItem('ambienteActivoId') || localStorage.getItem('kiosko_ambiente_id') || "");
const nombreAmbienteSeleccionado = ref(localStorage.getItem('ambienteActivoNombre') || localStorage.getItem('kiosko_ambiente_nombre') || "Ambiente no definido");
const fichaActiva = ref(localStorage.getItem('fichaActiva') || "Sin Ficha");
const nombreInstructor = ref(localStorage.getItem('nombreInstructor') || "Instructor");
const nombrePrograma = ref(localStorage.getItem('nombrePrograma') || "Programa no definido");

const apprentices = ref([]); 
const isLoading = ref(true);

// --- CONTROLADORES PARA FIRMA ---
const showFirmaModal = ref(false);
const aprendizSeleccionadoParaFirmar = ref({ name: "", doc: "" });

// --- RELOJES Y TIEMPOS ---
const horaInicio = ref(localStorage.getItem('horaInicio') || '--:--');
const horaFin = ref(localStorage.getItem('horaFin') || '--:--');
const tiempoExtra = ref(localStorage.getItem('tiempoExtra') || '0 min');

// --- ALERTAS, MODALES Y NODOS IOT ---
const systemAlerts = ref([
  {
    id: 1,
    severity: "warning",
    message: "Alerta de Deserción: Validación Dataverse pendiente.",
    source: "Asistencia",
    timestamp: "Hoy",
  },
]);
const activeModal = ref(null);
const selectedApprentice = ref(null);

const thermometers = ref([
  { id: 1, value: 24.5 },
  { id: 2, value: 25.0 }
]);

const getTempHeight = (val) => {
  const min = 15;
  const max = 35;
  let pct = ((val - min) / (max - min)) * 100;
  if (pct < 10) pct = 10;
  if (pct > 100) pct = 100;
  return pct + "%";
};

const getTempColor = (val) => {
  if (val < 20) return "#3b82f6"; // Azul frío
  if (val > 26) return "#ef4444"; // Rojo calor
  return "#22c55e"; // Verde ok
};

watch(() => thermometers.value, (newVals) => {
  const isHot = newVals.some(t => t.value > 26);
  const isCold = newVals.some(t => t.value < 20);

  // Filtrar alertas existentes de temperatura
  systemAlerts.value = systemAlerts.value.filter(a => a.source !== "Sensores de Temperatura");

  if (isHot) {
    systemAlerts.value.push({
      id: Date.now(),
      severity: "error", // Aparecerá roja
      message: "Temperatura alta. Sugerencia: Encender / Ajustar AC.",
      source: "Sensores de Temperatura",
      timestamp: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
    });
  } else if (isCold) {
    systemAlerts.value.push({
      id: Date.now(),
      severity: "info", // Aparecerá azul o neutral
      message: "Temperatura muy baja. Sugerencia: Regular / Apagar AC.",
      source: "Sensores de Temperatura",
      timestamp: new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
    });
  }
}, { deep: true });

const meters = ref([
  { id: 1, label: "Iluminación Aula", value: 120 },
  { id: 2, label: "Bancos de Cómputo", value: 850 },
  { id: 3, label: "Rack Comunicaciones", value: 450 },
  { id: 4, label: "Aires Acondicionados", value: 1200 },
]);

// Nodos de Bancos de Cómputo (Reducidos a 8)
const roomNodes = ref(
  Array.from({ length: 8 }, (_, i) => ({
    id: i + 1,
    energized: isPowerOn.value,
    load: Math.floor(Math.random() * 90) + 10,
    maxLoad: Math.floor(Math.random() * 20) + 100, // Simulación de pico máximo
  }))
);

// Estados para Iluminación
const lightStates = ref(
  Array.from({ length: 4 }, (_, i) => ({
    id: i + 1,
    label: `Zona ${i + 1}`,
    energized: isPowerOn.value
  }))
);

// Estado y telemetría para Rack
const rackPowerState = ref(false);
const rackMinLoad = ref(150);
const rackMaxLoad = ref(400);

const acPowerState = ref(false);
const acMinLoad = ref(800);
const acMaxLoad = ref(1500);

// 🟢 FUNCIÓN DE RECUPERACIÓN: Sincroniza la vista con la base de datos en memoria (Redis)
const recuperarEstadoClase = async (sesionId) => {
  console.log("🔍 Intentando recuperar clase para sesión:", sesionId);
  try {
    // Asegúrate de usar la variable BASE_URL que ya tienes definida en tu archivo
    const url = `${BASE_URL}/api/asistencia/sesion/${sesionId}/ingresos`;
    
    const response = await fetch(url);
    
    if (response.ok) {
      const data = await response.json();
      const documentosPresentes = data.ingresos;
      console.log("📦 Documentos recuperados de Redis:", documentosPresentes);

      if (documentosPresentes.length > 0) {
        documentosPresentes.forEach(doc => {
          // Comparamos el documento de Redis con la lista visual de Dataverse
          const aprendiz = apprentices.value.find(ap => String(ap.doc) === String(doc));
          
          if (aprendiz) {
            aprendiz.status = "present"; // Lo pintamos de verde
            if (!aprendiz.lastSeen || aprendiz.lastSeen === "--:--") {
              aprendiz.lastSeen = "Sincronizado";
            }
          }
        });
      }
    } else {
      console.error("❌ El backend rechazó la petición de recuperación.");
    }
  } catch (error) {
    console.error("❌ ERROR al intentar recuperar el estado desde Redis:", error);
  }
};

// ==========================================
// 📡 CEREBRO WEBSOCKET (DOBLE VÍA CON KIOSKO)
// ==========================================
let wsDashboard = null;

const conectarWebSocketDashboard = () => {
  if (!ambienteSeleccionadoId.value || ambienteSeleccionadoId.value === "Sin Definir") return;

  const WS_URL = BASE_URL.replace(/^http/, 'ws');
  wsDashboard = new WebSocket(`${WS_URL}/api/ws/ambiente/${ambienteSeleccionadoId.value}`);

  wsDashboard.onopen = () => {
    console.log(`[Dashboard] 🟢 Escuchando al ambiente ${nombreAmbienteSeleccionado.value}`);
  };

  wsDashboard.onmessage = (event) => {
    const mensaje = JSON.parse(event.data);
    
    // 1. El Kiosko encendió el aula
    if (mensaje.tipo === "SESION_INICIADA") {
      if (!isPowerOn.value) { 
        toast.success("Aula energizada remotamente desde la Terminal Kiosko.");
        isPowerOn.value = true;
        
        // Encendemos los nodos visualmente
        roomNodes.value.forEach((node) => { node.energized = true; });

        // Sincronizamos la memoria local
        localStorage.setItem('sesionActivaId', mensaje.sesion_id);
        localStorage.setItem('isPowerOn', 'true');
        
        const fechaEntrada = mensaje.hora ? new Date(mensaje.hora) : new Date();
        horaInicio.value = fechaEntrada.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        localStorage.setItem('horaInicio', horaInicio.value);

        // Cargamos la lista operativa
        recargarListadoAprendices();

        // 🔌 Iniciar sondeo de telemetría de hardware
        startTelemetryPolling();
      }
    } 
    // 2. Un aprendiz ingresó su PIN en el Kiosko
    else if (mensaje.tipo === "APRENDIZ_INGRESO") {
      const aprendiz = apprentices.value.find(ap => String(ap.doc) === String(mensaje.documento));
      if (aprendiz) {
        aprendiz.status = "present";
        aprendiz.lastSeen = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        toast.info(`Ingreso desde Kiosko: ${mensaje.nombre}`);
      }
    }
    // 🟢 NUEVA REGLA 3: Capturar cuando el aprendiz completa su firma táctil
    else if (mensaje.tipo === "APRENDIZ_FIRMA") {
      const aprendiz = apprentices.value.find(ap => String(ap.doc) === String(mensaje.documento));
      if (aprendiz) {
        // Actualizamos el estado visual exactamente como lo haría el proceso local
        aprendiz.lastSeen = "Firma Completada";
        toast.success(`Firma registrada para: ${aprendiz.name}`);
      }
    }
  };

  wsDashboard.onclose = () => {
    console.warn("[Dashboard] 🔴 Conexión perdida. Reconectando...");
    setTimeout(conectarWebSocketDashboard, 3000);
  };
};

// ==========================================
// 🔄 FUNCIONES DE CARGA Y SINCRONIZACIÓN
// ==========================================
const recargarListadoAprendices = async () => {
  if (fichaActiva.value === "Sin Ficha") return;
  isLoading.value = true;
  try {
    const response = await fetch(`${BASE_URL}/api/fichas/${fichaActiva.value}/aprendices`);
    if (!response.ok) throw new Error("No se encontraron aprendices.");

    const data = await response.json();
    apprentices.value = data.map((ap) => ({
      id: ap.documento,
      name: ap.nombre || 'Sin Nombre',
      doc: ap.documento,
      email: ap.correo,
      status: "absent", 
      lastSeen: "Esperando ingreso"
    }));

    // 🟢 LA SOLUCIÓN DEFINITIVA: Sincronización automática
    // Apenas termine de armar la lista visual, busca si hay una sesión activa
    // y recupera a los que ya habían entrado (incluso si se inició desde la tablet).
    
    console.log("✅ Lista de Dataverse cargada. Total alumnos:", apprentices.value.length);
    
    const sesionActivaId = localStorage.getItem('sesionActivaId');
    if (sesionActivaId && apprentices.value.length > 0) {
      await recuperarEstadoClase(sesionActivaId);
    } else {
      console.log("⚠️ No se ejecutó la recuperación porque falta el ID de sesión o la lista está vacía.");
    }

  } catch (error) {
    console.error("Error consultando aprendices:", error);
    toast.warning("El aula está lista, pero no hay aprendices registrados.");
  } finally {
    isLoading.value = false;
  }
};

// ==========================================
// 📡 TELEPATÍA DEL QR (Mantiene soporte local)
// ==========================================
let qrListenerInterval = null;
let telemetryInterval = null;

watch(qrProjected, (newVal) => {
  if (newVal) {
    qrListenerInterval = setInterval(async () => {
      const sesionId = localStorage.getItem('sesionActivaId');
      if (!sesionId) return;

      try {
        const res = await fetch(`${BASE_URL}/api/asistencia/ultimo-escaneo/${sesionId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.documento) {
            const aprendiz = apprentices.value.find(a => a.doc === data.documento);
            if (aprendiz) {
              qrProjected.value = false;

              if (data.accion === "ingreso_exitoso") {
                aprendiz.status = "present";
                aprendiz.lastSeen = "En Clase";
                toast.success(`¡${aprendiz.name} ha registrado su ingreso!`);
              } 
              else if (data.accion === "requiere_firma") {
                aprendizSeleccionadoParaFirmar.value = { name: aprendiz.name, doc: aprendiz.doc };
                showFirmaModal.value = true;
              }
            }
          }
        }
      } catch (error) {}
    }, 1500); 
  } else {
    if (qrListenerInterval) clearInterval(qrListenerInterval);
  }
});

// ==========================================
// 🚀 LÓGICA DE ASISTENCIA Y FIRMAS
// ==========================================
const procesarValidacionPin = async (pinIngresado) => {
  isValidatingPin.value = true;
  try {
    const sesionId = localStorage.getItem('sesionActivaId') || "";
    const response = await fetch(`${BASE_URL}/api/asistencia/validar-pin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        pin: pinIngresado,
        sesion_id: sesionId
      })
    });

    if (response.ok) {
      const data = await response.json();
      const aprendizEncontrado = apprentices.value.find(a => a.doc === data.documento_aprendiz);
      
      if (!aprendizEncontrado) {
        toast.warning("PIN válido, pero el aprendiz no pertenece a esta ficha operativa.");
        return;
      }

      if (data.accion === "ingreso_exitoso") {
        aprendizEncontrado.status = "present";
        aprendizEncontrado.lastSeen = "En Clase"; 
        toast.success(data.mensaje);
        showPinModal.value = false;
      } 
      else if (data.accion === "requiere_firma") {
        aprendizSeleccionadoParaFirmar.value = {
          name: aprendizEncontrado.name,
          doc: aprendizEncontrado.doc
        };
        showPinModal.value = false;
        showFirmaModal.value = true; 
      }
    } else {
      const errorData = await response.json();
      toast.error(errorData.detail || "El código introducido es incorrecto o ya caducó.");
    }
  } catch (error) {
    console.error("Error validando PIN:", error);
    toast.error("Error de conexión con el servidor.");
  } finally {
    isValidatingPin.value = false;
  }
};

const habilitarSalidaClase = async () => {
  const sesionId = localStorage.getItem('sesionActivaId');
  if (!sesionId) {
    toast.error("No hay una sesión activa para finalizar.");
    return;
  }

  isFinishingClass.value = true;
  try {
    const res = await fetch(`${BASE_URL}/api/asistencia/habilitar-salida/${sesionId}`, { method: "POST" });
    if (res.ok) {
      salidaHabilitada.value = true;
      localStorage.setItem('salidaHabilitada', 'true'); 
      qrProjected.value = false;
      
      const currentTimeStr = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
      horaFin.value = currentTimeStr;
      localStorage.setItem('horaFin', currentTimeStr);

      toast.success("¡Clase finalizada! Ya puedes registrar las firmas de los presentes.");
    }
  } catch (error) {
    toast.error("Error al conectar con el servidor para habilitar salidas.");
  } finally {
    isFinishingClass.value = false;
  }
};

const procesarRegistroFirmaAsistencia = async (base64Signature) => {
  const sesionId = localStorage.getItem('sesionActivaId') || "";
  try {
    const response = await fetch(`${BASE_URL}/api/asistencia/guardar-firma`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sesion_id: sesionId,
        documento_aprendiz: aprendizSeleccionadoParaFirmar.value.doc,
        nombre_aprendiz: aprendizSeleccionadoParaFirmar.value.name,
        firma_base64: base64Signature
      })
    });

    if (response.ok) {
      toast.success(`¡Firma de salida registrada para ${aprendizSeleccionadoParaFirmar.value.name}!`);
      const aprendiz = apprentices.value.find(a => a.doc === aprendizSeleccionadoParaFirmar.value.doc);
      if(aprendiz) aprendiz.lastSeen = "Firma Completada";
      showFirmaModal.value = false;
    } else {
      toast.error("Falló el guardado del registro en el servidor.");
    }
  } catch (error) {
    toast.error("Error de red al procesar la firma táctil.");
  }
};

const enviarReporteSemanalManual = async () => {
  toast.info("Procesando matriz de asistencia. Por favor, espera...");
  try {
    const correo = localStorage.getItem('instructorEmail') || "correo@sena.edu.co";
    const sesionId = localStorage.getItem('sesionActivaId') || ""; 
    const textoHorario = `${horaInicio.value} a ${horaFin.value !== '--:--' ? horaFin.value : 'En curso'}`;
    
    const urlParams = new URLSearchParams({
      numero_ficha: fichaActiva.value,
      nombre_programa: nombrePrograma.value,
      nombre_instructor: nombreInstructor.value,
      correo_destino: correo,
      nombre_ambiente: nombreAmbienteSeleccionado.value,
      horario: textoHorario
    });

    if (sesionId) urlParams.append("sesion_activa", sesionId);

    const response = await fetch(`${BASE_URL}/api/asistencia/matriz-semanal?${urlParams.toString()}`, { 
      method: "POST" 
    });

    if (response.ok) {
      toast.success(`¡Reporte solicitado! Llegará a ${correo} en unos instantes.`);
    } else {
      toast.warning("Fallo la estructura del envío en el servidor.");
    }
  } catch (error) {
    toast.error("Fallo de red al solicitar el reporte.");
  }
};

// ==========================================
// 🔌 OPERACIONES IOT (AULA)
// ==========================================
const toggleMasterPower = async () => {
  console.log("⚡ Clicked toggleMasterPower. Current isPowerOn:", isPowerOn.value);
  if (!isPowerOn.value && (!ambienteSeleccionadoId.value || ambienteSeleccionadoId.value === "Sin Definir")) {
    toast.warning("¡Alerta! No se detectó un ambiente enlazado.");
    router.push("/route-selector"); 
    return; 
  }

  isTogglingPower.value = true;
  isPowerOn.value = !isPowerOn.value;
  roomNodes.value.forEach((node) => { node.energized = isPowerOn.value; });
  lightStates.value.forEach((light) => { light.energized = isPowerOn.value; });
  rackPowerState.value = isPowerOn.value;
  acPowerState.value = isPowerOn.value;

  if (isPowerOn.value) {
    salidaHabilitada.value = false;
    toast.info("Energizando aula...");
    startTelemetryPolling();
    
    try {
      const emailInstructor = localStorage.getItem('instructorEmail') || "";
      
      if (fichaActiva.value !== "Sin Ficha") {
        const responseSesion = await fetch(`${BASE_URL}/api/sesiones/iniciar`, { 
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ficha: fichaActiva.value,
            email: emailInstructor,
            ambiente_id: ambienteSeleccionadoId.value
          })
        });

        if (responseSesion.ok) {
          const data = await responseSesion.json();
          localStorage.setItem('sesionActivaId', data.sesion_id);
          const fechaEntrada = new Date(data.hora_entrada);
          horaInicio.value = fechaEntrada.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
          
          localStorage.setItem('isPowerOn', 'true');
          localStorage.setItem('salidaHabilitada', 'false');
          localStorage.setItem('horaInicio', horaInicio.value);
          localStorage.removeItem('horaFin');
          localStorage.removeItem('tiempoExtra');
          horaFin.value = '--:--';
          tiempoExtra.value = '0 min';

          toast.success("¡Aula ENERGIZADA y sesión registrada!");
        } else {
          toast.warning("Iniciado en Modo Local (Falla al registrar sesión).");
          localStorage.setItem('isPowerOn', 'true');
        }
      } else {
        toast.info("Iniciado en Modo Local (Sin ficha activa).");
        localStorage.setItem('isPowerOn', 'true');
      }
    } catch (error) {
      toast.warning("Iniciado en Modo Local (Sin conexión a Dataverse).");
      localStorage.setItem('isPowerOn', 'true');
    }

    // 🔌 ENVIAR COMANDO MAESTRO AL ARDUINO (ENCENDER)
    await fetch(`${BASE_URL}/api/iot/master`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: 1 })
    }).catch(err => console.warn("Error al encender hardware por serial:", err));
  
  } else {
    toast.info("Apagando aula...");
    stopTelemetryPolling();
    try {
      const sesionId = localStorage.getItem('sesionActivaId') || "";
      if (sesionId && fichaActiva.value !== "Sin Ficha") {
        const correo = localStorage.getItem('instructorEmail') || "correo@sena.edu.co";
        
        const payloadCierre = {
          sesion_id: sesionId,
          numero_ficha: fichaActiva.value,
          nombre_programa: nombrePrograma.value,
          nombre_instructor: nombreInstructor.value,
          correo_destino: correo
        };
        
        await fetch(`${BASE_URL}/api/asistencia/cerrar-asistencia`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadCierre)
        });

        await fetch(`${BASE_URL}/api/sesiones/finalizar?sesion_id=${sesionId}`, { method: "POST" });
      }
    } catch (error) {
      console.warn("No se pudo registrar el cierre en la base de datos:", error);
    }

    localStorage.setItem('isPowerOn', 'false');
    localStorage.setItem('salidaHabilitada', 'false');
    localStorage.removeItem('sesionActivaId'); 

    salidaHabilitada.value = false;
    isPowerOn.value = false;
    roomNodes.value.forEach((node) => { node.energized = false; });
    lightStates.value.forEach((light) => { light.energized = false; });
    rackPowerState.value = false;

    // 🔌 ENVIAR COMANDO MAESTRO AL ARDUINO (APAGAR)
    await fetch(`${BASE_URL}/api/iot/master`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: 0 })
    }).catch(err => console.warn("Error al apagar hardware por serial:", err));

    toast.success("¡Aula APAGADA correctamente!");
  }
  isTogglingPower.value = false;
};

const toggleNodePower = async (node) => {
  console.log("⚡ Clicked toggleNodePower. Node:", node);
  const nextState = !node.energized;
  // B1 (id 1) -> Relé 3. B2 (id 2) -> Relé 4.
  if (node.id === 1 || node.id === 2) {
    const relayId = node.id === 1 ? "R3" : "R4";
    const targetUrl = `${BASE_URL}/api/iot/relay`;
    console.log(`🌐 Fetching: ${targetUrl} with payload:`, { relay_id: relayId, status: nextState ? 1 : 0 });
    try {
      const res = await fetch(targetUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ relay_id: relayId, status: nextState ? 1 : 0 })
      });
      console.log(`📡 Response status: ${res.status}`);
      if (res.ok) {
        const data = await res.json();
        console.log("🟢 Response data:", data);
        node.energized = nextState;
        toast.success(`Banco ${node.id} (Puesto P${node.id}) ${nextState ? 'encendido' : 'apagado'} físicamente.`);
      } else {
        const errorText = await res.text();
        console.error("🔴 Response error text:", errorText);
        toast.error("Error al conmutar el relé en el hardware.");
      }
    } catch (e) {
      console.error("❌ Network or Fetch error:", e);
      toast.error("Error de conexión con el controlador IoT.");
    }
  } else {
    // Modo Simulado para los bancos restantes
    node.energized = nextState;
  }
};

const toggleLightPower = async (light) => {
  console.log("⚡ Clicked toggleLightPower. Light:", light);
  const nextState = !light.energized;
  const relayId = `R${light.id + 4}`;
  const targetUrl = `${BASE_URL}/api/iot/relay`;
  console.log(`🌐 Fetching: ${targetUrl} with payload:`, { relay_id: relayId, status: nextState ? 1 : 0 });
  try {
    const res = await fetch(targetUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ relay_id: relayId, status: nextState ? 1 : 0 })
    });
    console.log(`📡 Response status: ${res.status}`);
    if (res.ok) {
      const data = await res.json();
      console.log("🟢 Response data:", data);
      light.energized = nextState;
      toast.success(`${light.label} ${nextState ? 'encendida' : 'apagada'} físicamente.`);
    } else {
      const errorText = await res.text();
      console.error("🔴 Response error text:", errorText);
      toast.error("Error al conmutar la zona de iluminación.");
    }
  } catch (e) {
    console.error("❌ Network or Fetch error:", e);
    toast.error("Error de conexión con el controlador IoT.");
  }
};

const toggleRackPower = () => {
  rackPowerState.value = !rackPowerState.value;
};

const toggleAcPower = () => {
  acPowerState.value = !acPowerState.value;
};

// 📡 FUNCIONES AUXILIARES PARA MANEJAR EL SONDEO
const startTelemetryPolling = () => {
  if (!telemetryInterval) {
    console.log("🟢 Iniciando sondeo de telemetría...");
    telemetryInterval = setInterval(pollTelemetry, 2000);
    pollTelemetry();
  }
};

const stopTelemetryPolling = () => {
  if (telemetryInterval) {
    console.log("🔴 Deteniendo sondeo de telemetría...");
    clearInterval(telemetryInterval);
    telemetryInterval = null;
  }
};

// Memoria caché para estabilizar las lecturas de los sensores ACS712
const telemetryCache = ref({});

// 📡 FUNCIÓN DE SONDEO (POLLING) DE TELEMETRÍA REAL
const pollTelemetry = async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/iot/telemetry`);
    if (res.ok) {
      const data = await res.json();
      const tel = data.telemetry || {};
      // Estabilizar lecturas: Los sensores ACS712 a veces envían 0W erróneamente en AC.
      // Si el relé está encendido LOCALMENTE, ignoramos las caídas abruptas a 0 y mantenemos el último valor real.
      Object.keys(tel).forEach(key => {
        const val = parseFloat(tel[key] || 0);
        
        // Mapear el sensor a su estado local (frontend)
        let isRelayOnLocally = false;
        if (key === "5") isRelayOnLocally = lightStates.value[0]?.energized;
        else if (key === "6") isRelayOnLocally = lightStates.value[1]?.energized;
        else if (key === "7") isRelayOnLocally = lightStates.value[2]?.energized;
        else if (key === "8") isRelayOnLocally = lightStates.value[3]?.energized;
        else if (key === "3") isRelayOnLocally = roomNodes.value[0]?.energized;
        else if (key === "4") isRelayOnLocally = roomNodes.value[1]?.energized;
        
        if (val > 0) {
          telemetryCache.value[key] = val;
        } else if (val === 0) {
          if (isRelayOnLocally && isPowerOn.value) {
            // El relé está ON localmente, ignoramos este "0" como ruido del sensor y mantenemos el caché
          } else {
            // El relé está OFF, forzamos a 0
            telemetryCache.value[key] = 0;
          }
        }
      });

      const tc = telemetryCache.value;

      // 1. Iluminación Aula (Suma de Relés 5 a 8)
      const w5 = parseFloat(tc["5"] || 0);
      const w6 = parseFloat(tc["6"] || 0);
      const w7 = parseFloat(tc["7"] || 0);
      const w8 = parseFloat(tc["8"] || 0);
      meters.value[0].value = Math.round(w5 + w6 + w7 + w8);

      // 2. Bancos de Cómputo (Suma de Relés 3 y 4)
      const w3 = parseFloat(tc["3"] || 0);
      const w4 = parseFloat(tc["4"] || 0);
      meters.value[1].value = Math.round(w3 + w4);

      // 3. Rack de Comunicaciones (Simulado dinámicamente si está ON)
      if (rackPowerState.value) {
        meters.value[2].value = Math.floor(Math.random() * (rackMaxLoad.value - rackMinLoad.value)) + rackMinLoad.value;
      } else {
        meters.value[2].value = 0;
      }

      // 4. Aires Acondicionados (Simulado dinámicamente si está ON)
      if (acPowerState.value) {
        meters.value[3].value = Math.floor(Math.random() * (acMaxLoad.value - acMinLoad.value)) + acMinLoad.value;
      } else {
        meters.value[3].value = 0;
      }

      // 5. Sincronizar estados si el aula está energizada
      if (isPowerOn.value) {
        if (roomNodes.value[0]) {
          roomNodes.value[0].energized = states["R3"] === 1;
          roomNodes.value[0].load = Math.round(w3);
        }
        if (roomNodes.value[1]) {
          roomNodes.value[1].energized = states["R4"] === 1;
          roomNodes.value[1].load = Math.round(w4);
        }
        lightStates.value.forEach(light => {
          const relayKey = `R${light.id + 4}`;
          if (states[relayKey] !== undefined) {
            light.energized = states[relayKey] === 1;
          }
        });

        // Simulación de temperatura si el aula está encendida
        thermometers.value.forEach(t => {
          t.value = parseFloat((t.value + (Math.random() - 0.5)).toFixed(1));
          if (t.value > 30) t.value = 30;
          if (t.value < 18) t.value = 18;
        });
      }
    }
  } catch (e) {
    console.error("Error consultando telemetría del hardware:", e);
  }
};

// ==========================================
// 🎛️ CONTROLADORES DE BOTONES E INTERFAZ
// ==========================================
const projectQR = () => {
  if (!isPowerOn.value) {
    toast.warning("Debes energizar el aula antes de proyectar el código QR.");
    return;
  }
  qrProjected.value = !qrProjected.value; 
};

const openPinModal = () => {
  if (!isPowerOn.value) {
    toast.warning("Debes energizar el aula antes de usar el ingreso por PIN.");
    return;
  }
  showPinModal.value = true;
};

const toggleNFC = () => {
  if (!isPowerOn.value) {
    toast.warning("Debes energizar el aula para activar el escáner NFC.");
    return;
  }
  nfcScanning.value = !nfcScanning.value;
  toast.info(nfcScanning.value ? "Lector NFC activado." : "Lector NFC desactivado.");
};

const handleAlertResolution = (alertId) => {
  systemAlerts.value = systemAlerts.value.filter((alert) => alert.id !== alertId);
  toast.success("Alerta resuelta exitosamente.");
};

const openModal = (type, apprentice) => {
  selectedApprentice.value = apprentice;
  activeModal.value = type;
};

const closeModal = () => {
  activeModal.value = null;
  selectedApprentice.value = null;
};

const handleExitConfirm = (reason) => {
  if (selectedApprentice.value) {
    selectedApprentice.value.status = "absent";
    selectedApprentice.value.lastSeen = "Salida Inesperada";
    toast.warning(`Salida anticipada registrada: ${reason}`);
  }
  closeModal();
};

const cerrarSesion = () => {
  if (isPowerOn.value) {
    toast.warning("Primero debes apagar el aula y finalizar la sesión de clase actual.");
    return;
  }
  localStorage.clear();
  toast.success("Sesión cerrada correctamente. Volviendo al inicio.");
  router.push("/route-selector"); 
};



// ==========================================
// 🚀 CICLO DE VIDA
// ==========================================
onMounted(async () => {
  // =========================================================================
  // 1. ESCUCHADOR DE EVENTOS: Sincronización si la tablet inicia la clase
  // =========================================================================
  window.addEventListener('storage', async (event) => {
    if (event.key === 'sesionActivaId' && event.newValue) {
      console.log("⚡ Sesión detectada desde la tablet. Activando energía en el Dashboard...");
      
      // Encendido visual y persistencia
      isPowerOn.value = true;
      localStorage.setItem('isPowerOn', 'true');
      rackPowerState.value = true;
      acPowerState.value = true;
      
      // Sincronización de variables de tiempo y salida
      horaInicio.value = localStorage.getItem('horaInicio') || '--:--';
      salidaHabilitada.value = false;
      localStorage.setItem('salidaHabilitada', 'false');
      
      // Energización de los nodos (Control por estación)
      if (roomNodes.value) {
        roomNodes.value.forEach((node) => { node.energized = true; });
      }
      
      // Re-enlace de identificadores físicos
      ambienteSeleccionadoId.value = localStorage.getItem('kiosko_ambiente_id') || localStorage.getItem('ambienteActivoId');
      nombreAmbienteSeleccionado.value = localStorage.getItem('kiosko_ambiente_nombre') || localStorage.getItem('ambienteActivoNombre');
      
      // Levantar WebSocket
      conectarWebSocketDashboard();
      
      // 🚀 Descarga de alumnos y recuperación automática de estados
      await recargarListadoAprendices();

      // 🔌 Iniciar sondeo de telemetría de hardware
      startTelemetryPolling();
    }
  });

  // =========================================================================
  // 2. SEGURIDAD: Validación de Rol
  // =========================================================================
  if (!hasRole(["instructor", "dinamizador"])) {
    toast.error("Acceso denegado. Se requiere perfil de Instructor.");
    router.push("/route-selector");
    return;
  }

  // =========================================================================
  // 3. RELOJ MAESTRO
  // =========================================================================
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString();
  }, 1000);

  // =========================================================================
  // 4. FLUJO DE CARGA INICIAL
  // =========================================================================
  
  // Iniciamos el canal bidireccional si hay un ambiente guardado
  conectarWebSocketDashboard();

  // CASO A: Recarga accidental de página (F5) con la clase ya iniciada
  if (isPowerOn.value) {
    // Iniciamos el sondeo de telemetría de hardware
    startTelemetryPolling();
    // Esta única línea descarga la lista y pinta los verdes automáticamente
    await recargarListadoAprendices();
    return;
  }

  // CASO B: Modo Standby (No hay sesión ni ficha asignada aún)
  if (fichaActiva.value === "Sin Ficha") {
    console.log("Dashboard en Modo Standby: Esperando que el Kiosko inicie el flujo.");
    isLoading.value = false;
    return; 
  }

  // CASO C: Arranque normal desde la PC (El instructor configura todo desde el Dashboard)
  await recargarListadoAprendices();
});

onUnmounted(() => {
  if (qrListenerInterval) clearInterval(qrListenerInterval);
  if (telemetryInterval) clearInterval(telemetryInterval);
  if (wsDashboard) wsDashboard.close();
});
</script>

<template>
  <div class="dashboard-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="logo-duo">
          <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
          <div class="logo-divider" />
          <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="logo-volt" />
        </div>
        <div class="environment-badge">
          <h1> <span style="font-size: 0.6em; color: #666; display: block; text-transform: uppercase;">
            Ambiente de Formación </span>{{ nombreAmbienteSeleccionado.toUpperCase() }}</h1>
          <p class="header-meta">
            Ficha: {{ fichaActiva }} - {{ nombrePrograma }} | Instructor: {{ nombreInstructor }} |
            <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>

      <div class="power-master-box" v-if="hasPermission('gestionar_aula')">
        <button class="power-switch" :class="{ 'power-active': isPowerOn, 'loading': isTogglingPower }" @click="toggleMasterPower" :disabled="isTogglingPower">
          <font-awesome-icon :icon="isTogglingPower ? 'fa-solid fa-spinner' : 'fa-solid fa-power-off'" :class="{ 'fa-spin': isTogglingPower }" />
        </button>

        <button class="btn-logout-instructor" @click="cerrarSesion" title="Cerrar Sesión" style="margin-left: 15px; background-color: #e74c3c; color: white; border: none; padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
          <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
        </button>
      </div>
    </header>

    <div class="time-cards-container">
      <div class="time-card start-card">
        <div class="icon-box">
          <font-awesome-icon icon="fa-solid fa-clock" />
        </div>
        <div class="info-box">
          <p class="card-title">Hora de Inicio</p>
          <p class="card-value">{{ horaInicio }}</p>
        </div>
      </div>

      <div class="time-card end-card">
        <div class="icon-box">
          <font-awesome-icon icon="fa-solid fa-trash" />
        </div>
        <div class="info-box">
          <p class="card-title">Hora de Cierre</p>
          <p class="card-value">{{ horaFin }}</p>
        </div>
      </div>

      <div class="time-card extra-card">
        <div class="icon-box">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
        </div>
        <div class="info-box">
          <p class="card-title">Tiempo Extra</p>
          <p class="card-value">{{ tiempoExtra }}</p>
        </div>
      </div>
    </div>

    <main class="dash-grid">
      <section class="dash-col energy-section">
        <div class="module-card">
          <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-microchip" /> TELEMETRÍA DE CONSUMO</h2>
          <div class="meters-grid">
            <template v-for="m in meters" :key="m.id">
              <!-- Velocímetros para Iluminación (1) y Bancos de Cómputo (2) -->
              <div v-if="m.id === 1 || m.id === 2" class="speedometer-wrapper">
                <SpeedometerChart
                  :title="m.label"
                  :currentValue="isPowerOn ? m.value : 0"
                  :maxValue="m.id === 1 ? 250 : 2000"
                  unit="W"
                />
              </div>
              
              <!-- Barra dinámica para Rack y Aires Acondicionados (3 y 4) -->
              <DynamicMeterBar
                v-else-if="m.id === 3 || m.id === 4"
                :label="m.label"
                :value="m.value"
                :maxValue="m.id === 3 ? 1000 : 3000"
                unit="W"
                :isActive="isPowerOn"
              >
                <!-- Controles para el Rack -->
                <div class="rack-panel-integrated" v-if="m.id === 3">
                  <button class="rack-btn-integrated" :class="{ 'rack-on': rackPowerState }" @click="hasPermission('gestionar_aula') ? toggleRackPower() : null" :disabled="!hasPermission('gestionar_aula')">
                    <span>{{ rackPowerState ? 'ON' : 'OFF' }}</span>
                  </button>
                  <div class="rack-stats-integrated">
                    <div class="stat-box-integrated max-stat">
                      <small>MÁX</small>
                      <span>{{ rackPowerState ? rackMaxLoad : 0 }}W</span>
                    </div>
                    <div class="stat-box-integrated min-stat">
                      <small>MÍN</small>
                      <span>{{ rackPowerState ? rackMinLoad : 0 }}W</span>
                    </div>
                  </div>
                </div>

                <!-- Controles para Aires Acondicionados -->
                <div class="rack-panel-integrated" v-if="m.id === 4">
                  <button class="rack-btn-integrated" :class="{ 'rack-on': acPowerState }" @click="hasPermission('gestionar_aula') ? toggleAcPower() : null" :disabled="!hasPermission('gestionar_aula')">
                    <span>{{ acPowerState ? 'ON' : 'OFF' }}</span>
                  </button>
                  <div class="rack-stats-integrated">
                    <div class="stat-box-integrated max-stat" style="color: #3498db; background: rgba(52, 152, 219, 0.1);">
                      <small>MÁX</small>
                      <span>{{ acPowerState ? acMaxLoad : 0 }}W</span>
                    </div>
                    <div class="stat-box-integrated min-stat" style="color: #2980b9; background: rgba(41, 128, 185, 0.1);">
                      <small>MÍN</small>
                      <span>{{ acPowerState ? acMinLoad : 0 }}W</span>
                    </div>
                  </div>
                </div>
              </DynamicMeterBar>
            </template>
          </div>
        </div>

        <div class="module-card map-card">
          <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-plug" /> CONTROL DE ENERGÍA POR ESTACIÓN</h2>
          <p class="map-instruction">Haz clic sobre un control para conmutar su flujo eléctrico.</p>
          
          <div class="energy-control-layout">
            <!-- Fila Superior: Bancos y Luces -->
            <div class="energy-top-row">
              <div class="room-map-wrapper">
                <h3 class="section-subtitle">Bancos de Cómputo</h3>
                <div class="room-map">
                  <button v-for="node in roomNodes" :key="node.id" class="map-node" :class="{ 'node-on': node.energized }" @click="hasPermission('gestionar_aula') ? toggleNodePower(node) : null" :disabled="!hasPermission('gestionar_aula')">
                    <small>B{{ node.id }}</small>
                    <font-awesome-icon icon="fa-solid fa-bolt" class="node-bolt" />
                    <!-- Visualiza el máximo histórico (o el actual si es mayor) -->
                    <span class="node-watts">{{ node.energized ? Math.max(node.load, node.maxLoad) + "W" : "OFF" }}</span>
                  </button>
                </div>
              </div>

              <div class="lights-wrapper">
                <h3 class="section-subtitle">Iluminación</h3>
                <div class="lights-grid">
                  <button v-for="light in lightStates" :key="light.id" class="light-btn" :class="{ 'light-on': light.energized }" @click="hasPermission('gestionar_aula') ? toggleLightPower(light) : null" :disabled="!hasPermission('gestionar_aula')">
                    <font-awesome-icon icon="fa-solid fa-lightbulb" class="light-icon" />
                    <span>{{ light.label }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-col attendance-section">
        <div class="actions-group" v-if="hasPermission('gestionar_aula')">
          <button class="btn-action nfc" :class="{ 'btn-active': nfcScanning }" @click="toggleNFC">
            <font-awesome-icon icon="fa-solid fa-wifi" />
            <span>{{ nfcScanning ? "ESCANEANDO" : "ACTIVAR NFC" }}</span>
          </button>

          <button class="btn-action qr" :class="{ 'btn-active': qrProjected }" @click="projectQR">
            <font-awesome-icon icon="fa-solid fa-qrcode" />
            <span>MOSTRAR QR</span>
          </button>

          <button class="btn-action pin" @click="openPinModal">
            <font-awesome-icon icon="fa-solid fa-lock" />
            <span>DIGITAR PIN</span>
          </button>

          <button v-if="isPowerOn" class="btn-action" :class="{ 'btn-active': salidaHabilitada }" style="background-color: #f39c12; color: white;" @click="habilitarSalidaClase" :disabled="salidaHabilitada || isFinishingClass">
            <font-awesome-icon :icon="isFinishingClass ? 'fa-solid fa-spinner' : 'fa-solid fa-flag-checkered'" :class="{ 'fa-spin': isFinishingClass }" />
            <span>{{ isFinishingClass ? "PROCESANDO..." : (salidaHabilitada ? "SALIDAS ACTIVAS" : "FINALIZAR CLASE") }}</span>
          </button>

          <button class="btn-action" style="background-color: #34495e; color: white;" @click="enviarReporteSemanalManual">
            <font-awesome-icon icon="fa-solid fa-file-excel" />
            <span>ENVIAR REPORTE</span>
          </button>
        </div>

        <AlertPanel title="ALERTAS DEL AMBIENTE" icon="fa-solid fa-triangle-exclamation" :alerts="systemAlerts" @resolve="handleAlertResolution" />

        <!-- GRÁFICAS DE TEMPERATURA USANDO CHART.JS -->
        <div class="module-card">
          <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-temperature-half" /> CLIMATIZACIÓN (TEMP)</h2>
          <div class="temp-charts-grid">
            <div class="chart-box" v-for="t in thermometers" :key="t.id">
              <ThermometerChart :currentValue="t.value" :label="'ZONA ' + t.id" />
            </div>
          </div>
        </div>
      </section>

      <section class="dash-footer-table" v-if="hasRole(['instructor', 'dinamizador'])">
        <div class="module-card table-card">
          <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-users" /> LISTADO OPERATIVO DE APRENDICES</h2>
          <div class="table-responsive-wrapper">
            <table class="apprentices-table">
              <thead>
                <tr>
                  <th>APRENDIZ</th>
                  <th>ESTADO</th>
                  <th>INGRESO</th>
                  <th class="text-center">ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in apprentices" :key="a.id">
                  <td>
                    <div class="table-user-info">
                      <strong>{{ a.name }}</strong>
                      <small>ID: VM-{{ a.id }}</small>
                    </div>
                  </td>
                  <td>
                    <span :class="a.status === 'present' ? 'status-green' : 'status-gray'">
                      {{ a.status === 'present' ? 'EN CLASE' : 'AUSENTE' }}
                    </span>
                  </td>
                  <td><span class="time-cell">{{ a.lastSeen }}</span></td>
                  <td>
                    <div class="actions-cell">
                      <button class="btn-table action-view" title="Ver Perfil" @click="openModal('profile', a)"><font-awesome-icon icon="fa-solid fa-user" /></button>
                      <button class="btn-table action-chart" title="Historial" @click="openModal('attendance', a)"><font-awesome-icon icon="fa-solid fa-calendar-days" /></button>
                      <button v-if="a.status === 'present' && hasPermission('gestionar_aula')" class="btn-table action-exit" title="Salida Inesperada" @click="openModal('exit', a)"><font-awesome-icon icon="fa-solid fa-right-from-bracket" /></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <QrModal
      :show="qrProjected"
      :fichaActiva="fichaActiva"
      @close="qrProjected = false"
    />

    <PinModal 
      v-if="showPinModal"
      :isLoading="isValidatingPin" 
      @close="showPinModal = false" 
      @submit="procesarValidacionPin"
    />

    <FirmaModal 
      v-if="showFirmaModal"
      :apprenticeName="aprendizSeleccionadoParaFirmar.name"
      @close="showFirmaModal = false"
      @save="procesarRegistroFirmaAsistencia"
    />

    <ProfileModal
      v-if="activeModal === 'profile'"
      :apprentice="selectedApprentice"
      @close="closeModal"
    />
    
    <AttendanceModal
      v-if="activeModal === 'attendance'"
      :apprentice="selectedApprentice"
      @close="closeModal"
    />
    
    <ExitModal
      v-if="activeModal === 'exit'"
      :apprentice="selectedApprentice"
      @close="closeModal"
      @confirm="handleExitConfirm"
    />
    
    <DarkModeToggle />
  </div>
</template>

<style scoped>
/* ==========================================
   ESTRUCTURA BASE Y CABECERA
   ========================================== */
.dashboard-shell { font-family: var(--fuente-principal); min-height: 100vh; background-color: var(--fondo-app); color: var(--texto-principal); padding: 1rem; box-sizing: border-box; }
.dash-header { display: flex; flex-direction: column; gap: 1rem; background: var(--fondo-tarjetas); padding: 1.25rem; border-radius: 16px; border: 1px solid var(--borde); margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03); }
.header-left { display: flex; flex-direction: column; gap: 0.75rem; }
.logo-duo { display: flex; align-items: center; gap: 12px; }
.logo-sena { height: 32px; width: auto; }
.logo-volt { height: 28px; width: auto; }
.logo-divider { width: 1px; height: 24px; background: var(--borde); }
.environment-badge h1 { font-size: 1.15rem; font-weight: 800; color: var(--sena-azul-oscuro); margin: 0; }
.header-meta { margin-top: 4px; font-size: 0.7rem; color: var(--texto-secundario); }
.header-meta span { color: var(--sena-azul-oscuro); font-family: monospace; font-weight: 600; }
.power-master-box { display: flex; align-items: center; justify-content: space-between; background: var(--fondo-app); border: 1px solid var(--borde); padding: 0.5rem 1rem; border-radius: 12px; }
.power-label { font-size: 0.65rem; font-weight: 700; color: var(--texto-secundario); }
.power-switch { width: 38px; height: 38px; border-radius: 50%; border: 2px solid var(--borde); background: var(--fondo-tarjetas); color: var(--texto-secundario); font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.power-switch.power-active { background: var(--sena-verde); color: var(--sena-blanco); border-color: var(--sena-verde-oscuro); box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25); }
.dash-grid { display: flex; flex-direction: column; gap: 1.5rem; }
.dash-col { display: flex; flex-direction: column; gap: 1.5rem; }

@media (min-width: 992px) {
  .dashboard-shell { padding: 1.5rem; }
  .dash-header { flex-direction: row; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; }
  .header-left { flex-direction: row; align-items: center; gap: 2.5rem; }
  .logo-sena { height: 44px; } .logo-volt { height: 40px; }
  .environment-badge h1 { font-size: 1.4rem; }
  .power-master-box { background: transparent; border: none; padding: 0; gap: 1.5rem; }
  .dash-grid { grid-template-columns: 1fr 380px; display: grid; }
}

/* ==========================================
   TARJETAS DE TIEMPO
   ========================================== */
.time-cards-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0 30px 0; }
.time-card { display: flex; align-items: center; padding: 16px; background-color: var(--fondo-tarjetas); border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid var(--borde); }
.start-card { border-left-color: var(--sena-verde-oscuro); } 
.end-card { border-left-color: #f43f5e; } 
.extra-card { border-left-color: var(--sena-amarillo); }
.icon-box { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0; }
.icon-box svg { width: 24px !important; height: 24px !important; }
.icon-box font-awesome-icon { font-size: 1.5rem; }
.start-card .icon-box { background-color: #d1fae5; color: #059669; }
.end-card .icon-box { background-color: #ffe4e6; color: #e11d48; }
.extra-card .icon-box { background-color: #fef3c7; color: #d97706; }
.info-box { display: flex; flex-direction: column; }
.card-title { font-size: 0.85rem; color: var(--texto-secundario); margin: 0 0 4px 0; font-weight: 500; }
.card-value { font-size: 1.25rem; font-weight: 700; color: var(--texto-principal); margin: 0; }
.power-switch svg { width: 1.5rem; height: 1.5rem; }

/* ==========================================
   MÓDULOS DE AULA Y MAPA IOT
   ========================================== */
.module-card { background: var(--fondo-tarjetas); border: 1px solid var(--borde); border-radius: 16px; padding: 1.25rem; }
.module-title { font-size: 0.75rem; font-weight: 700; color: var(--sena-azul-oscuro); margin: 0 0 1rem 0; display: flex; align-items: center; gap: 8px; text-transform: uppercase; }
.meters-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); 
  gap: 1rem; 
}
.speedometer-wrapper {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.speedometer-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
  text-align: center;
}
.meter-pill { background: var(--fondo-app); padding: 0.85rem; border-radius: 12px; border: 1px solid var(--borde); }
.meter-label { font-size: 0.6rem; color: var(--texto-secundario); font-weight: 600; display: block; margin-bottom: 4px; }
.meter-val { font-size: 1.2rem; font-weight: 800; color: var(--sena-azul-oscuro); }
.meter-val small { font-size: 0.7rem; color: var(--sena-verde); margin-left: 2px; }
.meter-bar { height: 4px; background: var(--borde); margin-top: 8px; border-radius: 2px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--sena-verde); transition: width 0.4s ease; }
.map-instruction { font-size: 0.7rem; color: var(--texto-secundario); margin: -0.5rem 0 1rem 0; }
.energy-control-layout { display: flex; flex-direction: column; gap: 1.5rem; }
.energy-top-row { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.section-subtitle { font-size: 0.7rem; text-transform: uppercase; color: var(--texto-secundario); margin-bottom: 0.5rem; font-weight: 700; border-bottom: 1px solid var(--borde); padding-bottom: 4px; }

/* Bancos */
.room-map-wrapper { flex: 2; min-width: 200px; }
.room-map { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.map-node { aspect-ratio: 1 / 1; max-width: 85px; width: 100%; background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 0.25rem; cursor: pointer; color: var(--texto-secundario); transition: all 0.2s ease; font-family: inherit; }
.map-node:hover:not(:disabled) { background: var(--fondo-tarjetas); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
.map-node:disabled { opacity: 0.6; cursor: not-allowed; }
.map-node small { font-size: 0.5rem; font-weight: 700; }
.node-bolt { font-size: 1rem; opacity: 0.5; }
.node-watts { font-size: 0.6rem; font-weight: 700; font-family: monospace; }
.map-node.node-on { background: rgba(57, 169, 0, 0.06); border-color: var(--sena-verde); color: var(--sena-verde-oscuro); }
.map-node.node-on .node-bolt { color: var(--sena-verde); opacity: 1; }

/* Luces */
.lights-wrapper { flex: 1; min-width: 150px; }
.lights-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.light-btn { background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 1rem 0.5rem; cursor: pointer; color: var(--texto-secundario); font-weight: 700; font-size: 0.65rem; transition: all 0.2s ease; }
.light-btn:hover:not(:disabled) { background: var(--fondo-tarjetas); }
.light-btn.light-on { background: rgba(253, 195, 0, 0.1); border-color: var(--sena-amarillo); color: #d49a00; }
.light-icon { font-size: 1.25rem; }

/* Rack Integrated (Inside DynamicMeterBar slot) */
.rack-panel-integrated { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; align-items: stretch; margin-top: 0.5rem; }
.rack-btn-integrated { background: var(--fondo-app); border: 2px solid var(--borde); border-radius: 8px; display: flex; align-items: center; justify-content: center; padding: 1rem; cursor: pointer; color: var(--texto-secundario); font-weight: 800; font-size: 1.5rem; transition: all 0.2s ease; }
.rack-btn-integrated.rack-on { background: rgba(0, 48, 64, 0.05); border-color: var(--sena-azul-oscuro); color: var(--sena-azul-oscuro); }
[data-theme="dark"] .rack-btn-integrated.rack-on { background: rgba(80, 229, 249, 0.1); color: var(--sena-cyan); border-color: var(--sena-cyan); }
.rack-stats-integrated { display: flex; flex-direction: column; gap: 0.5rem; justify-content: space-between; }
.stat-box-integrated { flex: 1; background: var(--fondo-app); border: 1px dashed var(--borde); border-radius: 8px; padding: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
.stat-box-integrated small { font-size: 0.7rem; color: var(--texto-secundario); font-weight: 700; text-transform: uppercase; }
.stat-box-integrated span { font-size: 1rem; font-weight: 800; font-family: monospace; }
.min-stat span { color: var(--sena-amarillo); }
.max-stat span { color: #ef4444; }

/* ==========================================
   TERMÓMETROS CHART.JS
   ========================================== */
.temp-charts-grid { display: flex; flex-wrap: wrap; gap: 1rem; padding-top: 1rem; }
.chart-box { flex: 1 1 150px; min-width: 0; background: var(--fondo-app); border-radius: 12px; border: 1px solid var(--borde); padding: 1rem 0; }

/* ==========================================
   BOTONERA LATERAL (3 COLUMNAS)
   ========================================== */
.actions-group { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.btn-action { padding: 1rem 0.5rem; border-radius: 12px; border: 1px solid var(--borde); background: var(--fondo-tarjetas); color: var(--texto-secundario); display: flex; flex-direction: column; align-items: center; gap: 6px; font-weight: 700; font-size: 0.65rem; cursor: pointer; border-style: solid; transition: all 0.2s ease; }
.btn-action:hover { background: var(--fondo-app); }
.btn-action.nfc.btn-active { background: var(--sena-azul-oscuro); color: var(--sena-blanco); border-color: var(--sena-azul-oscuro); }
.btn-action.qr.btn-active { background: var(--sena-verde); color: var(--sena-blanco); border-color: var(--sena-verde-oscuro); }
.btn-action.qr:hover:not(.btn-active) { border-color: var(--sena-verde); color: var(--sena-verde); background: rgba(57, 169, 0, 0.1); }
.btn-action.nfc:hover:not(.btn-active) { border-color: var(--sena-azul-oscuro); color: var(--sena-azul-oscuro); background: rgba(0, 48, 64, 0.05); }
[data-theme="dark"] .btn-action.nfc:hover:not(.btn-active) { background: rgba(80, 229, 249, 0.1); }
.btn-action.pin:hover { border-color: var(--sena-amarillo); color: var(--sena-azul-oscuro); background: rgba(253, 195, 0, 0.1); }

/* ==========================================
   TABLA DE APRENDICES
   ========================================== */
.dash-footer-table { grid-column: 1 / -1; }
.table-responsive-wrapper { width: 100%; overflow-x: auto; padding-bottom: 0.5rem; }
.apprentices-table { width: 100%; border-collapse: collapse; min-width: 450px; }
.apprentices-table th { padding: 10px 8px; border-bottom: 2px solid var(--fondo-app); font-size: 0.65rem; color: var(--texto-secundario); text-transform: uppercase; text-align: left; }
.apprentices-table td { padding: 12px 8px; border-bottom: 1px solid var(--fondo-app); font-size: 0.75rem; vertical-align: middle; }
.table-user-info strong { color: var(--sena-azul-oscuro); font-weight: 600; display: block; }
.table-user-info small { color: var(--texto-secundario); font-size: 0.65rem; }
.status-green { color: var(--sena-verde-oscuro); background: rgba(57, 169, 0, 0.1); padding: 4px 8px; border-radius: 12px; font-weight: 700; font-size: 0.6rem; }
.status-gray { color: var(--texto-secundario); background: var(--fondo-app); padding: 4px 8px; border-radius: 12px; font-weight: 600; font-size: 0.6rem; }
.time-cell { font-family: monospace; color: var(--texto-secundario); }
.actions-cell { display: flex; gap: 6px; }
.btn-table { border: 1px solid var(--borde); padding: 6px 10px; border-radius: 8px; cursor: pointer; background: var(--fondo-app); color: var(--texto-secundario); transition: all 0.2s; }
.btn-table:hover { color: var(--sena-azul-oscuro); background: var(--borde); }

/* ==========================================
   ESTILOS DE RESPALDO PARA MODAL PIN (Por si acaso el componente hijo los requiere)
   ========================================== */
.pin-modal { max-width: 360px; padding: 2rem 1.5rem; }
.pin-instruction { font-size: 0.8rem; color: var(--texto-secundario); margin: 0.5rem 0 1.5rem; line-height: 1.4; }
.pin-display { font-size: 2.2rem; font-weight: 800; color: var(--sena-azul-oscuro); background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 16px; height: 70px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; letter-spacing: 0.1em; transition: all 0.3s ease; }
.pin-display.is-loading { font-size: 1rem; letter-spacing: normal; color: var(--sena-verde); background: rgba(57, 169, 0, 0.1); border-color: var(--sena-verde); }
.keypad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem; transition: opacity 0.3s ease; }
.btn-key { aspect-ratio: 1 / 1; background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 12px; font-size: 1.4rem; font-weight: 700; color: var(--sena-azul-oscuro); cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; }
.btn-key:hover { background: var(--sena-blanco); border-color: var(--sena-verde); transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 48, 64, 0.05); }
.btn-key:active { transform: translateY(0); }
.action-key { font-size: 1.1rem; color: #e53e3e; background: rgba(229, 62, 62, 0.05); border-color: transparent; }
.action-key:hover { background: #e53e3e; color: white; border-color: #e53e3e; }
.submit-key { font-size: 1.2rem; background: var(--sena-verde); color: white; border-color: var(--sena-verde-oscuro); }
.submit-key:hover:not(:disabled) { background: var(--sena-verde-oscuro); }
.submit-key:disabled { background: var(--borde); border-color: var(--borde); color: var(--texto-secundario); cursor: not-allowed; opacity: 0.5; }
</style>