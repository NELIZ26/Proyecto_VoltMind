<script setup>
import DarkModeToggle from '@/components/DarkModeToggle.vue';
import FirmaModal from "@/components/FirmaModal.vue";
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { useKioskStore } from '@/stores/kioskStore';
// IMPORTACIÓN DE COMPONENTES DEL SUBSISTEMA
import PinKeypadModal from "@/components/PinKeypadModal.vue";
import QrModal from "@/components/QrModal.vue";
import ProfileModal from "@/components/profileModal.vue";
import AttendanceModal from "@/components/attendanceModal.vue";
import ExitModal from "@/components/exitModal.vue";
import AlertPanel from "@/components/AlertPanel.vue";
import { useRole } from "@/composables/useRole";

const toast = useToast();
const router = useRouter();
const { hasRole, hasPermission } = useRole();
const kioskStore = useKioskStore();

// --- ESTADOS REACTIVOS PRINCIPALES ---
const isPowerOn = ref(false);
const nfcScanning = ref(false);
const qrProjected = ref(false);
const currentTime = ref(new Date().toLocaleTimeString());

// --- ESTADOS DE DATOS REALES (Tu conexión restaurada) ---
const fichaActiva = ref(""); 
const apprentices = ref([]); 
const isLoading = ref(true); 
const nombrePrograma = ref("");
const nombreInstructor = ref("");

const lightState1 = ref(false); 
const lightState2 = ref(false);

// --- ESTADOS DEL TECLADO PIN ---
const showPinModal = ref(false);
const isValidatingPin = ref(false);

// CONTROLADORES DE INTERCEPCIÓN PARA LA FIRMA
const showFirmaModal = ref(false);
const aprendizSeleccionadoParaFirmar = ref({ name: "", doc: "" });

// Recuperamos la hora si el profe recarga la página, si no, mostramos "--:--"
const horaInicio = ref(localStorage.getItem('horaInicio') || '--:--');
const horaFin = ref('--:--');
const tiempoExtra = ref('0 min'); // Más adelante le daremos lógica a esto

// --- ESTADOS DE ALERTAS ---
const systemAlerts = ref([
  {
    id: 1,
    severity: "warning",
    message: "Alerta de Deserción: Validación Dataverse pendiente.",
    source: "Asistencia",
    timestamp: "Hoy",
  },
]);

// --- MANEJO DE VENTANAS MODALES ---
const activeModal = ref(null);
const selectedApprentice = ref(null);

// --- MOCK DATA INSTITUCIONAL (Energía) ---
const meters = ref([
  { id: 1, label: "ZONA 1 (Iluminación Aula)", value: 0 },
  { id: 2, label: "ZONA 2 (Bancos de Cómputo)", value: 0 }
]);

const roomNodes = ref(
  Array.from({ length: 16 }, (_, i) => ({
    id: i + 1,
    energized: false,
    load: Math.floor(Math.random() * 90) + 10,
  }))
);

const toggleLights = async (zone) => {
  const currentState = zone === 1 ? lightState1.value : lightState2.value;
  const newState = !currentState;
  try {
    const response = await fetch("http://127.0.0.1:8000/api/iot/relay", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rele: `L${zone}`, estado: newState ? "1" : "0" })
    });
    
    if (response.ok) {
      if (zone === 1) lightState1.value = newState;
      else lightState2.value = newState;
      toast.success(newState ? `💡 Iluminación Z${zone} Encendida` : `💡 Iluminación Z${zone} Apagada`);
    } else {
      toast.error("Error al comunicarse con el módulo IoT.");
    }
  } catch (error) {
    console.error(error);
    toast.error("Servidor IoT desconectado.");
  }
};

