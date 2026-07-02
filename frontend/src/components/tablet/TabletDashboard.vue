<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { useKioskStore } from '@/stores/kioskStore';

const toast = useToast();
const kioskStore = useKioskStore();

const emit = defineEmits(['open-firma', 'open-qr', 'open-pin']);

const fichaActiva = ref(localStorage.getItem('fichaActiva') || '0000000');
const nombreInstructor = ref(localStorage.getItem('nombreInstructor') || 'Instructor');
const currentTime = ref('');
const apprentices = ref([]);
const isLoading = ref(true);

const showAllAlertsModal = ref(false);
const isListeningNfc = ref(false);

const horaInicio = ref(localStorage.getItem('horaInicio') || '--:--');
const horaFin = ref(localStorage.getItem('horaFin') || '--:--');

let timeInterval;

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: true });
  
  // Sincronización fallback con localStorage por si los WebSockets fallan
  const storedHora = localStorage.getItem('horaInicio');
  if (storedHora && storedHora !== horaInicio.value) {
    horaInicio.value = storedHora;
  } else if (!storedHora && horaInicio.value !== '--:--') {
    horaInicio.value = '--:--';
  }

  const storedHoraFin = localStorage.getItem('horaFin');
  if (storedHoraFin && storedHoraFin !== horaFin.value) {
    horaFin.value = storedHoraFin;
  } else if (!storedHoraFin && horaFin.value !== '--:--') {
    horaFin.value = '--:--';
  }
};

onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
  kioskStore.connectWebSocket("402"); // Ambiente fijo por ahora
});

// Vigilar firma forzada por el instructor
watch(() => kioskStore.firmaRequerida, (newFirma) => {
  if (newFirma) {
    // Si el instructor pide firma de salida manual, abrimos el modal
    emit('open-firma', { id: newFirma.id, name: newFirma.name });
    kioskStore.clearFirma();
  }
});

onUnmounted(() => {
  clearInterval(timeInterval);
});

// To be integrated with modals in TabletView

const toggleNfcListening = () => {
  isListeningNfc.value = !isListeningNfc.value;
  if (isListeningNfc.value) {
    toast.info("Escuchando lector NFC de la tablet...");
  }
};


</script>

