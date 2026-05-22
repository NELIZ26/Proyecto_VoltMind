<template>
  <div class="carnet-shell">
    <WaveTexture direction="horizontal" />

    <div
      class="carnet"
      :class="{ 'is-validated': isValidated || isNfcTransmitting }"
    >
      <div class="laser-scanner" />

      <div class="carnet-header">
        <div class="carnet-header-left">
          <div class="logo-container">
            <div class="logo-shine" />
            <img src="@/assets/LogoSena.png" alt="SENA" class="carnet-logo" />
          </div>

          <div class="carnet-brand">
            <div class="brand-title-group">
              <span class="brand-name">SENA</span>
              <span class="brand-divider" />
              <span class="brand-project">VoltMind</span>
            </div>
            <span class="brand-sub"
              >Centro de Electricidad y Automatización</span
            >
          </div>
        </div>

        <div
          class="carnet-badge"
          :class="{ 'is-active': isValidated || isNfcTransmitting }"
        >
          <span class="badge-led" />
          <font-awesome-icon
            :icon="
              isValidated || isNfcTransmitting
                ? 'fa-solid fa-circle-check'
                : 'fa-solid fa-id-badge'
            "
            class="badge-icon"
          />
          <span>{{
            isNfcTransmitting
              ? "TRANSMITIENDO"
              : isValidated
                ? "VALIDADO"
                : "APRENDIZ"
          }}</span>
        </div>
      </div>

      <div class="carnet-identity">
        <UserAvatar
          :src="userStore.avatarUrl"
          :alt="userStore.name"
          :isTransmitting="isNfcTransmitting"
          :isValidated="isValidated"
        />

        <div class="user-info">
          <h2 class="user-name">{{ userStore.name || "Aprendiz SENA" }}</h2>
          <p class="user-email">
            {{ userStore.email || "usuario@sena.edu.co" }}
          </p>
          <div class="user-meta">
            <span class="meta-tag tag-ficha">
              <font-awesome-icon icon="fa-solid fa-graduation-cap" />
              Ficha 2997671
            </span>
            <span class="meta-tag tag-area">
              <font-awesome-icon icon="fa-solid fa-bolt" />
              Electricidad
            </span>
          </div>
        </div>
      </div>

      <div class="carnet-scan-zone">
        <div
          class="otp-preview"
          :class="{ 'otp-active': otpCode || isNfcTransmitting }"
        >
          <div class="otp-title">
            {{ isNfcTransmitting ? "VÍNCULO NFC ACTIVO" : "PIN DINÁMICO" }}
          </div>
          <div class="otp-value">
            {{ isNfcTransmitting ? "NFC" : otpDisplay }}
          </div>
          <div class="otp-meta">
            <span class="otp-timer-badge" v-if="otpCode && !isNfcTransmitting">
              <font-awesome-icon icon="fa-solid fa-clock" class="icon-pulse" />
              {{ otpSeconds }}s restantes
            </span>
            <span class="otp-status-text">
              {{
                isNfcTransmitting
                  ? "Acerque el teléfono a la antena de la tablet."
                  : otpMessage
              }}
            </span>
          </div>
        </div>
      </div>

      <div class="carnet-footer">
        <div class="carnet-id-number">
          <font-awesome-icon
            icon="fa-solid fa-fingerprint"
            class="icon-brand-tech"
          />
          VM-{{ idCode }}
        </div>
        <div class="carnet-validity">
          <span class="live-dot" />
          Vigente 2026
        </div>
      </div>
    </div>

    <div class="action-panel">
      <button
        class="btn-scan"
        @click="generateOtp"
        :disabled="isGeneratingOtp || isNfcTransmitting"
      >
        <font-awesome-icon icon="fa-solid fa-lock" />
        <span>{{ isGeneratingOtp ? "Generando..." : "PIN" }}</span>
      </button>

      <button
        class="btn-nfc"
        @click="triggerNfcTransmission"
        :disabled="isNfcTransmitting"
      >
        <span class="nfc-pulse-ring" v-if="isNfcTransmitting" />
        <font-awesome-icon
          :icon="
            isNfcTransmitting
              ? 'fa-solid fa-rss'
              : 'fa-solid fa-contactless-payment'
          "
          :class="{ 'icon-broadcast': isNfcTransmitting }"
        />
        <span>{{ isNfcTransmitting ? "Enviando..." : "NFC" }}</span>
      </button>

      <button
        class="btn-exit"
        @click="handleExitCard"
        :disabled="isNfcTransmitting"
      >
        <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
        <span>Salir</span>
      </button>
    </div>

    <transition name="status-slide">
      <div v-if="statusMsg" class="status-strip" :class="statusType">
        <font-awesome-icon
          :icon="
            statusType === 'success'
              ? 'fa-solid fa-circle-check'
              : statusType === 'info'
                ? 'fa-solid fa-wave-square'
                : 'fa-solid fa-triangle-exclamation'
          "
        />
        {{ statusMsg }}
      </div>
    </transition>

    <div class="voltmind-watermark">VoltMind Access</div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import WaveTexture from "@/components/WaveTexture.vue";
