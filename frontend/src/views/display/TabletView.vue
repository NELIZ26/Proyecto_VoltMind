<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useToast } from "vue-toastification";

// Subcomponentes del Flujo de la Tablet
import TabletAccess from "@/components/tablet/TabletAccess.vue";
import TabletSelectFicha from "@/components/tablet/TabletSelectFicha.vue";
import TabletDashboard from "@/components/tablet/TabletDashboard.vue";

// Modales del sistema
import PinKeypadModal from "@/components/PinKeypadModal.vue";
import QrModal from "@/components/QrModal.vue";
import FirmaModal from "@/components/FirmaModal.vue";

const toast = useToast();

// 🟢 MÁQUINA DE ESTADOS (0: Setup, 1: Access, 2: Select Ficha, 3: Dashboard)
const currentStep = ref(0);

// Estados de la Tablet
const ambienteId = ref("");
const ambienteNombre = ref("");
const ambientesDisponibles = ref([]);
const isLoadingAmbientes = ref(false);

const qrProjected = ref(false);
const showPinModal = ref(false);
const isValidatingPin = ref(false);
const showFirmaModal = ref(false);

const aprendizSeleccionadoParaFirmar = ref({ name: "", doc: "" });
const fichaActiva = ref(localStorage.getItem('fichaActiva') || "Sin Ficha"); 

// ==========================================
// ⚙️ PASO 0: CONFIGURACIÓN INICIAL DEL KIOSCO
// ==========================================
const cargarAmbientes = async () => {
  isLoadingAmbientes.value = true;
  try {
    const res = await fetch("http://localhost:8000/api/sesiones/ambientes");
    if (res.ok) {
      ambientesDisponibles.value = await res.json();
    } else {
      toast.error("Error al cargar los ambientes de la base de datos.");
    }
  } catch (error) {
    console.error("Error consultando ambientes:", error);
    toast.error("Servidor desconectado.");
  } finally {
    isLoadingAmbientes.value = false;
  }
};

const guardarConfiguracionKiosko = () => {
  if (!ambienteId.value) {
    toast.warning("Debes seleccionar un ambiente de formación.");
    return;
  }
  
  // Guardamos la configuración física de esta tablet
  const ambienteSeleccionado = ambientesDisponibles.value.find(a => a.id === ambienteId.value);
  ambienteNombre.value = ambienteSeleccionado.nombre;
  
  localStorage.setItem('kiosko_ambiente_id', ambienteId.value);
  localStorage.setItem('kiosko_ambiente_nombre', ambienteNombre.value);
  
  toast.success(`Kiosko configurado exitosamente para: ${ambienteNombre.value}`);
  
  // Encendemos el radar y pasamos a la pantalla de espera
  conectarWebSocket();
  currentStep.value = 1;
};

// ==========================================
// 📡 CEREBRO WEBSOCKET (EL ESPEJO)
// ==========================================
let ws = null;

const conectarWebSocket = () => {
  if (!ambienteId.value) return;

  // 🟢 CORRECCIÓN 403: Usamos localhost en lugar de 127.0.0.1 para evitar bloqueos CORS
  ws = new WebSocket(`ws://localhost:8000/api/ws/ambiente/${ambienteId.value}`);

  ws.onopen = () => {
    console.log(`[Kiosko] 🟢 Conectado y escuchando al ambiente ${ambienteNombre.value}`);
  };

  ws.onmessage = (event) => {
    const mensaje = JSON.parse(event.data);
    console.log("[Kiosko] 📩 Orden del servidor:", mensaje);

    if (mensaje.tipo === "SESION_INICIADA") {
      toast.success("Aula energizada remotamente. Modo ingreso activado.");
      currentStep.value = 3; 
    } 
    else if (mensaje.tipo === "SESION_FINALIZADA") {
      toast.info("El instructor finalizó la clase.");
      currentStep.value = 1;
    }
    else if (mensaje.tipo === "CAMBIO_ESTADO" && mensaje.nuevo_estado === "MODO_SALIDA") {
      toast.warning("Modo Salida Activado. Aprendices, registren su firma.");
    }
    else if (mensaje.tipo === "FORZAR_FIRMA") {
      openFirmaModal({ name: mensaje.nombre_aprendiz, doc: mensaje.aprendiz_id });
    }
  };

  ws.onclose = () => {
    console.warn("[Kiosko] 🔴 Conexión perdida. Reconectando en 3s...");
    setTimeout(conectarWebSocket, 3000);
  };
};