// --- GESTIÓN DEL TECLADO PIN ---
const handlePinSubmit = async (pinValue) => {
  if (pinValue.length !== 4) {
    toast.error("El PIN debe tener exactamente 4 dígitos.");
    return;
  }
  isValidatingPin.value = true;
  
  try {
    const sesionId = localStorage.getItem('sesionActivaId') || "";
    const response = await fetch(`http://127.0.0.1:8000/api/asistencia/validar-pin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        pin: pinValue,
        sesion_id: sesionId
      })
    });

    if (response.ok) {
      const data = await response.json();
      
      // Buscamos el documento retornado en nuestra lista local de la ficha
      const aprendizEncontrado = apprentices.value.find(a => a.doc === data.documento_aprendiz);
      
      if (aprendizEncontrado) {
        // Interceptamos el flujo: Cargamos los datos y abrimos la firma en la tablet
        aprendizSeleccionadoParaFirmar.value = {
          name: aprendizEncontrado.name,
          doc: aprendizEncontrado.doc
        };
        showPinModal.value = false; // Cerramos el teclado
        showFirmaModal.value = true; // 🖋️ Abrimos el lienzo de firmas
      } else {
        toast.warning("PIN válido, pero el aprendiz no pertenece a esta ficha operativa.");
      }
    } else {
      toast.error("El código introducido es incorrecto o ya caducó.");
    }
  } catch (error) {
    console.error("Error validando PIN:", error);
    toast.error("Error de respuesta del nodo central.");
  } finally {
    isValidatingPin.value = false;
  }
};

const procesarRegistroFirmaAsistencia = async (base64Signature) => {
  const sesionId = localStorage.getItem('sesionActivaId') || "";
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/asistencia/guardar-firma`, {
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
      const index = apprentices.value.findIndex(a => a.doc === aprendizSeleccionadoParaFirmar.value.doc);
      if (index !== -1) {
        if (apprentices.value[index].status === 'present') {
           apprentices.value[index].status = "absent";
           apprentices.value[index].lastSeen = "Salida: " + new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
           toast.success(`¡Salida y firma registradas para ${aprendizSeleccionadoParaFirmar.value.name}!`);
        } else {
           apprentices.value[index].status = "present";
           apprentices.value[index].lastSeen = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
           toast.success(`¡Asistencia y firma registradas para ${aprendizSeleccionadoParaFirmar.value.name}!`);
        }
      }
      showFirmaModal.value = false;
    } else {
      toast.error("Falló el empaquetado del registro en la memoria del servidor.");
    }
  } catch (error) {
    console.error(error);
    toast.error("Error de red al procesar la firma táctil.");
  }
};

const solicitarReporteAsistenciaPDF = async (idDeSesionCerrada) => {
  console.log("Ejecutando orden de PDF para la sesión:", idDeSesionCerrada);
  toast.info("Ensamblando PDF con las firmas...");
  
  try {
    // Tomamos todo del localStorage para evitar errores de variables no definidas en Vue
    const correo = localStorage.getItem('instructorEmail') || "ferley_tobon@soy.sena.edu.co";
    const ficha = localStorage.getItem('fichaActiva') || "3465773";
    const programa = localStorage.getItem('nombrePrograma') || "Analisis y Desarrollo de Software";
    const instructor = localStorage.getItem('instructorName') || "Ferley Tobon";

    const response = await fetch(`http://127.0.0.1:8000/api/asistencia/generar-reporte`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sesion_id: idDeSesionCerrada,
        numero_ficha: ficha,
        nombre_programa: programa,
        nombre_instructor: instructor,
        correo_destino: correo
      })
    });

    if (response.ok) {
      toast.success("¡PDF generado en el servidor con éxito!");
      console.log("¡Orden de PDF completada en Python!");
    } else {
      const err = await response.json();
      console.error("Error del backend:", err);
      toast.warning("Fallo al empaquetar el PDF.");
    }
  } catch (error) {
    console.error("Error de conexión al pedir el PDF:", error);
    toast.error("Fallo de red al solicitar el reporte final.");
  }
};