import UserAvatar from "@/components/UserAvatar.vue";

const router = useRouter();

const isValidated = ref(false);
const statusMsg = ref("");
const statusType = ref("info");
const otpCode = ref("");
const otpSeconds = ref(0);
const otpTimer = ref(null);
const isGeneratingOtp = ref(false);
const isNfcTransmitting = ref(false);
const otpMessage = ref("Pulsa Generar PIN o usa NFC para validar.");

const userStore = ref({
  name: "Diego Alejandro Tobar",
  email: "diego.tobar@sena.edu.co",
  avatarUrl: "",
});

const idCode = computed(() => "2997671");

onUnmounted(() => {
  clearOtpTimer();
});

// --- LÓGICA DE CONTROL DEL CARNET ---
const showStatus = (msg, type = "info", duration = 3000) => {
  statusMsg.value = msg;
  statusType.value = type;
  setTimeout(() => {
    statusMsg.value = "";
  }, duration);
};

const clearOtpTimer = () => {
  if (otpTimer.value) {
    clearInterval(otpTimer.value);
    otpTimer.value = null;
  }
};

const startOtpTimer = () => {
  clearOtpTimer();
  otpTimer.value = setInterval(() => {
    otpSeconds.value = Math.max(0, otpSeconds.value - 1);
    if (otpSeconds.value === 0) {
      clearOtpTimer();
      otpMessage.value = "El PIN expiró. Genera uno nuevo.";
      otpCode.value = "";
    }
  }, 1000);
};

const generateOtp = async () => {
  isGeneratingOtp.value = true;
  setTimeout(() => {
    otpCode.value = Math.floor(1000 + Math.random() * 9000).toString();
    otpSeconds.value = 60;
    otpMessage.value = "PIN generado. Ingrésalo en la tablet.";
    startOtpTimer();
    isValidated.value = false;
    isGeneratingOtp.value = false;
    showStatus("PIN creado con éxito.", "success", 2500);
  }, 800);
};

const triggerNfcTransmission = () => {
  isNfcTransmitting.value = true;
  clearOtpTimer();
  otpCode.value = "";
  showStatus("Emisor NFC VoltMind activado...", "info", 2000);

  setTimeout(() => {
    isNfcTransmitting.value = false;
    isValidated.value = true;
    showStatus("Token transmitido vía RFID/NFC con éxito.", "success", 3000);
  }, 3500);
};

const otpDisplay = computed(() => {
  if (!otpCode.value) return "----";
  return otpCode.value.split("").join(" ");
});

const handleExitCard = () => {
  showStatus("Cerrando sesión...", "info", 1000);
  setTimeout(() => {
    router.push("/");
  }, 1000);
};
</script>

<style scoped>
/* ==========================================================================
   INTERFAZ ADAPTADA AL MANUAL DE IDENTIDAD VISUAL SENA 2024 (CASO 1: BLANCO)
   CON VARIABLES CSS GLOBALES
   ========================================================================== */

.carnet-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 32px 16px;
  background: var(--sena-gris-claro);
  position: relative;
  overflow: hidden;
  font-family: var(--fuente-principal);
}

.carnet {
  width: 100%;
  max-width: 375px;
  background: var(--sena-blanco);
  border-radius: 24px;
  border: 1px solid var(--borde);
  box-shadow:
    0 20px 40px rgba(0, 48, 64, 0.08),
    /* Transparencia manual basada en azul oscuro */ 0 1px 3px
      rgba(0, 0, 0, 0.05); /* Sombra genérica base */
  position: relative;
  overflow: hidden;
  transition:
    max-width 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    border-color 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 1;
}

.carnet.is-validated {
  border-color: var(--sena-verde);
  box-shadow:
    0 20px 40px rgba(57, 169, 0, 0.12),
    0 0 0 1px var(--sena-verde);
  max-width: 390px;
  transform: scale(1.015);
  transform-origin: left center;
}

.laser-scanner {
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--sena-verde),
    transparent
  );
  animation: scan-action 4s linear infinite;
  z-index: 4;
  opacity: 0.4;
}

@keyframes scan-action {
  0% {
    top: -10%;
  }
  50% {
    top: 110%;
  }
  100% {
    top: -10%;
  }
}

.carnet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--sena-gris-claro);
  background: var(--sena-blanco);
}

.logo-container {
  padding: 6px;
  border-radius: 10px;
  border: 1px solid var(--borde);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--sena-blanco);
}

