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

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
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

const meters = ref([
  { id: 1, label: "Iluminación Aula", value: 120 },
  { id: 2, label: "Bancos de Cómputo", value: 850 },
  { id: 3, label: "Rack Comunicaciones", value: 450 },
]);

// Si el aula ya estaba encendida en caché, cargamos los nodos encendidos
const roomNodes = ref(
  Array.from({ length: 16 }, (_, i) => ({
    id: i + 1,
    energized: isPowerOn.value,
    load: Math.floor(Math.random() * 90) + 10,
  }))
);

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

  wsDashboard = new WebSocket(`ws://localhost:8000/api/ws/ambiente/${ambienteSeleccionadoId.value}`);

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

  try {
    const res = await fetch(`${BASE_URL}/api/asistencia/habilitar-salida/${sesionId}`, { method: "POST" });
    if (res.ok) {
      salidaHabilitada.value = true;
      localStorage.setItem('salidaHabilitada', 'true'); 
      qrProjected.value = false;
      toast.success("¡Clase finalizada! Ya puedes registrar las firmas de los presentes.");
    }
  } catch (error) {
    toast.error("Error al conectar con el servidor para habilitar salidas.");
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
  if (!isPowerOn.value && (!ambienteSeleccionadoId.value || ambienteSeleccionadoId.value === "Sin Definir")) {
    toast.warning("¡Alerta! No se detectó un ambiente enlazado.");
    router.push("/route-selector"); 
    return; 
  }

  isPowerOn.value = !isPowerOn.value;
  roomNodes.value.forEach((node) => { node.energized = isPowerOn.value; });

  if (isPowerOn.value) {
    salidaHabilitada.value = false;
    toast.info("Energizando aula y registrando inicio de clase...");
    
    try {
      const emailInstructor = localStorage.getItem('instructorEmail') || "";
      
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

        toast.success("¡Aula ENERGIZADA y sesión registrada con éxito!");
      } else {
        throw new Error("El servidor rechazó el inicio de sesión");
      }
    } catch (error) {
      isPowerOn.value = false;
      roomNodes.value.forEach((node) => { node.energized = false; });
      toast.error("Error de conexión con Dataverse. Reintente encender.");
    }
  
  } else {
    toast.info("Apagando aula y guardando asistencias en Dataverse...");
    try {
      const sesionId = localStorage.getItem('sesionActivaId') || "";
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

      const responseCierre = await fetch(`${BASE_URL}/api/sesiones/finalizar?sesion_id=${sesionId}`, { method: "POST" });
      if (!responseCierre.ok) throw new Error("Fallo finalizando la sesión.");
      
      const dataCierre = await responseCierre.json();
      horaFin.value = new Date(dataCierre.hora_salida).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
      tiempoExtra.value = dataCierre.tiempo_extra;

      localStorage.setItem('isPowerOn', 'false');
      localStorage.setItem('salidaHabilitada', 'false');
      localStorage.setItem('horaFin', horaFin.value);
      localStorage.removeItem('sesionActivaId'); 

      salidaHabilitada.value = false;
      isPowerOn.value = false;
      toast.success("¡Aula APAGADA y datos guardados correctamente!");
      
    } catch (error) {
      isPowerOn.value = true; 
      toast.error("Error al cerrar la clase en Dataverse.");
    }
  }
};

const toggleNodePower = (node) => {
  node.energized = !node.energized;
  isPowerOn.value = roomNodes.value.some((n) => n.energized);
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
        <span class="power-label">{{ isPowerOn ? "AULA ENERGIZADA" : "AULA APAGADA" }}</span>
        <button class="power-switch" :class="{ 'power-active': isPowerOn }" @click="toggleMasterPower">
          <font-awesome-icon icon="fa-solid fa-power-off" />
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
            <div v-for="m in meters" :key="m.id" class="meter-pill">
              <span class="meter-label">{{ m.label }}</span>
              <span class="meter-val">{{ isPowerOn ? m.value : 0 }}<small>W</small></span>
              <div class="meter-bar">
                <div class="bar-fill" :style="{ width: isPowerOn ? m.value / 10 + '%' : '0%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="module-card map-card">
          <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-plug" /> CONTROL DE ENERGÍA POR ESTACIÓN</h2>
          <p class="map-instruction">Haz clic sobre un puesto para conmutar su flujo eléctrico.</p>
          <div class="room-map-wrapper">
            <div class="room-map">
              <button v-for="node in roomNodes" :key="node.id" class="map-node" :class="{ 'node-on': node.energized }" @click="hasPermission('gestionar_aula') ? toggleNodePower(node) : null" :disabled="!hasPermission('gestionar_aula')">
                <small>P{{ node.id }}</small>
                <font-awesome-icon icon="fa-solid fa-bolt" class="node-bolt" />
                <span class="node-watts">{{ node.energized ? node.load + "W" : "OFF" }}</span>
              </button>
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

          <button v-if="isPowerOn" class="btn-action" :class="{ 'btn-active': salidaHabilitada }" style="background-color: #f39c12; color: white;" @click="habilitarSalidaClase" :disabled="salidaHabilitada">
            <font-awesome-icon icon="fa-solid fa-flag-checkered" />
            <span>{{ salidaHabilitada ? "SALIDAS ACTIVAS" : "FINALIZAR CLASE" }}</span>
          </button>

          <button class="btn-action" style="background-color: #34495e; color: white;" @click="enviarReporteSemanalManual">
            <font-awesome-icon icon="fa-solid fa-file-excel" />
            <span>ENVIAR REPORTE</span>
          </button>
        </div>

        <AlertPanel title="ALERTAS DEL AMBIENTE" icon="fa-solid fa-triangle-exclamation" :alerts="systemAlerts" @resolve="handleAlertResolution" />
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
.meters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem; }
.meter-pill { background: var(--fondo-app); padding: 0.85rem; border-radius: 12px; border: 1px solid var(--borde); }
.meter-label { font-size: 0.6rem; color: var(--texto-secundario); font-weight: 600; display: block; margin-bottom: 4px; }
.meter-val { font-size: 1.2rem; font-weight: 800; color: var(--sena-azul-oscuro); }
.meter-val small { font-size: 0.7rem; color: var(--sena-verde); margin-left: 2px; }
.meter-bar { height: 4px; background: var(--borde); margin-top: 8px; border-radius: 2px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--sena-verde); transition: width 0.4s ease; }
.map-instruction { font-size: 0.7rem; color: var(--texto-secundario); margin: -0.5rem 0 1rem 0; }
.room-map-wrapper { width: 100%; overflow: hidden; }
.room-map { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }

@media (min-width: 992px) { .room-map { grid-template-columns: repeat(8, 1fr); max-width: 760px; } }

.map-node { aspect-ratio: 1 / 1; max-width: 85px; width: 100%; background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 0.25rem; cursor: pointer; color: var(--texto-secundario); transition: all 0.2s ease; font-family: inherit; border-style: solid; }
.map-node:hover:not(:disabled) { background: var(--fondo-tarjetas); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
.map-node:disabled { opacity: 0.6; cursor: not-allowed; }
.map-node small { font-size: 0.5rem; font-weight: 700; }
.node-bolt { font-size: 1rem; opacity: 0.5; }
.node-watts { font-size: 0.6rem; font-weight: 700; font-family: monospace; }
.map-node.node-on { background: rgba(57, 169, 0, 0.06); border-color: var(--sena-verde); color: var(--sena-verde-oscuro); }
.map-node.node-on .node-bolt { color: var(--sena-verde); opacity: 1; }

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