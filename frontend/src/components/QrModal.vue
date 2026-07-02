<script setup>
import { ref, watch, onUnmounted } from 'vue';
import QrcodeVue from 'qrcode.vue';

const props = defineProps({
  show: { type: Boolean, required: true },
  fichaActiva: { type: String, required: true }
});

const emit = defineEmits(['close']);
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const qrData = ref("GENERANDO..."); // Aquí guardamos el token real
let refreshInterval = null;

// 1. Función para pedirle un QR nuevo a Python (Tu código)
const fetchNewQr = async () => {
  try {
    const sesionId = localStorage.getItem('sesionActivaId');
    if (!sesionId) return;

    const response = await fetch(`${BASE_URL}/api/asistencia/generar-qr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sesion_id: sesionId })
    });

    if (response.ok) {
      const data = await response.json();
      qrData.value = data.token; // Actualizamos el QR con el token de Dataverse
    }
  } catch (error) {
    console.error("Error renovando QR", error);
  }
};

// 2. Control de tiempos unificado
const startInterval = () => {
  stopInterval();
  fetchNewQr(); // Pedimos el primero apenas se abre
  refreshInterval = setInterval(() => {
    fetchNewQr();
  }, 5000); // Se renueva cada 5 segundos
};

const stopInterval = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
};

// 3. Vigilar si el modal se abre o cierra (Código del equipo adaptado)
watch(() => props.show, (show) => {
  if (show) {
    startInterval();
  } else {
    stopInterval();
  }
}, { immediate: true });

onUnmounted(() => {
  stopInterval();
});

const handleClose = () => {
  emit('close');
};
</script>

<template>
  <div v-if="show" class="qr-overlay flex-center animate-fade-in" @click="handleClose">
    <div class="qr-modal animate-scale-in" @click.stop>
      <h3>CÓDIGO QR DE ASISTENCIA AMBIENTE 402</h3>

      <div class="qr-container-proyector">
        <qrcode-vue :value="qrData" :size="220" level="M" />
      </div>

      <p>
        Abre VoltMind Access en tu teléfono, selecciona "ESCANEAR" y apunta a
        la pantalla para registrar tu asistencia.
      </p>
      <button class="btn-close-overlay font-bold" @click="handleClose">
        CERRAR PANTALLA COMPARTIDA
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Nos quedamos con los estilos del equipo (HEAD) porque tienen la estructura visual más reciente */
.qr-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.45);
  backdrop-filter: blur(6px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.qr-modal {
  background: var(--fondo-tarjetas);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
  text-align: center;
  width: 100%;
  max-width: 360px;
  padding: 2rem;
  border-radius: var(--border-radius-lg, 16px);
  box-shadow: 0 20px 40px rgba(0, 48, 64, 0.16);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.qr-modal h3 {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0;
  line-height: 1.4;
}

.qr-container-proyector {
  background: #ffffff; 
  padding: 1.25rem;
  border-radius: 12px;
  display: inline-block;
  margin: 1.5rem 0;
  box-shadow: 0 8px 24px rgba(0, 48, 64, 0.08);
  border: 1px solid var(--borde);
}

.qr-modal p {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  line-height: 1.5;
  margin-bottom: 1.5rem;
}
.btn-close-overlay {
  background: var(--sena-azul-oscuro);
  color: #ffffff;
  border: none;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-close-overlay:hover {
  background: var(--sena-verde);
  color: #ffffff;
}
</style>