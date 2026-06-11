<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
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

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
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

// --- ESTADOS DE LA SESIÓN (Traídos desde el Selector de Fichas) ---
// Simplemente leemos la memoria, ya no necesitamos hacer consultas al backend aquí
const ambienteSeleccionadoId = ref(localStorage.getItem('ambienteActivoId') || "");
const nombreAmbienteSeleccionado = ref(localStorage.getItem('ambienteActivoNombre') || "Ambiente no definido");

// --- ESTADOS DE DATOS REALES Y SESIÓN ---
// Estos se cargan inmediatamente de la memoria del navegador
const fichaActiva = ref(localStorage.getItem('fichaActiva') || "Sin Ficha");
const nombreInstructor = ref(localStorage.getItem('nombreInstructor') || "Instructor");
const nombrePrograma = ref(localStorage.getItem('nombrePrograma') || "Programa no definido");

// Estos arrancan vacíos porque se llenan tras consultar la API en el onMounted
const apprentices = ref([]); 
const isLoading = ref(true);

// CONTROLADORES DE INTERCEPCIÓN PARA LA FIRMA
const showFirmaModal = ref(false);
const aprendizSeleccionadoParaFirmar = ref({ name: "", doc: "" });

// RELOJES Y TIEMPOS
const horaInicio = ref(localStorage.getItem('horaInicio') || '--:--');
const horaFin = ref(localStorage.getItem('horaFin') || '--:--');
const tiempoExtra = ref(localStorage.getItem('tiempoExtra') || '0 min');

// --- ESTADOS DE ALERTAS Y MODALES ---
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

const roomNodes = ref(
  Array.from({ length: 16 }, (_, i) => ({
    id: i + 1,
    energized: false,
    load: Math.floor(Math.random() * 90) + 10,
  }))
);

// ==========================================
// 📡 TELEPATÍA DEL QR (1 a 1)
// ==========================================
let qrListenerInterval = null;

// Observa cuando el instructor abre o cierra el QR
watch(qrProjected, (newVal) => {
  if (newVal) {
    // Si el QR está proyectado, la tablet pregunta cada 1.5 segundos si alguien ya lo quemó
    qrListenerInterval = setInterval(async () => {
      const sesionId = localStorage.getItem('sesionActivaId');
      if (!sesionId) return;

      try {
        const res = await fetch(`${BASE_URL}/api/asistencia/ultimo-escaneo/${sesionId}`);
        if (res.ok) {
          const data = await res.json();
          
          if (data.documento) {
            // ¡Alguien lo escaneó! Buscamos quién fue
            const aprendiz = apprentices.value.find(a => a.doc === data.documento);
            
            if (aprendiz) {
              qrProjected.value = false; // Cerramos el QR automáticamente

              if (data.accion === "ingreso_exitoso") {
                aprendiz.status = "present";
                aprendiz.lastSeen = "En Clase"; // 🟢 Exactamente como lo pediste
                toast.success(`¡${aprendiz.name} ha registrado su ingreso!`);
              } 
              else if (data.accion === "requiere_firma") {
                aprendizSeleccionadoParaFirmar.value = { name: aprendiz.name, doc: aprendiz.doc };
                showFirmaModal.value = true; // 🟢 Saltamos a la firma
              }
            }
          }
        }
      } catch (error) {
        // Silencio para no molestar la UI si hay latencia
      }
    }, 1500); 
  } else {
    // Si cierran el QR, apagamos el oyente
    if (qrListenerInterval) clearInterval(qrListenerInterval);
  }
});


// ==========================================
// 🚀 LÓGICA DE ASISTENCIA Y FIRMAS (PIN / NFC)
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
        aprendizEncontrado.lastSeen = "En Clase"; // Homologado con el QR
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
    toast.error("Error de respuesta del nodo central.");
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
      localStorage.setItem('salidaHabilitada', 'true'); // 🟢 NUEVO: Persistir estado de salida
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
      toast.error("Falló el empaquetado del registro en la memoria del servidor.");
    }
  } catch (error) {
    console.error(error);
    toast.error("Error de red al procesar la firma táctil.");
  }
};

