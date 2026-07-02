<script setup>
import { ref } from "vue";
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

// Máquina de estados principal para la vista (1: Access, 2: Select Ficha, 3: Dashboard)
const currentStep = ref(1);

// Estados de los modales
const qrProjected = ref(false);
const showPinModal = ref(false);
const isValidatingPin = ref(false);
const showFirmaModal = ref(false);

const aprendizSeleccionadoParaFirmar = ref({ name: "", doc: "" });
const fichaActiva = ref(localStorage.getItem('fichaActiva') || "Sin Ficha"); 

// === Control de Flujo de la Tablet ===
const handleNfcSuccess = () => {
  toast.success("Credencial NFC validada. Instructor reconocido.");
  currentStep.value = 2; // Avanzamos a Seleccionar Ficha
};

const handleFichaSelected = (ficha) => {
  fichaActiva.value = ficha.numero;
  currentStep.value = 3; // Avanzamos al Dashboard
};

const handleGoBack = () => {
  currentStep.value = 1; // Volvemos al inicio
};

// === Control de Modales (Se pueden llamar desde cualquier paso) ===
const openQrModal = (apprentice = null) => {
  qrProjected.value = true;
};

const openPinModal = (apprentice = null) => {
  showPinModal.value = true;
};

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
      
      if (data.accion === "INGRESO") {
        // Primera vez: Sólo registramos ingreso sin firma
        toast.success(`¡Bienvenido ${data.nombre_aprendiz || "Aprendiz"}! Ingreso registrado.`);
        showPinModal.value = false;
      } else {
        // Segunda vez (SALIDA): Exigimos la firma
        aprendizSeleccionadoParaFirmar.value = {
          name: data.nombre_aprendiz || "Aprendiz",
          doc: data.documento_aprendiz
        };
        showPinModal.value = false;
        showFirmaModal.value = true;
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
    <!-- Renderizado Condicional del Flujo -->
    <TabletAccess 
      v-if="currentStep === 1" 
      @nfc-success="handleNfcSuccess"
      @open-qr="openQrModal"
      @open-pin="openPinModal"
    />

    <TabletSelectFicha 
      v-else-if="currentStep === 2"
      @ficha-selected="handleFichaSelected"
      @go-back="handleGoBack"
    />

    <TabletDashboard 
      v-else-if="currentStep === 3"
      @open-firma="openFirmaModal"
      @open-qr="openQrModal"
      @open-pin="openPinModal"
    />

    <!-- Modales Globales -->
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
</style>