// ==========================================
// 🚀 CICLO DE VIDA
// ==========================================
onMounted(() => {
  // ¿Esta tablet ya fue configurada antes?
  const ambienteGuardado = localStorage.getItem('kiosko_ambiente_id');
  const nombreGuardado = localStorage.getItem('kiosko_ambiente_nombre');

  if (ambienteGuardado) {
    // Si ya sabe qué aula es, salta el Paso 0 y enciende el radar
    ambienteId.value = ambienteGuardado;
    ambienteNombre.value = nombreGuardado;
    currentStep.value = 1;
    conectarWebSocket();
  } else {
    // Si es una tablet nueva, pide configuración
    currentStep.value = 0;
    cargarAmbientes();
  }
});

onUnmounted(() => {
  if (ws) ws.close();
});

// === Control de Flujo de la Tablet ===
const handleNfcSuccess = () => {
  toast.success("Credencial NFC validada. Instructor reconocido.");
  currentStep.value = 2; 
};

const handleFichaSelected = async (ficha) => {
  fichaActiva.value = ficha.numero;
  
  localStorage.setItem('fichaActiva', ficha.numero);
  // Rescatamos los datos locales de la Tablet
  const emailInstructor = localStorage.getItem('instructorEmail');
  const ambienteKiosko = localStorage.getItem('kiosko_ambiente_id'); // El que configuraste en el Paso 0

  toast.info("Energizando aula y registrando clase...");

  try {
    // 1. Disparamos la creación de la sesión en FastAPI (Esto activa el WebSocket para el Dashboard)
    const responseSesion = await fetch(`http://localhost:8000/api/sesiones/iniciar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ficha: fichaActiva.value,
        email: emailInstructor,
        ambiente_id: ambienteKiosko
      })
    });

    if (responseSesion.ok) {
      const data = await responseSesion.json();
      
      // Guardamos la sesión en el Kiosco
      localStorage.setItem('sesionActivaId', data.sesion_id);
      localStorage.setItem('isPowerOn', 'true');
      localStorage.setItem('horaInicio', new Date(data.hora_entrada).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }));

      // 2. Encendemos los relés IoT físicos
      await fetch(`http://localhost:8000/api/iot/master`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ estado: "1" })
      });

      toast.success("¡Aula ENERGIZADA desde el Kiosko!");
      
      // 3. Ahora sí, avanzamos visualmente a la pantalla de aprendices
      currentStep.value = 3; 
    } else {
      toast.error("Falló el registro de la sesión en la base de datos.");
    }
  } catch (error) {
    console.error("Error encendiendo aula:", error);
    toast.error("Error de conexión con el nodo central.");
  }
};

const handleGoBack = () => {
  currentStep.value = 1; 
};

// === Control de Modales ===
const openQrModal = () => qrProjected.value = true;
const openPinModal = () => showPinModal.value = true;

const openFirmaModal = (apprentice) => {
  if (apprentice) {
    aprendizSeleccionadoParaFirmar.value = {
      name: apprentice.name,
      doc: apprentice.id || apprentice.doc
    };
    showFirmaModal.value = true;
  }
};

