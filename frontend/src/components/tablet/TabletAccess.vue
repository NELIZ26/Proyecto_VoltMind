<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// 🟢 AQUÍ ESTÁ LA MAGIA: Le decimos al hijo que reciba el nombre del aula desde el Padre
const props = defineProps({
  ambienteNombre: {
    type: String,
    default: "Ambiente Desconocido"
  }
});

const emit = defineEmits(['nfc-success', 'open-qr', 'open-pin']);

const currentTime = ref('');
const currentDate = ref('');
let timer;

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  currentDate.value = now.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});

// Simulamos el NFC con un click
const handleNfcClick = () => {
  emit('nfc-success');
};
</script>

<template>
  <div class="tablet-access-container">
    <div class="top-right-clock">
      <div class="time-display">{{ currentTime }}</div>
      <div class="date-display">{{ currentDate }}</div>
    </div>

    <div class="header-logos">
      <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="logo-volt" />
      <div class="logo-divider"></div>
      <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
    </div>

    <div class="location-badge">
      <font-awesome-icon icon="fa-solid fa-location-dot" />
      <span>{{ ambienteNombre }}</span>
    </div>

    <div class="title-section">
      <h1>PANEL DE ACCESO VOLTMIND</h1>
      <p>Acerque su carnet digital NFC al dispositivo:</p>
    </div>

    <div class="nfc-box" @click="handleNfcClick">
      <span>Validando ....</span>
    </div>

    <div class="action-buttons">
      <button class="btn-dark" @click="emit('open-qr')">
        <font-awesome-icon icon="fa-solid fa-qrcode" />
        <span>ESCANEAR QR</span>
      </button>
      <button class="btn-yellow" @click="emit('open-pin')">
        <font-awesome-icon icon="fa-solid fa-lock" />
        <span>DIGITAR PIN</span>
      </button>
    </div>

    <div class="footer-text">
      "Esperando credencial / Validando / Acceso concedido / Token expirado"
    </div>
  </div>
</template>

<style scoped>
.tablet-access-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
  position: relative;
  background-color: var(--fondo-app);
  padding: 2rem;
  box-sizing: border-box;
}

.top-right-clock {
  position: absolute;
  top: 2rem;
  right: 2rem;
  text-align: center;
}

.time-display {
  background-color: #e2e8f0;
  color: var(--sena-azul-oscuro);
  font-size: 1.25rem;
  font-weight: 800;
  padding: 8px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.date-display {
  color: var(--texto-secundario);
  font-size: 0.9rem;
  font-weight: 600;
}

.header-logos {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 1.5rem;
}

.logo-volt {
  height: 48px;
  width: auto;
}

.logo-sena {
  height: 48px;
  width: auto;
}

.logo-divider {
  width: 1px;
  height: 32px;
  background-color: var(--borde);
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.15);
  border: 1px solid rgba(57, 169, 0, 0.4);
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--sena-verde-oscuro);
  font-size: 0.85rem;
  font-weight: 800;
  margin-bottom: 2rem;
}

.title-section {
  text-align: center;
  margin-bottom: 2rem;
}

.title-section h1 {
  font-size: 2rem;
  font-weight: 900;
  color: var(--sena-azul-oscuro);
  margin: 0 0 8px 0;
}

.title-section p {
  font-size: 1rem;
  color: var(--texto-secundario);
  margin: 0;
}

.nfc-box {
  width: 100%;
  max-width: 500px;
  background-color: #e5f5e5;
  border: 1px solid #c2e0c6;
  border-radius: 12px;
  padding: 3rem 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nfc-box:hover {
  background-color: #d1f0d1;
  transform: scale(1.02);
}

.nfc-box span {
  font-size: 1.8rem;
  font-weight: 800;
  color: #8cc63f; /* Verde brillante que se ve en la imagen */
}

.action-buttons {
  display: flex;
  gap: 1rem;
  width: 100%;
  max-width: 500px;
  margin-bottom: 3rem;
}

.btn-dark {
  flex: 1;
  background-color: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  border: none;
  border-radius: 8px;
  padding: 1.2rem;
  font-size: 1rem;
  font-weight: 800;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-dark:hover {
  transform: translateY(-2px);
}
.btn-dark svg {
  font-size: 1.5rem;
}

.btn-yellow {
  flex: 1;
  background-color: var(--sena-amarillo);
  color: var(--sena-blanco);
  border: none;
  border-radius: 8px;
  padding: 1.2rem;
  font-size: 1rem;
  font-weight: 800;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-yellow:hover {
  transform: translateY(-2px);
}
.btn-yellow svg {
  font-size: 1.5rem;
}

.footer-text {
  color: var(--texto-secundario);
  font-size: 0.85rem;
}
</style>