<script setup>
import { ref, onMounted, onUnmounted} from 'vue';
import QrcodeVue from 'qrcode.vue'; // 🟢 Importamos el componente del QR

const props = defineProps(['fichaActiva']);
const emit = defineEmits(['close']);
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const qrData = ref(""); // 🟢 Aquí guardamos el token
let refreshInterval = null;

// 1. Función para pedirle un QR nuevo a Python
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
      qrData.value = data.token; // Actualizamos la variable
    }
  } catch (error) {
    console.error("Error renovando QR", error);
  }
};

onMounted(() => {
  // Pedimos el primero apenas se abre la ventana
  fetchNewQr();
  
  // Pedimos uno nuevo cada 5 segundos para que nunca muera
  refreshInterval = setInterval(() => {
    fetchNewQr();
  }, 5000); 
});

onUnmounted(() => {
  // Apagamos el motor cuando cierras la ventana
  if (refreshInterval) clearInterval(refreshInterval);
});
</script>

<template>
  <div class="qr-overlay" @click="emit('close')">
    <div class="qr-modal" @click.stop>
      <h3>CÓDIGO QR DE ASISTENCIA AMBIENTE 402</h3>
      
      <div class="qr-container-proyector">
        <qrcode-vue :value="qrData" :size="220" level="M" />
      </div>
      
      <p>Abre VoltMind Access en tu teléfono, selecciona "ESCANEAR" y apunta a la pantalla para registrar tu asistencia.</p>
      
      <button class="btn-close-overlay" @click="emit('close')">
        CERRAR PANTALLA COMPARTIDA
      </button>
    </div>
  </div>
</template>
<style scoped>
.qr-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.qr-modal {
  background: var(--sena-blanco, #ffffff);
  color: var(--sena-azul-oscuro, #003040);
  text-align: center;
  max-width: 400px;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.qr-modal h3 {
  font-size: 1rem;
  font-weight: 800;
  margin: 0;
}

.qr-container-proyector {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 16px;
  display: inline-block;
  margin: 1.5rem 0;
  box-shadow: 0 8px 24px rgba(0, 48, 64, 0.1);
  border: 1px solid var(--borde, #e2e8f0);
  transition: transform 0.2s ease;
}

.qr-modal p {
  font-size: 0.85rem;
  color: var(--texto-secundario, #64748b);
  line-height: 1.5;
  margin-bottom: 2rem;
}

.btn-close-overlay {
  background: var(--sena-azul-oscuro, #003040);
  color: var(--sena-blanco, #ffffff);
  border: none;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
}

.btn-close-overlay:hover {
  background: var(--sena-verde-oscuro, #007832);
}
</style>