const handlePinSubmit = async (pinValue) => {
  if (pinValue.length !== 4) {
    toast.error("El PIN debe tener exactamente 4 dígitos.");
    return;
  }
  isValidatingPin.value = true;
  
  try {
    const sesionId = localStorage.getItem('sesionActivaId') || "";
    const response = await fetch(`http://localhost:8000/api/asistencia/validar-pin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        pin: pinValue,
        sesion_id: sesionId
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log("📦 RESPUESTA DE DATAVERSE / REDIS:", data);
      
      // 🟢 RUTA 1: ES UN INSTRUCTOR
      if (data.rol === "instructor" && data.accion === "activar_aula") {
        toast.success(data.mensaje); 
        // ⚠️ Asegúrate de que el backend está retornando el correo en "identificador"
        localStorage.setItem("instructorEmail", data.identificador); 
        showPinModal.value = false;
        currentStep.value = 2; // Avanza a seleccionar ficha
      } 
      // 🟡 RUTA 2: APRENDIZ (INGRESO)
      else if (data.accion === "ingreso_exitoso") {
        toast.success(`¡Bienvenido! Ingreso registrado.`);
        showPinModal.value = false;
      } 
      // 🔴 RUTA 3: APRENDIZ (SALIDA/FIRMA)
      else if (data.accion === "requiere_firma") {
        aprendizSeleccionadoParaFirmar.value = {
          name: data.nombre_aprendiz || "Aprendiz",
          doc: data.documento_aprendiz
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
    toast.error("Error de conexión con VoltMind central.");
  } finally {
    isValidatingPin.value = false;
  }
};

const procesarRegistroFirmaAsistencia = async (base64Signature) => {
  const sesionId = localStorage.getItem('sesionActivaId') || "";
  
  try {
    const response = await fetch(`http://localhost:8000/api/asistencia/guardar-firma`, {
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
      toast.success(`¡Asistencia y firma registradas para ${aprendizSeleccionadoParaFirmar.value.name}!`);
      showFirmaModal.value = false;
    } else {
      toast.error("Falló el empaquetado del registro en la memoria del servidor.");
    }
  } catch (error) {
    console.error(error);
    toast.error("Error de red al procesar la firma táctil.");
  }
};
</script>

<template>
  <div class="tablet-host-view">
    
    <div v-if="currentStep === 0" class="setup-container">
      <div class="setup-card">
        <font-awesome-icon icon="fa-solid fa-microchip" class="setup-icon" />
        <h2>Configuración de Terminal</h2>
        <p>Asigna esta tablet a un ambiente físico para vincularla a la red VoltMind.</p>
        
        <div v-if="isLoadingAmbientes" class="loading-state">
          Buscando ambientes en Dataverse...
        </div>
        
        <div v-else class="form-group">
          <select v-model="ambienteId" class="form-select">
            <option value="" disabled>Seleccione el aula actual...</option>
            <option v-for="amb in ambientesDisponibles" :key="amb.id" :value="amb.id">
              {{ amb.nombre }}
            </option>
          </select>
          <button @click="guardarConfiguracionKiosko" class="btn-setup">Vincular Kiosko</button>
        </div>
      </div>
    </div>

    <TabletAccess 
      v-else-if="currentStep === 1"
      :ambienteNombre="ambienteNombre"
      @nfc-success="handleNfcSuccess"
      @open-qr="openQrModal"
      @open-pin="openPinModal"
    />

    <TabletSelectFicha 
      v-else-if="currentStep === 2"
      :ambienteNombre="ambienteNombre"
      @ficha-selected="handleFichaSelected"
      @go-back="handleGoBack"
    />

    <TabletDashboard 
      v-else-if="currentStep === 3"
      :ambienteNombre="ambienteNombre"
      @open-firma="openFirmaModal"
      @open-qr="openQrModal"
      @open-pin="openPinModal"
    />

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
  </div>
</template>

<style scoped>
.tablet-host-view {
  width: 100%;
  min-height: 100vh;
  background-color: var(--fondo-app);
}

/* Estilos básicos para la pantalla de configuración */
.setup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f4f6f9;
}
.setup-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
}
.setup-icon {
  font-size: 3rem;
  color: #39a900;
  margin-bottom: 20px;
}
.form-select {
  width: 100%;
  padding: 12px;
  margin: 20px 0;
  border-radius: 6px;
  border: 1px solid #ddd;
}
.btn-setup {
  width: 100%;
  padding: 12px;
  background-color: #39a900;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.btn-setup:hover {
  background-color: #2d8a00;
}
</style>