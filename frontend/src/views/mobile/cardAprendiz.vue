<template>
  <div class="carnet-shell">
    <WaveTexture direction="horizontal" />

    <div
      class="carnet"
      :class="{
        'is-validated': isValidated || isNfcTransmitting || isScanningQr,
      }"
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
            <span class="brand-sub">Centro de Electricidad</span>
          </div>
        </div>

        <div
          class="carnet-badge"
          :class="{
            'is-active': isValidated || isNfcTransmitting || isScanningQr,
          }"
        >
          <span class="badge-led" />
          <font-awesome-icon
            :icon="
              isNfcTransmitting
                ? 'fa-solid fa-satellite-dish'
                : isScanningQr
                  ? 'fa-solid fa-camera'
                  : isValidated
                    ? 'fa-solid fa-circle-check'
                    : 'fa-solid fa-id-badge'
            "
            class="badge-icon"
          />
          <span>{{
            isNfcTransmitting
              ? "TRANSMITIENDO"
              : isScanningQr
                ? "CÁMARA ACTIVA"
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
          :isTransmitting="isNfcTransmitting || isScanningQr"
          :isValidated="isValidated"
        />

        <div class="user-info">
          <h2 class="user-name">{{ userStore.name || "Aprendiz SENA" }}</h2>
          <p class="user-email">
            {{ userStore.email || "usuario@sena.edu.co" }}
          </p>
          <div class="user-meta">
            <span class="meta-tag tag-ficha">
              <font-awesome-icon icon="fa-solid fa-graduation-cap" /> 2997671
            </span>
          </div>
        </div>
      </div>

      <div class="carnet-scan-zone">
        <div
          class="otp-preview"
          :class="{
            'otp-active': otpCode || isNfcTransmitting || isScanningQr,
          }"
        >
          <div class="otp-title">
            {{
              isNfcTransmitting
                ? "VÍNCULO NFC"
                : isScanningQr
                  ? "ESCÁNER ÓPTICO"
                  : "PIN DINÁMICO"
            }}
          </div>

          <div class="otp-value" v-if="!isScanningQr">
            {{ isNfcTransmitting ? "NFC" : otpDisplay }}
          </div>

          <div class="otp-meta" style="margin-top: 10px">
            <span
              class="otp-timer-badge"
              v-if="otpCode && !isNfcTransmitting && !isScanningQr"
            >
              <font-awesome-icon icon="fa-solid fa-clock" class="icon-pulse" />
              {{ otpSeconds }}s restantes
            </span>
            <span class="otp-status-text">
              {{
                isNfcTransmitting
                  ? "Acerca el teléfono a la tablet."
                  : isScanningQr
                    ? "Apunta la cámara al código de la tablet."
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
          <span class="live-dot" /> Vigente 2026
        </div>
      </div>
    </div>

    <div class="action-panel">
      <button
        class="btn-method btn-qr"
        @click="startQrScan"
        :disabled="isGeneratingOtp || isNfcTransmitting || isScanningQr"
      >
        <font-awesome-icon icon="fa-solid fa-camera" />
        <span>ESCANEAR</span>
      </button>

      <button
        class="btn-method btn-nfc"
        @click="triggerNfcTransmission"
        :disabled="isGeneratingOtp || isScanningQr"
      >
        <span class="nfc-pulse-ring" v-if="isNfcTransmitting" />
        <font-awesome-icon
          :icon="isNfcTransmitting ? 'fa-solid fa-rss' : 'fa-solid fa-wifi'"
        />
        <span>NFC</span>
      </button>

      <button
        class="btn-method btn-pin"
        @click="generateOtp"
        :disabled="isGeneratingOtp || isNfcTransmitting || isScanningQr"
      >
        <font-awesome-icon icon="fa-solid fa-lock" />
        <span>PIN</span>
      </button>

      <button
        class="btn-exit-small"
        @click="handleExitCard"
        title="Cerrar Sesión"
      >
        <font-awesome-icon icon="fa-solid fa-right-from-bracket" />
      </button>
    </div>

    <div v-if="isScanningQr" class="scanner-overlay">
      <div class="scanner-header">
        <h3>Escaneando Código del Aula</h3>
        <button class="btn-close-scanner" @click="isScanningQr = false">
          Cancelar
        </button>
      </div>
      <div class="camera-viewport">
        <qrcode-stream
          @detect="onQrDetect"
          @error="onCameraError"
        ></qrcode-stream>
        <div class="scanner-target"></div>
      </div>
    </div>

    <transition name="status-slide">
      <div v-if="statusMsg" class="status-strip" :class="statusType">
        <font-awesome-icon
          :icon="
            statusType === 'success'
              ? 'fa-solid fa-circle-check'
              : 'fa-solid fa-circle-info'
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
import { QrcodeStream } from "vue-qrcode-reader"; // <-- Importamos el lector
import WaveTexture from "@/components/WaveTexture.vue";
import UserAvatar from "@/components/UserAvatar.vue";

const router = useRouter();

// --- ESTADOS ---
const isValidated = ref(false);
const statusMsg = ref("");
const statusType = ref("info");
const otpMessage = ref("Selecciona un método de validación.");

const otpCode = ref("");
const isGeneratingOtp = ref(false);
const isNfcTransmitting = ref(false);
const isScanningQr = ref(false); // Estado de la cámara

const otpSeconds = ref(0);
const otpTimer = ref(null);

const userStore = ref({
  name: "Diego Alejandro Tobar",
  email: "diego.tobar@sena.edu.co",
  avatarUrl: "",
});

const idCode = computed(() => "2997671");
const otpDisplay = computed(() =>
  otpCode.value ? otpCode.value.split("").join(" ") : "----",
);

onUnmounted(() => {
  clearOtpTimer();
});

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

const resetMethods = () => {
  clearOtpTimer();
  isValidated.value = false;
  otpCode.value = "";
  isScanningQr.value = false;
  isNfcTransmitting.value = false;
};

// 1. LÓGICA ESCÁNER QR (NUEVO)
const startQrScan = () => {
  resetMethods();
  isScanningQr.value = true;
};

// Evento que se dispara cuando la cámara lee un QR
const onQrDetect = (detectedCodes) => {
  if (detectedCodes && detectedCodes.length > 0) {
    const qrData = detectedCodes[0].rawValue; // Aquí tienes lo que dice el QR de la tablet
    isScanningQr.value = false;
    isValidated.value = true;
    showStatus("Código de aula validado exitosamente.", "success", 3000);
    console.log("Datos capturados del QR:", qrData);
    // Aquí harías la petición a FastAPI enviando el qrData
  }
};

// Función mejorada para capturar problemas de permisos de cámara
const onCameraError = (error) => {
  isScanningQr.value = false; // Cerramos el modal de la cámara
  
  let errorMsg = "Error desconocido de cámara.";

  // Diccionario de errores nativos del navegador / OS
  if (error.name === 'NotAllowedError') {
    errorMsg = "Permiso denegado: Activa la cámara en tu navegador/teléfono.";
  } else if (error.name === 'NotFoundError') {
    errorMsg = "No se detectó ninguna cámara en el dispositivo.";
  } else if (error.name === 'NotSupportedError' || error.name === 'InsecureContextError') {
    errorMsg = "Seguridad: La cámara requiere entorno seguro (HTTPS).";
  } else if (error.name === 'NotReadableError') {
    errorMsg = "La cámara ya está siendo usada por otra aplicación.";
  } else if (error.name === 'OverconstrainedError') {
    errorMsg = "Las cámaras no cumplen los requisitos del sistema.";
  } else if (error.name === 'StreamApiNotSupportedError') {
    errorMsg = "Tu navegador no soporta streaming de video.";
  }

  showStatus(errorMsg, "error", 5000); // Mostramos el toast rojo por 5 segundos
};

// 2. LÓGICA PIN
const generateOtp = () => {
  resetMethods();
  isGeneratingOtp.value = true;
  setTimeout(() => {
    otpCode.value = Math.floor(1000 + Math.random() * 9000).toString();
    isGeneratingOtp.value = false;
    otpMessage.value = "Ingresa este PIN en la tablet.";
    otpSeconds.value = 30;
    otpTimer.value = setInterval(() => {
      otpSeconds.value = Math.max(0, otpSeconds.value - 1);
      if (otpSeconds.value === 0) {
        clearOtpTimer();
        otpMessage.value = "PIN expirado.";
        otpCode.value = "";
      }
    }, 1000);
    showStatus("PIN temporal creado.", "success", 2000);
  }, 500);
};

// 3. LÓGICA NFC
const triggerNfcTransmission = () => {
  resetMethods();
  isNfcTransmitting.value = true;
  showStatus("Acerca tu teléfono a la tablet...", "info", 2000);
  setTimeout(() => {
    isNfcTransmitting.value = false;
    isValidated.value = true;
    showStatus("Ingreso RFID validado.", "success", 3000);
  }, 4000);
};

const handleExitCard = () => {
  router.push("/route-selector");
};
</script>

<style scoped>
/* (MANTÉN TU CSS ORIGINAL DE LA TARJETA Y BOTONERA) */
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
    0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
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
  background: rgba(57, 169, 0, 0.08);
  border-color: rgba(57, 169, 0, 0.3);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 140px;
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
  display: block;
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

.action-panel {
  display: flex;
  gap: 8px;
  width: 100%;
  max-width: 375px;
  z-index: 1;
}
.btn-method {
  flex: 1;
  border: none;
  border-radius: 12px;
  padding: 14px 4px;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}
.btn-method font-awesome-icon {
  font-size: 1.1rem;
}
.btn-qr {
  background: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
}
.btn-qr:hover:not(:disabled) {
  background: #001f2a;
  transform: translateY(-2px);
}
.btn-nfc {
  background: var(--sena-verde);
  color: var(--sena-blanco);
}
.btn-nfc:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
}
.btn-pin {
  background: var(--sena-amarillo);
  color: var(--sena-azul-oscuro);
}
.btn-pin:hover:not(:disabled) {
  background: #e0ac00;
  transform: translateY(-2px);
}
.btn-exit-small {
  width: 48px;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}
.btn-exit-small:hover {
  background: #ff4d4f;
  color: white;
  border-color: #ff4d4f;
}
.btn-method:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* --- ESTILOS DE LA CÁMARA (NUEVO) --- */
.scanner-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 999;
  display: flex;
  flex-direction: column;
}

.scanner-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  z-index: 1000;
}

.scanner-header h3 {
  font-size: 1rem;
  margin: 0;
}

.btn-close-scanner {
  background: transparent;
  color: var(--sena-amarillo);
  border: 1px solid var(--sena-amarillo);
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 700;
}

.camera-viewport {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* El cuadro objetivo flotante sobre la cámara */
.scanner-target {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 250px;
  height: 250px;
  border: 2px solid var(--sena-verde);
  border-radius: 12px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5); /* Oscurece el resto de la pantalla */
  pointer-events: none;
}
.scanner-target::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--sena-verde);
  animation: scan-line 2s infinite linear;
}

@keyframes scan-line {
  0% {
    top: 0;
  }
  50% {
    top: 100%;
  }
  100% {
    top: 0;
  }
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
  z-index: 1000;
  white-space: nowrap;
}
.status-strip.success {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}
.status-strip.error {
  border-color: #e53e3e;
  color: #e53e3e;
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
.nfc-pulse-ring {
  position: absolute;
  inset: 0;
  border: 2px solid var(--sena-verde);
  border-radius: 12px;
  animation: nfc-wave 1.2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}
</style>