// --- OPERACIONES IOT (Lógica mejorada del Equipo) ---
const toggleMasterPower = async () => {
  isPowerOn.value = !isPowerOn.value;
  
  roomNodes.value.forEach((node) => {
    node.energized = isPowerOn.value;
  });

  // ==========================================
  // 🟢 ENVIAR ORDEN MAESTRA AL ARDUINO
  // ==========================================
  try {
    await fetch(`http://127.0.0.1:8000/api/iot/master`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado: isPowerOn.value ? "1" : "0" })
    });
  } catch (error) {
    console.error("Error enviando comando maestro:", error);
  }

  // ==========================================
  // 🟢 LÓGICA DE ENCENDIDO
  // ==========================================
  if (isPowerOn.value) {
    toast.info("Energizando aula y registrando inicio de clase...");
    
    try {
      const emailInstructor = localStorage.getItem('instructorEmail') || "";
      const responseSesion = await fetch(`http://127.0.0.1:8000/api/sesiones/iniciar?ficha=${fichaActiva.value}&email=${emailInstructor}`, {
        method: "POST"
      });

      if (responseSesion.ok) {
        const data = await responseSesion.json();
        
        // 1. Guardamos el ID único de ESTA sesión en el navegador
        localStorage.setItem('sesionActivaId', data.sesion_id);
        
        // 2. Formatear y mostrar hora de inicio
        const fechaEntrada = new Date(data.hora_entrada);
        horaInicio.value = fechaEntrada.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        localStorage.setItem('horaInicio', horaInicio.value); // Para que no se borre si recarga la página
        horaFin.value = '--:--'; // Reseteamos la hora de fin por si había una anterior
        localStorage.removeItem('horaFin'); // Limpiar la de la clase anterior
        
        toast.success("¡Aula ENERGIZADA y sesión registrada con éxito!");
      } else {
        const errorData = await responseSesion.json();
        console.error("Error del servidor:", errorData);
        toast.error("Aula encendida, pero falló el registro en base de datos.");
      }
    } catch (error) {
      console.error("Error de conexión:", error);
      toast.error("Error de conexión con el servidor.");
    }
    
  } 
  // ==========================================
  // 🔴 LÓGICA DE APAGADO
  // ==========================================
  else {
    toast.info("Apagando aula y registrando salida...");
    
    try {
      // Recuperamos el ID exacto que guardamos al encender
      const sesionId = localStorage.getItem('sesionActivaId') || "";
      
      if (!sesionId) {
        toast.warning("El aula se apagó, pero no se encontró una sesión activa para cerrar.");
        return; 
      }

      const responseCierre = await fetch(`http://127.0.0.1:8000/api/sesiones/finalizar?sesion_id=${sesionId}`, {
        method: "POST"
      });

      if (responseCierre.ok) {
        const dataCierre = await responseCierre.json();
        
        // 🟢 ¡AQUÍ ESTÁ LA LÍNEA QUE FALTABA! Disparamos el PDF antes de limpiar la memoria
        console.log("Enviando orden al backend para generar PDF...");
        await solicitarReporteAsistenciaPDF(sesionId);

        // Limpiamos la memoria
        localStorage.removeItem('sesionActivaId'); 
        localStorage.removeItem('horaInicio'); 
        
        // Formatear hora de fin
        const fechaSalida = new Date(dataCierre.hora_salida);
        horaFin.value = fechaSalida.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        localStorage.setItem('horaFin', horaFin.value);
        
        // 🟡 NUEVO: Actualizar la tarjeta amarilla
        tiempoExtra.value = dataCierre.tiempo_extra;

        toast.success("¡Aula APAGADA y sesión finalizada en Dataverse!");
      }
       else {
        const errorData = await responseCierre.json();
        console.error("Error del servidor al cerrar:", errorData);
        toast.error("El aula se apagó, pero falló el registro de salida.");
      }
    } catch (error) {
      console.error("Error de conexión:", error);
      toast.error("Error de conexión con el servidor al cerrar.");
    }
  }
};

const toggleNodePower = async (node) => {
  node.energized = !node.energized;
  if (!node.energized && !roomNodes.value.some((n) => n.energized)) {
    isPowerOn.value = false;
  } else {
    isPowerOn.value = true;
  }

  // --- NUEVA LÓGICA IOT: Enviar comando al Arduino para P1, P2 o P3 ---
  if (node.id >= 1 && node.id <= 3) {
    try {
      await fetch(`http://127.0.0.1:8000/api/iot/relay`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rele: String(node.id),
          estado: node.energized ? "1" : "0"
        })
      });
    } catch (error) {
      console.error(`Error al conmutar relé ${node.id}:`, error);
      toast.error(`No se pudo comunicar con el relé ${node.id}`);
    }
  }
};

// --- SUBSISTEMA DE ALERTAS Y MODALES ---
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

const goToLogin = () => {
  router.push("/login");
};

const handleManualAttendance = (a) => {
  if (a.status !== 'present') {
    a.status = 'present';
    a.lastSeen = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
    toast.success(`Asistencia registrada manualmente para ${a.name}`);
  }
};

const handleManualExit = async (a) => {
  // Cuando es manual exit (y firma), enviamos la orden a FastAPI para que la Tablet reaccione
  toast.info(`Forzando firma en kiosko para ${a.name}...`);
  try {
    const response = await fetch("http://127.0.0.1:8000/api/kiosko/forzar-firma", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ambiente_id: "402", // Por ahora estático
        aprendiz_id: a.doc,
        nombre_aprendiz: a.name
      })
    });
    if (response.ok) {
      toast.success(`Petición enviada. La tablet ahora solicitará la firma de ${a.name}`);
    }
  } catch (error) {
    toast.error("Error al comunicarse con el Kiosko.");
  }
};

// Control de Estado del Kiosko
const kioskStatus = ref("ACTIVO");