<template>
  <div class="tablet-dashboard">
    <!-- Top Header Bar -->
    <header class="dash-top-bar">
      <div class="dash-left">
        <img src="@/assets/LogoSena.png" alt="SENA" class="h-logo" />
        <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="h-logo volt-logo" />
        <div class="dash-title-area">
          <h1>AMBIENTE 402</h1>
          <p>Ficha: {{ fichaActiva }} | Instructor: {{ nombreInstructor }} | {{ currentTime }}</p>
        </div>
      </div>
      <div class="dash-right">
        <span class="status-text">AULA APAGADA</span>
      </div>
    </header>

    <!-- Time Cards -->
    <div class="time-cards-row">
      <div class="time-card start-card">
        <div class="tc-icon green-bg"><font-awesome-icon icon="fa-solid fa-clock" /></div>
        <div class="tc-info">
          <span>Hora de Inicio</span>
          <strong>{{ horaInicio !== '--:--' ? horaInicio : kioskStore.horaInicio }}</strong>
        </div>
      </div>
      <div class="time-card end-card">
        <div class="tc-icon red-bg"><font-awesome-icon icon="fa-solid fa-trash" /></div>
        <div class="tc-info">
          <span>Hora de Cierre</span>
          <strong>{{ horaFin }}</strong>
        </div>
      </div>
      <div class="time-card extra-card">
        <div class="tc-icon yellow-bg"><font-awesome-icon icon="fa-solid fa-triangle-exclamation" /></div>
        <div class="tc-info">
          <span>Horas Extras</span>
          <strong>0 min</strong>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="kiosk-fullscreen-container">
      <div v-if="kioskStore.status === 'BLOQUEADO'" class="kiosk-blocked-msg">
        <font-awesome-icon icon="fa-solid fa-ban" class="block-icon" />
        <h2>REGISTRO CERRADO</h2>
        <p>El instructor ha bloqueado los métodos de registro. Acércate al escritorio.</p>
      </div>

      <div v-else class="registration-methods">
        <div class="kiosk-btn" :class="{'listening': isListeningNfc}" @click="toggleNfcListening">
          <div class="kiosk-btn-icon"><font-awesome-icon icon="fa-solid fa-wifi" /></div>
          <div class="kiosk-btn-text">
            <h3>Acercar Carnet</h3>
            <p>Lector NFC activo</p>
          </div>
        </div>
        
        <div class="kiosk-btn qr-action" @click="emit('open-qr')">
          <div class="kiosk-btn-icon"><font-awesome-icon icon="fa-solid fa-qrcode" /></div>
          <div class="kiosk-btn-text">
            <h3>Escanear QR</h3>
            <p>Muestra tu código a la cámara</p>
          </div>
        </div>

        <div class="kiosk-btn pin-action" @click="emit('open-pin')">
          <div class="kiosk-btn-icon"><font-awesome-icon icon="fa-solid fa-lock" /></div>
          <div class="kiosk-btn-text">
            <h3>Ingresar PIN</h3>
            <p>Digita tu código de acceso manual</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showAllAlertsModal" class="modal-overlay" @click.self="showAllAlertsModal = false">
      <div class="modal-content">
        <h3>Todas las Alertas</h3>
        <div class="alerts-list">
          <div class="alert-card" style="margin-bottom: 12px;">
            <div class="ac-icon"><font-awesome-icon icon="fa-solid fa-triangle-exclamation" /></div>
            <div class="ac-content">
              <p>Alerta de Deserción: Validación Dataverse pendiente.</p>
              <span>HOY • ASISTENCIA</span>
            </div>
          </div>
          <div class="alert-card">
            <div class="ac-icon"><font-awesome-icon icon="fa-solid fa-triangle-exclamation" /></div>
            <div class="ac-content">
              <p>Alerta de Deserción: Validación Dataverse pendiente.</p>
              <span>AYER • ASISTENCIA</span>
            </div>
          </div>
        </div>
        <button class="btn-close" @click="showAllAlertsModal = false">Cerrar</button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.tablet-dashboard {
  min-height: 100vh;
  background-color: #e5e5e5;
  padding: 1.5rem;
  font-family: var(--fuente-principal);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* TOP BAR */
.dash-top-bar {
  background: var(--sena-blanco);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.dash-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.h-logo { height: 36px; }
.volt-logo { margin-left: -8px; }
.dash-title-area h1 {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 2px 0;
}
.dash-title-area p {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0;
}
.dash-right .status-text {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

/* TIME CARDS */
.time-cards-row {
  display: flex;
  gap: 1.5rem;
}
.time-card {
  flex: 1;
  background: var(--sena-blanco);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 6px solid transparent;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.start-card { border-left-color: var(--sena-verde); }
.end-card { border-left-color: #ef4444; }
.extra-card { border-left-color: var(--sena-amarillo); }

.tc-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}
.green-bg { background-color: var(--sena-verde); }
.red-bg { background-color: #ef4444; }
.yellow-bg { background-color: var(--sena-amarillo); }

.tc-info {
  display: flex;
  flex-direction: column;
}
.tc-info span {
  font-size: 0.8rem;
  color: var(--texto-secundario);
}
.tc-info strong {
  font-size: 1.1rem;
  color: var(--sena-azul-oscuro);
}

/* KIOSK CONTAINER */
.kiosk-fullscreen-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  width: 100%;
}

.kiosk-blocked-msg {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fef2f2;
  border: 2px dashed #f87171;
  color: #b91c1c;
  padding: 4rem;
  border-radius: 16px;
  text-align: center;
  gap: 1rem;
}
.kiosk-blocked-msg .block-icon {
  font-size: 4rem;
}
.kiosk-blocked-msg h2 {
  font-size: 2rem;
  font-weight: 900;
  margin: 0;
}
.kiosk-blocked-msg p {
  font-size: 1.2rem;
  margin: 0;
}

/* REGISTRATION METHODS (KIOSK) */
.registration-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-top: 1rem;
}
.kiosk-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  background: var(--fondo-app);
  border: 2px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}
.kiosk-btn:hover {
  border-color: var(--sena-azul-oscuro);
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.05);
}
.kiosk-btn-icon {
  font-size: 2rem;
  color: var(--sena-azul-oscuro);
  margin-bottom: 0.25rem;
  transition: all 0.3s ease;
}
.kiosk-btn-text h3 {
  margin: 0 0 0.25rem 0;
  color: var(--sena-azul-oscuro);
  font-size: 1.1rem;
  font-weight: 800;
}
.kiosk-btn-text p {
  margin: 0;
  color: var(--texto-secundario);
  font-size: 0.8rem;
}

/* Specific styling for listening state */
.kiosk-btn.listening {
  border-color: var(--sena-verde);
  background-color: #f0fdf4;
}
.kiosk-btn.listening .kiosk-btn-icon {
  color: var(--sena-verde);
  animation: pulse-green-icon 1.5s infinite;
}
@keyframes pulse-green-icon {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}



/* MODALS */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}
.modal-content {
  background: var(--sena-blanco);
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 12px 24px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
}
.modal-content.large-modal {
  max-width: 700px;
}
.modal-content h3 {
  margin: 0 0 1.5rem 0;
  color: var(--sena-azul-oscuro);
  font-weight: 800;
  font-size: 1.4rem;
}

.btn-close {
  background: var(--fondo-app);
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 1rem;
  align-self: flex-end;
}
.btn-close:hover {
  background: #e2e8f0;
}
</style>