.carnet-logo {
  height: 36px;
  width: auto;
}

.carnet-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.carnet-brand {
  display: flex;
  flex-direction: column;
}

.brand-title-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.brand-name {
  font-size: 1rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  letter-spacing: 0.02em;
}

.brand-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: var(--sena-verde);
}

.brand-project {
  font-size: 1rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.brand-sub {
  font-size: 0.65rem;
  color: var(--texto-secundario);
  font-weight: 500;
  opacity: 0.8;
}

.carnet-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--sena-gris-claro);
  border: 1px solid var(--borde);
  border-radius: 30px;
  padding: 6px 12px;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--texto-secundario);
  letter-spacing: 0.02em;
}

.badge-icon {
  font-size: 0.75rem;
}

.badge-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--sena-amarillo);
}

.carnet-badge.is-active {
  background: rgba(57, 169, 0, 0.08); /* Fondo verde transparente */
  border-color: rgba(57, 169, 0, 0.3); /* Borde verde semi-transparente */
  color: var(--sena-verde-oscuro);
  margin-left: 8px;
}

.carnet-badge.is-active .badge-led {
  background-color: var(--sena-verde);
}

.carnet-identity {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px;
}

.user-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0 0 2px;
}

.user-email {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  margin: 0 0 10px;
}

.user-meta {
  display: flex;
  gap: 8px;
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--sena-gris-claro);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.68rem;
  color: var(--texto-secundario);
  font-weight: 600;
}

.carnet-scan-zone {
  padding: 0 24px 24px;
}

.otp-preview {
  padding: 20px;
  border-radius: 16px;
  border: 1px solid var(--borde);
  background: var(--sena-gris-claro);
  text-align: center;
}

.otp-title {
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  color: var(--texto-secundario);
  font-weight: 700;
}

.otp-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  letter-spacing: 0.1em;
  margin: 8px 0;
}

.otp-preview.otp-active .otp-value {
  color: var(--sena-verde);
}

.otp-timer-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--borde);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.7rem;
  color: var(--texto-secundario);
  margin-bottom: 4px;
}

.otp-status-text {
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.carnet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--sena-gris-claro);
  background: var(--sena-blanco);
}

.carnet-id-number {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  font-family: monospace;
  font-weight: 700;
}

.icon-brand-tech {
  color: var(--sena-azul-oscuro);
}

.carnet-validity {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: var(--sena-verde-oscuro);
  font-weight: 700;
}

.live-dot {
  width: 6px;
  height: 6px;
  background-color: var(--sena-verde);
  border-radius: 50%;
  animation: pulse-dot 2s infinite alternate;
}

@keyframes pulse-dot {
  0% {
    transform: scale(0.9);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* ==========================================================================
   PANEL DE BOTONES
   ========================================================================== */
.action-panel {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 365px;
  z-index: 1;
}

.btn-scan,
.btn-nfc,
.btn-exit {
  border: none;
  border-radius: 12px;
  padding: 14px 8px;
  font-size: 0.8rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.btn-scan {
  flex: 1.2;
  background: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
}

.btn-scan:hover:not(:disabled) {
  background: #001f2a; /* Azul más oscuro para hover manual */
  transform: translateY(-1px);
}

.btn-nfc {
  flex: 1.2;
  background: var(--sena-verde);
  color: var(--sena-blanco);
  position: relative;
}

.btn-nfc:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
  transform: translateY(-1px);
}

.nfc-pulse-ring {
  position: absolute;
  inset: 0;
  border: 2px solid var(--sena-verde);
  border-radius: 12px;
  animation: nfc-wave 1.2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

@keyframes nfc-wave {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  100% {
    transform: scale(1.1, 1.2);
    opacity: 0;
  }
}

.btn-exit {
  flex: 1;
  background: var(--borde);
  color: var(--texto-secundario);
}

.btn-exit:hover:not(:disabled) {
  background: #cbd5e0; /* Gris más oscuro para hover manual */
  color: var(--sena-negro);
}

.btn-scan:disabled,
.btn-nfc:disabled,
.btn-exit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.status-strip {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--sena-blanco);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 25px rgba(0, 48, 64, 0.1);
  z-index: 100;
}

.status-strip.success {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}

.status-strip.info {
  border-color: var(--sena-azul-oscuro);
  color: var(--sena-azul-oscuro);
}

.status-slide-enter-active,
.status-slide-leave-active {
  transition: all 0.3s ease;
}

.status-slide-enter-from,
.status-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(15px);
}

.voltmind-watermark {
  position: absolute;
  bottom: 12px;
  font-size: 0.65rem;
  color: var(--borde);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  user-select: none;
}

.icon-pulse {
  animation: pulse-icon 1.5s infinite alternate;
}

@keyframes pulse-icon {
  0% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>