const toggleKioskStatus = async () => {
  let nuevoEstado = "ACTIVO";
  if (kioskStatus.value === "ACTIVO") nuevoEstado = "BLOQUEADO";
  else if (kioskStatus.value === "BLOQUEADO") nuevoEstado = "MODO_SALIDA";
  else nuevoEstado = "ACTIVO";
  
  try {
    const response = await fetch("http://127.0.0.1:8000/api/kiosko/estado", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ambiente_id: "402", estado: nuevoEstado })
    });
    if (response.ok) {
      kioskStatus.value = nuevoEstado;
      toast.success(`Kiosko actualizado a: ${nuevoEstado}`);
    }
  } catch (error) {
    toast.error("Error al enviar el comando al kiosko.");
  }
};

// --- CICLO DE VIDA (Tu conexión real a FastAPI y Dataverse) ---
onMounted(async () => {
  // 1. Guardián de Seguridad del Equipo
  if (!hasRole(["instructor", "dinamizador"])) {
    toast.error("Acceso denegado. Se requiere perfil de Instructor.");
    router.push("/route-selector");
    return;
  }

  // 2. Reloj y Telemetría IoT
  setInterval(async () => {
    currentTime.value = new Date().toLocaleTimeString();
    
    // Polling de Telemetría (cada segundo)
    try {
      const res = await fetch("http://127.0.0.1:8000/api/iot/telemetry");
      if (res.ok) {
        const data = await res.json();
        if (data["1"] !== undefined) {
          // Asignar el valor al primer medidor (Iluminación Aula)
          meters.value[0].value = Math.round(data["1"]); 
        }
        if (data["2"] !== undefined) {
          // Asignar el valor al segundo medidor (Bancos de Cómputo)
          meters.value[1].value = Math.round(data["2"]);
        }
      }
    } catch (e) {
      console.error("Error en telemetría:", e);
    }
  }, 1000);

  // 3. Tus variables reales de localStorage
  fichaActiva.value = localStorage.getItem('fichaActiva') || "Sin Ficha";
  nombrePrograma.value = localStorage.getItem('nombrePrograma') || "Programa no definido";
  nombreInstructor.value = localStorage.getItem('nombreInstructor') || "Instructor";

  if (fichaActiva.value === "Sin Ficha") {
    toast.error("No hay una ficha activa. Redirigiendo...");
    router.push("/route-selector");
    return;
  }

  // 4. Tu llamada a FastAPI
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/fichas/${fichaActiva.value}/aprendices`);
    
    if (!response.ok) {
      throw new Error("No se encontraron aprendices para esta ficha.");
    }

    const data = await response.json();
    
    // Mapeo real de datos
    apprentices.value = data.map((ap) => ({
      id: ap.documento,
      name: ap.nombre || 'Sin Nombre',
      doc: ap.documento,
      email: ap.correo,
      status: "absent", 
      lastSeen: "Esperando ingreso",
      absences: 0,
      enum: "N/A",
      history: []
    }));

  } catch (error) {
    console.error("Error consultando aprendices:", error);
    toast.warning("El aula está lista, pero no hay aprendices registrados.");
  } finally {
    isLoading.value = false;
  }

  // 5. Iniciar la conexión WebSocket para recibir asistencias en tiempo real
  kioskStore.connectWebSocket("402");
});

// ESCUCHAR ASISTENCIAS EN TIEMPO REAL DESDE LA TABLET
watch(() => kioskStore.ultimaAsistencia, (newAsistencia) => {
  if (newAsistencia) {
    const index = apprentices.value.findIndex(a => String(a.doc) === String(newAsistencia.documento));
    if (index !== -1) {
      // Clonamos para forzar reactividad en el array
      const student = { ...apprentices.value[index] };
      const accionStr = String(newAsistencia.accion || "").toUpperCase().trim();

      if (accionStr === "INGRESO" || accionStr === "ENTRADA") {
        student.status = "present";
        student.lastSeen = newAsistencia.hora;
      } else if (accionStr === "SALIDA") {
        student.status = "absent"; 
        student.lastSeen = newAsistencia.hora;
      } else {
        // Fallback robusto por si el backend manda algo diferente a INGRESO/SALIDA
        student.status = "present";
        student.lastSeen = newAsistencia.hora || new Date().toLocaleTimeString();
      }
      
      // Reasignación en el índice para que Vue renderice los cambios
      apprentices.value[index] = student;
    }
  }
}, { deep: true });

</script>

<template>
  <div class="dashboard-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="logo-duo">
          <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
          <div class="logo-divider" />
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind"
            class="logo-volt"
          />
        </div>
        <div class="environment-badge">
          <h1>AMBIENTE 402</h1>
          <p class="header-meta">
            Ficha: {{ fichaActiva }} - {{ nombrePrograma }} | Instructor: {{ nombreInstructor }} |
           <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>

      <div class="header-right-actions" v-if="hasPermission('gestionar_aula')">
        <span class="power-label">{{
          isPowerOn ? "AULA ENERGIZADA" : "AULA APAGADA"
        }}</span>
        <div class="header-action-col">
          <button
            class="power-switch"
            :class="{ 'power-active': isPowerOn }"
            @click="toggleMasterPower"
            style="width: 42px; height: 42px; font-size: 1.2rem;"
          >
            <font-awesome-icon icon="fa-solid fa-power-off" />
          </button>
          <span class="header-action-label" style="visibility: hidden;">_</span>
        </div>
        <div class="header-action-col">
          <button class="header-icon-btn exit-icon" @click="goToLogin">
            <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
          </button>
          <span class="header-action-label">EXIT</span>
        </div>
        <div class="header-action-col">
          <button class="header-icon-btn carnet-icon">
            <font-awesome-icon icon="fa-solid fa-clipboard-user" />
          </button>
          <span class="header-action-label">CARNET</span>
        </div>
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
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-microchip" /> TELEMETRÍA DE
            CONSUMO
          </h2>

          <div class="meters-grid">
            <div v-for="m in meters" :key="m.id" class="meter-pill">
              <span class="meter-label">{{ m.label }}</span>
              <span class="meter-val"
                >{{ m.value }}<small>W</small></span
              >
              <div class="meter-bar">
                <div
                  class="bar-fill"
                  :style="{ width: (m.value > 100 ? 100 : m.value) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="module-card map-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-plug" /> CONTROL DE ENERGÍA POR
            ESTACIÓN
          </h2>
          <p class="map-instruction">
            Haz clic sobre un puesto para conmutar su flujo eléctrico de forma
            independiente.
          </p>

          <div class="map-and-lights-container">
            <div class="room-map-wrapper" style="flex: 2;">
              <div class="room-map">
                <button
                  v-for="node in roomNodes"
                  :key="node.id"
                  class="map-node"
                  :class="{ 'node-on': node.energized }"
                  @click="hasPermission('gestionar_aula') ? toggleNodePower(node) : null"
                  :disabled="!hasPermission('gestionar_aula')"
                >
                  <small>P{{ node.id }}</small>
                  <font-awesome-icon icon="fa-solid fa-bolt" class="node-bolt" />
                  <span class="node-watts">{{ node.energized ? node.load + "W" : "OFF" }}</span>
                </button>
              </div>
            </div>
            
            <div class="lighting-controls-wrapper" style="flex: 1; display: flex; flex-direction: row; gap: 15px; justify-content: center; align-items: center; border-left: 1px solid var(--borde); padding-left: 20px;">
              <button 
                class="light-big-btn" 
                :class="{'active': lightState1}" 
                @click="toggleLights(1)"
              >
                <small>ZONA 1</small>
                <font-awesome-icon icon="fa-solid fa-lightbulb" class="lb-icon" />
                <span class="node-status">{{ lightState1 ? "ON" : "OFF" }}</span>
              </button>
              
              <button 
                class="light-big-btn" 
                :class="{'active': lightState2}" 
                @click="toggleLights(2)"
              >
                <small>ZONA 2</small>
                <font-awesome-icon icon="fa-solid fa-lightbulb" class="lb-icon" />
                <span class="node-status">{{ lightState2 ? "ON" : "OFF" }}</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-col attendance-section">
        <button 
          class="btn-wide-action" 
          v-if="hasPermission('gestionar_aula')"
          :class="{
            'kiosk-active': kioskStatus === 'ACTIVO',
            'kiosk-blocked': kioskStatus === 'BLOQUEADO',
            'kiosk-exit': kioskStatus === 'MODO_SALIDA'
          }"
          @click="toggleKioskStatus"
        >
          {{ kioskStatus === 'ACTIVO' ? 'BLOQUEAR KIOSKO' : (kioskStatus === 'BLOQUEADO' ? 'HABILITAR SALIDAS KIOSKO' : 'ABRIR KIOSKO (ENTRADAS)') }}
        </button>

        <div class="module-card alert-card">
          <div class="alert-card-header">
            <h2 class="module-title">
              <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> ALERTA DE AMBIENTE
            </h2>
            <span class="alert-badge">1</span>
          </div>
          <div class="alerts-list">
             <div class="alert-item alert-warning">
               <div class="alert-icon"><font-awesome-icon icon="fa-solid fa-triangle-exclamation" /></div>
               <div class="alert-content">
                 <p class="alert-msg">Alerta de Deserción: Validación Dataverse pendiente.</p>
                 <span class="alert-meta">HOY • ASISTENCIA</span>
               </div>
               <div class="alert-check"><font-awesome-icon icon="fa-solid fa-check" /></div>
             </div>
             <div class="alert-item alert-success">
               <div class="alert-icon"><font-awesome-icon icon="fa-solid fa-shield-halved" /></div>
               <div class="alert-content">
                 <p class="alert-msg">Validación de Asistencia Exitosa<br>Aprendiz Registrado</p>
                 <span class="alert-meta">HOY • ASISTENCIA</span>
               </div>
               <div class="alert-check active"><font-awesome-icon icon="fa-solid fa-check" /></div>
             </div>
          </div>
          <button class="btn-show-more">Mostrar más</button>
        </div>

        <button class="btn-wide-action with-icon" v-if="hasPermission('gestionar_aula')">
          <font-awesome-icon icon="fa-solid fa-chart-simple" /> GENERACION DE INFORMES
        </button>
      </section>

      <section
        class="dash-footer-table"
        v-if="hasRole(['instructor', 'dinamizador'])"
      >
        <div class="module-card table-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-users" /> LISTADO OPERATIVO DE
            APRENDICES
          </h2>
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
                    <span
                      :class="
                        a.status === 'present' ? 'status-green' : 'status-gray'
                      "
                    >
                      {{ a.status === "present" ? "EN CLASE" : "AUSENTE" }}
                    </span>
                  </td>
                  <td>
                    <span class="time-cell">{{ a.lastSeen }}</span>
                  </td>
                  <td>
                    <div class="actions-cell">
                      <button
                        class="btn-table action-view"
                        title="Ver Perfil"
                        @click="openModal('profile', a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-user" />
                      </button>
                      <button
                        class="btn-table action-chart"
                        title="Historial"
                        @click="openModal('attendance', a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-calendar-days" />
                      </button>
                      <button
                        v-if="a.status !== 'present' && hasPermission('gestionar_aula')"
                        class="btn-table action-attendance"
                        title="Registrar Ingreso"
                        @click="handleManualAttendance(a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-check" />
                      </button>
                      <button
                        v-if="a.status === 'present' && hasPermission('gestionar_aula')"
                        class="btn-table action-exit"
                        title="Registrar Salida"
                        @click="handleManualExit(a)"
                      >
                        <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
                      </button>
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

    <PinKeypadModal 
      :isLoading="isValidatingPin" 
      :show="showPinModal" 
      @close="showPinModal = false" 
      @submit="handlePinSubmit"
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
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL (SENA 2024 - CASO BLANCO MÁXIMO)
   ========================================================================== */
.dashboard-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  background-color: var(--fondo-app);
  color: var(--texto-principal);
  padding: 1rem;
  box-sizing: border-box;
}

.dash-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--fondo-tarjetas);
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
}

.kiosk-active {
  background: var(--sena-verde) !important;
  color: white !important;
  border-color: var(--sena-verde-oscuro) !important;
}
.kiosk-blocked {
  background: #ef4444 !important;
  color: white !important;
  border-color: #b91c1c !important;
}
.kiosk-exit {
  background: #f59e0b !important;
  color: white !important;
  border-color: #d97706 !important;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.logo-duo {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-sena {
  height: 32px;
  width: auto;
}
.logo-volt {
  height: 28px;
  width: auto;
}
.logo-divider {
  width: 1px;
  height: 24px;
  background: var(--borde);
}
.environment-badge h1 {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.7rem;
  color: var(--texto-secundario);
}
.header-meta span {
  color: var(--sena-azul-oscuro);
  font-family: monospace;
  font-weight: 600;
}

.power-master-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 0.5rem 1rem;
  border-radius: 12px;
}
.power-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
}
.power-switch {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid var(--borde);
  background: var(--fondo-tarjetas);
  color: var(--texto-secundario);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.power-switch.power-active {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border-color: var(--sena-verde-oscuro);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.dash-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* REGLAS MULTICOLUMNA PARA PANTALLAS GRANDES Y TABLETS */
@media (min-width: 992px) {
  .dashboard-shell {
    padding: 1.5rem;
  }
  .dash-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 2rem;
  }
  .header-left {
    flex-direction: row;
    align-items: center;
    gap: 2.5rem;
  }
  .logo-sena {
    height: 44px;
  }
  .logo-volt {
    height: 40px;
  }
  .environment-badge h1 {
    font-size: 1.4rem;
  }
  .header-right-actions {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }
  .dash-grid {
    grid-template-columns: 1fr 380px;
    display: grid;
  }
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.header-action-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.header-icon-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid var(--borde);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
}
.header-icon-btn.exit-icon {
  color: #e11d48;
  border-color: #e11d48;
}
.header-icon-btn.carnet-icon {
  color: var(--texto-secundario);
  border-color: var(--texto-secundario);
}
.header-action-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.dash-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.25rem;
}
.module-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
}

.light-control-inline {
  display: flex;
  justify-content: flex-end;
  margin-top: -3rem;
  margin-bottom: 1rem;
}
.btn-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--borde);
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1.2rem;
}
.btn-icon-circle.btn-table.action-exit {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.light-big-btn {
  aspect-ratio: 1 / 1;
  max-width: 85px;
  width: 100%;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--texto-secundario);
  transition: all 0.2s ease;
  font-family: inherit;
}

.light-big-btn:hover {
  background: var(--fondo-tarjetas);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.light-big-btn.active {
  background: rgba(57, 169, 0, 0.06);
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}

.light-big-btn small {
  font-size: 0.5rem;
  font-weight: 700;
}

.light-big-btn .lb-icon {
  font-size: 1rem;
  opacity: 0.5;
}

.light-big-btn.active .lb-icon {
  color: var(--sena-verde);
  opacity: 1;
}

.light-big-btn .node-status {
  font-size: 0.6rem;
  font-weight: 700;
  font-family: monospace;
}

.meters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
}
.meter-pill {
  background: var(--fondo-app);
  padding: 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
}
.meter-label {
  font-size: 0.6rem;
  color: var(--texto-secundario);
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}
.meter-val {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}
.meter-val small {
  font-size: 0.7rem;
  color: var(--sena-verde);
  margin-left: 2px;
}
.meter-bar {
  height: 4px;
  background: var(--borde);
  margin-top: 8px;
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: var(--sena-verde);
  transition: width 0.4s ease;
}

/* ==========================================================================
   MAPA DE PUESTOS ELÉCTRICOS (REGLA DE 8 COLUMNAS AJUSTADAS)
   ========================================================================== */
.map-instruction {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  margin-bottom: 1.5rem;
}

.map-and-lights-container {
  display: flex;
  gap: 20px;
}

.room-map-wrapper {
  width: 100%;
  overflow: hidden;
}

.room-map {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

@media (min-width: 992px) {
  .room-map {
    grid-template-columns: repeat(9, 1fr);
    max-width: 100%;
  }
}

.map-node {
  aspect-ratio: 1 / 1;
  max-width: 85px; /* Restricción perimetral para evitar distorsión en monitores anchos */
  width: 100%;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 0.25rem;
  cursor: pointer;
  color: var(--texto-secundario);
  transition: all 0.2s ease;
  font-family: inherit;
  border-style: solid;
}
.map-node:hover:not(:disabled) {
  background: var(--fondo-tarjetas);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.map-node:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.map-node small {
  font-size: 0.5rem;
  font-weight: 700;
}
.node-bolt {
  font-size: 1rem;
  opacity: 0.5;
}
.node-watts {
  font-size: 0.6rem;
  font-weight: 700;
  font-family: monospace;
}

.map-node.node-on {
  background: rgba(57, 169, 0, 0.06);
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}
.map-node.node-on .node-bolt {
  color: var(--sena-verde);
  opacity: 1;
}

/* COMPONENTES DE INFRAESTRUCTURA LATERAL Y BOTONERA A 3 COLUMNAS */
.btn-wide-action {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  background: var(--fondo-app);
  color: var(--sena-azul-oscuro);
  font-weight: 800;
  font-size: 0.85rem;
  border: 1px solid var(--borde);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.btn-wide-action:hover {
  background: #f8fafc;
}
.alert-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.alert-badge {
  background: var(--fondo-app);
  color: var(--texto-secundario);
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid var(--borde);
}
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}
.alert-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 12px;
  gap: 12px;
  border: 2px solid transparent;
}
.alert-warning {
  background: #fefce8;
  border-color: #fef08a;
}
.alert-warning .alert-icon {
  color: #ca8a04;
  font-size: 1.2rem;
}
.alert-warning .alert-msg {
  color: #854d0e;
}
.alert-success {
  background: #f0fdf4;
  border-color: #bbf7d0;
}
.alert-success .alert-icon {
  color: #16a34a;
  font-size: 1.2rem;
}
.alert-success .alert-msg {
  color: #166534;
}
.alert-content {
  flex: 1;
}
.alert-msg {
  margin: 0 0 4px 0;
  font-size: 0.75rem;
  font-weight: 700;
}
.alert-meta {
  font-size: 0.65rem;
  color: var(--texto-secundario);
  text-transform: uppercase;
}
.alert-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e2e8f0;
}
.alert-check.active {
  color: #16a34a;
}
.btn-show-more {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--sena-azul-oscuro);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.5rem;
}
.btn-show-more:hover {
  text-decoration: underline;
}

/* TABLA GENERAL DE ALUMNOS */
.dash-footer-table {
  grid-column: 1 / -1;
}
.table-responsive-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 0.5rem;
}
.apprentices-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 450px;
}
.apprentices-table th {
  padding: 10px 8px;
  border-bottom: 2px solid var(--fondo-app);
  font-size: 0.65rem;
  color: var(--texto-secundario);
  text-transform: uppercase;
  text-align: left;
}
.apprentices-table td {
  padding: 12px 8px;
  border-bottom: 1px solid var(--fondo-app);
  font-size: 0.75rem;
  vertical-align: middle;
}
.table-user-info strong {
  color: var(--sena-azul-oscuro);
  font-weight: 600;
  display: block;
}
.table-user-info small {
  color: var(--texto-secundario);
  font-size: 0.65rem;
}
.status-green {
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.6rem;
}
.status-gray {
  color: var(--texto-secundario);
  background: var(--fondo-app);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.6rem;
}
.time-cell {
  font-family: monospace;
  color: var(--texto-secundario);
}

.actions-cell {
  display: flex;
  gap: 6px;
}
.btn-table {
  border: 1px solid var(--borde);
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  background: var(--fondo-app);
  color: var(--texto-secundario);
  transition: all 0.2s;
}
.btn-table:hover {
  color: var(--sena-azul-oscuro);
  background: var(--borde);
}

/* ==========================================================================
   ZONA PROYECTOR DE QR (ABS-EXTRACTED TO QrModal.vue)
   ========================================================================== */

/* ==========================================================================
   ESTILOS DEL TECLADO NUMÉRICO (PIN MODAL)
   ========================================================================== */
.pin-modal {
  max-width: 360px;
  padding: 2rem 1.5rem;
}
.pin-instruction {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0.5rem 0 1.5rem;
  line-height: 1.4;
}

.pin-display {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 16px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  letter-spacing: 0.1em;
  transition: all 0.3s ease;
}

.pin-display.is-loading {
  font-size: 1rem;
  letter-spacing: normal;
  color: var(--sena-verde);
  background: rgba(57, 169, 0, 0.1);
  border-color: var(--sena-verde);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 1.5rem;
  transition: opacity 0.3s ease;
}

.btn-key {
  aspect-ratio: 1 / 1;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-key:hover {
  background: var(--sena-blanco);
  border-color: var(--sena-verde);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 48, 64, 0.05);
}

.btn-key:active {
  transform: translateY(0);
}

.action-key {
  font-size: 1.1rem;
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.05);
  border-color: transparent;
}
.action-key:hover {
  background: #e53e3e;
  color: white;
  border-color: #e53e3e;
}

.submit-key {
  font-size: 1.2rem;
  background: var(--sena-verde);
  color: white;
  border-color: var(--sena-verde-oscuro);
}
.submit-key:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
}
.submit-key:disabled {
  background: var(--borde);
  border-color: var(--borde);
  color: var(--texto-secundario);
  cursor: not-allowed;
  opacity: 0.5;
}

/* ==========================================
   ESTILOS DE LAS TARJETAS DE TIEMPO
   ========================================== */
.time-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0 30px 0;
}

.time-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: var(--fondo-tarjetas);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border-left: 5px solid var(--borde);
}

/* Modificadores por color */
.start-card { border-left-color: var(--sena-verde-oscuro); }
.end-card { border-left-color: #f43f5e; }
.extra-card { border-left-color: var(--sena-amarillo); }

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

/* AQUÍ DOMAMOS LOS TAMAÑOS DE LOS ÍCONOS */
.icon-box svg {
  width: 24px !important;
  height: 24px !important;
}

.icon-box font-awesome-icon {
  font-size: 1.5rem;
}

/* Colores de fondo y texto de los íconos */
.start-card .icon-box { background-color: #d1fae5; color: #059669; }
.end-card .icon-box { background-color: #ffe4e6; color: #e11d48; }
.extra-card .icon-box { background-color: #fef3c7; color: #d97706; }

.info-box {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  margin: 0 0 4px 0;
  font-weight: 500;
}

.card-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--texto-principal);
  margin: 0;
}

/* Parche de seguridad para el botón de apagado gigante */
.power-switch svg {
  width: 1.5rem;
  height: 1.5rem;
}
</style>