const solicitarReporteAsistenciaPDF = async (idDeSesionCerrada) => {
  toast.info("Ensamblando PDF con las firmas...");
  try {
    const correo = localStorage.getItem('instructorEmail') || "ferley_tobon@soy.sena.edu.co";
    const ficha = localStorage.getItem('fichaActiva') || "3465773";
    const programa = localStorage.getItem('nombrePrograma') || "Analisis y Desarrollo de Software";
    const instructor = localStorage.getItem('instructorName') || "Ferley Tobon";

    const response = await fetch(`${BASE_URL}/api/asistencia/generar-reporte`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sesion_id: idDeSesionCerrada,
        numero_ficha: ficha,
        nombre_programa: programa,
        nombre_instructor: instructor,
        correo_destino: correo,
        competencia: "", 
        resultado_aprendizaje: ""
      })
    });

    if (response.ok) {
      toast.success("¡PDF generado en el servidor con éxito!");
    } else {
      toast.warning("Fallo al empaquetar el PDF en el servidor cloud.");
    }
  } catch (error) {
    toast.error("Fallo de red al solicitar el reporte final.");
  }
};

// ==========================================
// 🔌 OPERACIONES IOT (AULA)
// ==========================================
const toggleMasterPower = async () => {
  // 🟢 1. EL CANDADO ESTRICTO: Se valida ANTES de tocar los botones
  if (!isPowerOn.value && !ambienteSeleccionadoId.value) {
    toast.warning("¡Alerta! No se detectó un ambiente enlazado.");
    // Como ya no hay modal aquí, lo mandamos a la pantalla de selección
    router.push("/route-selector"); 
    return; // Cortamos la ejecución
  }

  // 🟢 2. CAMBIAMOS EL ESTADO VISUAL DE LA PANTALLA
  isPowerOn.value = !isPowerOn.value;
  roomNodes.value.forEach((node) => { node.energized = isPowerOn.value; });

  // 🟢 3. SI EL INSTRUCTOR ENCENDIÓ EL AULA
  if (isPowerOn.value) {
    salidaHabilitada.value = false;
    toast.info("Energizando aula y registrando inicio de clase...");
    
    try {
      const emailInstructor = localStorage.getItem('instructorEmail') || "";
      
      // Enviamos la petición usando el ID del ambiente correcto
      const responseSesion = await fetch(`${BASE_URL}/api/sesiones/iniciar?ficha=${fichaActiva.value}&email=${emailInstructor}&ambiente_id=${ambienteSeleccionadoId.value}`, { method: "POST" });

      if (responseSesion.ok) {
        const data = await responseSesion.json();
        localStorage.setItem('sesionActivaId', data.sesion_id);
        const fechaEntrada = new Date(data.hora_entrada);
        horaInicio.value = fechaEntrada.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        
        // Guardamos estado inicial de clase
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
      // ⚠️ ROLLBACK: Si el backend falla, apagamos el botón en la pantalla
      isPowerOn.value = false;
      roomNodes.value.forEach((node) => { node.energized = false; });
      toast.error("Error de conexión con Dataverse. Reintente encender.");
    }
  
  // 🟢 4. SI EL INSTRUCTOR APAGÓ EL AULA
  } else {
    toast.info("Apagando aula y registrando salida...");
    
    try {
      const sesionId = localStorage.getItem('sesionActivaId') || "";
      if (!sesionId) throw new Error("No hay sesión ID");

      const responseCierre = await fetch(`${BASE_URL}/api/sesiones/finalizar?sesion_id=${sesionId}`, { method: "POST" });

      if (responseCierre.ok) {
        const dataCierre = await responseCierre.json();
        
        // Disparamos la generación del PDF en segundo plano
        await solicitarReporteAsistenciaPDF(sesionId);

        const fechaSalida = new Date(dataCierre.hora_salida);
        horaFin.value = fechaSalida.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        tiempoExtra.value = dataCierre.tiempo_extra;

        // Guardamos todo en memoria para que no se pierda si recarga
        localStorage.setItem('isPowerOn', 'false');
        localStorage.setItem('salidaHabilitada', 'false');
        localStorage.setItem('horaFin', horaFin.value);
        localStorage.setItem('tiempoExtra', tiempoExtra.value);
        localStorage.removeItem('sesionActivaId'); 

        salidaHabilitada.value = false;
        toast.success("¡Aula APAGADA y sesión finalizada!");
      } else {
         throw new Error("El servidor rechazó el cierre de sesión");
      }
    } catch (error) {
      // ⚠️ ROLLBACK: Si falla el cierre, volvemos a encender el botón
      isPowerOn.value = true;
      roomNodes.value.forEach((node) => { node.energized = true; });
      toast.error("Error al cerrar la sesión en Dataverse.");
    }
  }
};

const toggleNodePower = (node) => {
  node.energized = !node.energized;
  isPowerOn.value = roomNodes.value.some((n) => n.energized);
};

// ==========================================
// 🎛️ CONTROLADORES DE BOTONES (QR, PIN, NFC)
// ==========================================

const projectQR = () => {
  if (!isPowerOn.value) {
    toast.warning("Debes energizar el aula antes de proyectar el código QR.");
    return;
  }
  // Cambia el estado de proyectado a no proyectado y viceversa
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
  if (nfcScanning.value) {
    toast.info("Lector NFC activado. Esperando tarjetas...");
  } else {
    toast.info("Lector NFC desactivado.");
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

const cerrarSesion = () => {
  // Verificamos si hay una clase activa antes de dejarlo salir (opcional, por seguridad)
  if (isPowerOn.value) {
    toast.warning("Primero debes apagar el aula y finalizar la sesión de clase actual.");
    return;
  }

  // 🔥 LIMPIEZA ABSOLUTA de la memoria del navegador
  localStorage.clear();
  
  toast.success("Sesión cerrada correctamente. Volviendo al inicio.");
  router.push("/route-selector"); // Redirige al selector de roles o login
};

// --- CICLO DE VIDA ---
onMounted(async () => {
  if (!hasRole(["instructor", "dinamizador"])) {
    toast.error("Acceso denegado. Se requiere perfil de Instructor.");
    router.push("/route-selector");
    return;
  }

  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString();
  }, 1000);

  fichaActiva.value = localStorage.getItem('fichaActiva') || "Sin Ficha";
  nombrePrograma.value = localStorage.getItem('nombrePrograma') || "Programa no definido";
  nombreInstructor.value = localStorage.getItem('nombreInstructor') || "Instructor";

  if (fichaActiva.value === "Sin Ficha") {
    toast.error("No hay una ficha activa. Redirigiendo...");
    router.push("/route-selector");
    return;
  }

  // Si la página se refrescó, mantener el aula encendida visualmente
  if (localStorage.getItem('sesionActivaId')) {
    isPowerOn.value = true;
  }

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
  } catch (error) {
    console.error("Error consultando aprendices:", error);
    toast.warning("El aula está lista, pero no hay aprendices registrados.");
  } finally {
    isLoading.value = false;
  }
});

