<script setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import QrcodeVue from 'qrcode.vue';

const props = defineProps({
  show: { type: Boolean, required: true },
  fichaActiva: { type: String, required: true }
});

const emit = defineEmits(['close']);

const dynamicToken = ref("GENERANDO...");
let qrInterval = null;

const qrPayload = computed(() => {
  return JSON.stringify({
    ambiente: "402",
    ficha: props.fichaActiva,
    token: dynamicToken.value,
  });
});

const startInterval = () => {
  stopInterval();
  dynamicToken.value = `VM-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
  qrInterval = setInterval(() => {
    dynamicToken.value = `VM-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
  }, 5000);
};

const stopInterval = () => {
  if (qrInterval) {
    clearInterval(qrInterval);
    qrInterval = null;
  }
};

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
        <qrcode-vue :value="qrPayload" :size="220" level="M" />
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
  background: #ffffff; /* Para asegurar contraste del código QR en modo claro y oscuro */
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