onUnmounted(() => {
  if (qrListenerInterval) clearInterval(qrListenerInterval);
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
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <div class="info-box">
          <p class="card-title">Hora de Inicio</p>
          <p class="card-value">{{ horaInicio }}</p>
        </div>
      </div>

      <div class="time-card end-card">
        <div class="icon-box">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
        </div>
        <div class="info-box">
          <p class="card-title">Hora de Cierre</p>
          <p class="card-value">{{ horaFin }}</p>
        </div>
      </div>

      <div class="time-card extra-card">
        <div class="icon-box">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
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
          <button class="btn-action qr" @click="qrProjected = true" :disabled="!isPowerOn">
            <font-awesome-icon icon="fa-solid fa-qrcode" />
            <span>MOSTRAR QR</span>
          </button>

          <button class="btn-action pin" @click="showPinModal = true" :disabled="!isPowerOn">
            <font-awesome-icon icon="fa-solid fa-lock" />
            <span>DIGITAR PIN</span>
          </button>

          <button v-if="isPowerOn" class="btn-action" :class="{ 'btn-active': salidaHabilitada }" style="background-color: #f39c12; color: white;" @click="habilitarSalidaClase" :disabled="salidaHabilitada">
            <font-awesome-icon icon="fa-solid fa-flag-checkered" />
            <span>{{ salidaHabilitada ? "SALIDAS ACTIVAS" : "FINALIZAR CLASE" }}</span>
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

    <QrModal v-if="qrProjected" :fichaActiva="fichaActiva" @close="qrProjected = false" />
    <PinModal v-if="showPinModal" :isLoading="isValidatingPin" @close="showPinModal = false" @submit="procesarValidacionPin" />
    <FirmaModal v-if="showFirmaModal" :apprenticeName="aprendizSeleccionadoParaFirmar.name" @close="showFirmaModal = false" @save="procesarRegistroFirmaAsistencia" />
    <ProfileModal v-if="activeModal === 'profile'" :apprentice="selectedApprentice" @close="closeModal" />
    <AttendanceModal v-if="activeModal === 'attendance'" :apprentice="selectedApprentice" @close="closeModal" />
    <ExitModal v-if="activeModal === 'exit'" :apprentice="selectedApprentice" @close="closeModal" @confirm="handleExitConfirm" />
 
    <div v-if="showAmbienteSelector" class="modal-overlay" style="z-index: 9999; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.85); position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;">
      <div class="modal-content" style="background: white; padding: 40px; border-radius: 12px; width: 450px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
        <img src="@/assets/LogoSena.png" alt="SENA" style="width: 90px; margin-bottom: 20px;" />
        <h2 style="color: #333; margin-bottom: 10px; font-size: 22px;">Configuración de Espacio</h2>
        <p style="color: #666; margin-bottom: 25px; line-height: 1.5;">Por favor, indica en qué ambiente físico vas a impartir esta sesión de formación para enlazar el hardware.</p>
        
        <select v-model="ambienteSeleccionado" style="width: 100%; padding: 14px; border-radius: 8px; border: 2px solid #e0e0e0; margin-bottom: 25px; font-size: 16px; outline: none; transition: border 0.3s;">
          <option disabled value="">Selecciona un ambiente de la lista...</option>
          <option v-for="amb in ambientesDisponibles" :key="amb.id" :value="amb.id">
            {{ amb.nombre }}
          </option>
        </select>

        <button @click="confirmarAmbiente" style="width: 100%; padding: 14px; background: #39a900; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; transition: background 0.3s;" onmouseover="this.style.background='#2d8500'" onmouseout="this.style.background='#39a900'">
          <font-awesome-icon icon="fa-solid fa-link" style="margin-right: 8px;" />
          ENLAZAR AMBIENTE
        </button>
      </div>
    </div>
 </div>
</template>

<style scoped>
/* Tu CSS original impecable */
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

@media (min-width: 992px) {
  .dashboard-shell { padding: 1.5rem; }
  .dash-header { flex-direction: row; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; }
  .header-left { flex-direction: row; align-items: center; gap: 2.5rem; }
  .logo-sena { height: 44px; } .logo-volt { height: 40px; }
  .environment-badge h1 { font-size: 1.4rem; }
  .power-master-box { background: transparent; border: none; padding: 0; gap: 1.5rem; }
  .dash-grid { grid-template-columns: 1fr 380px; display: grid; }
}

.dash-col { display: flex; flex-direction: column; gap: 1.5rem; }
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

.map-node { aspect-ratio: 1 / 1; max-width: 85px; width: 100%; background: var(--fondo-app); border: 1px solid var(--borde); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 0.25rem; cursor: pointer; color: var(--texto-secundario); transition: all 0.2s ease; font-family: inherit; }
.map-node:hover:not(:disabled) { background: #ffffff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
.map-node:disabled { opacity: 0.6; cursor: not-allowed; }
.map-node small { font-size: 0.5rem; font-weight: 700; }
.node-bolt { font-size: 1rem; opacity: 0.5; }
.node-watts { font-size: 0.6rem; font-weight: 700; font-family: monospace; }
.map-node.node-on { background: rgba(57, 169, 0, 0.06); border-color: var(--sena-verde); color: var(--sena-verde-oscuro); }
.map-node.node-on .node-bolt { color: var(--sena-verde); opacity: 1; }

.actions-group { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.btn-action { padding: 1rem 0.5rem; border-radius: 12px; border: 1px solid var(--borde); background: var(--fondo-tarjetas); color: var(--texto-secundario); display: flex; flex-direction: column; align-items: center; gap: 6px; font-weight: 700; font-size: 0.65rem; cursor: pointer; transition: all 0.2s ease; }
.btn-action:hover { background: var(--fondo-app); }
.btn-action.nfc.btn-active { background: var(--sena-azul-oscuro); color: var(--sena-blanco); border-color: var(--sena-azul-oscuro); }
.btn-action.qr.btn-active { background: var(--sena-verde); color: var(--sena-blanco); border-color: var(--sena-verde-oscuro); }
.btn-action.pin:hover { border-color: var(--sena-amarillo); color: var(--sena-azul-oscuro); background: rgba(253, 195, 0, 0.1); }

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

.time-cards-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0 30px 0; }
.time-card { display: flex; align-items: center; padding: 16px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #ccc; }
.start-card { border-left-color: #10b981; } .end-card { border-left-color: #f43f5e; } .extra-card { border-left-color: #f59e0b; }
.icon-box { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0; }
.icon-box svg { width: 24px !important; height: 24px !important; }
.start-card .icon-box { background-color: #d1fae5; color: #059669; }
.end-card .icon-box { background-color: #ffe4e6; color: #e11d48; }
.extra-card .icon-box { background-color: #fef3c7; color: #d97706; }
.info-box { display: flex; flex-direction: column; }
.card-title { font-size: 0.85rem; color: #6b7280; margin: 0 0 4px 0; font-weight: 500; }
.card-value { font-size: 1.25rem; font-weight: 700; color: #1f2937; margin: 0; }
.power-switch svg { width: 1.5rem; height: 1.5rem; }
</style>
