<template>
  <div class="carnet-shell">
    <div class="bg-particles">
      <span
        v-for="n in 12"
        :key="n"
        class="particle"
        :style="particleStyle(n)"
      />
    </div>

    <div
      class="carnet"
      :class="{ 'is-validated': isValidated || isNfcTransmitting }"
    >
      <div class="laser-scanner" />
      <div class="holo-overlay" />

      <div class="carnet-header">
        <div class="carnet-header-left">
          <div class="logo-container">
            <div class="logo-shine" />
            <img src="@/assets/LogoSena.png" alt="SENA" class="carnet-logo" />
          </div>

          <div class="carnet-brand">
            <div class="brand-title-group">
              <span class="brand-name">SENA</span>
              <span class="brand-divider" :style="{ background: neonColor }" />
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
          <span
            class="badge-led"
            :style="
              isValidated || isNfcTransmitting
                ? { backgroundColor: '#39a900', boxShadow: '0 0 8px #39a900' }
                : { backgroundColor: '#ffd700', boxShadow: '0 0 8px #ffd700' }
            "
          />
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
        <div
          class="avatar-ring"
          :style="{
            '--neon-dynamic': isNfcTransmitting ? '#00ffcc' : neonColor,
          }"
        >
          <div class="avatar-inner">
            <img
              v-if="userStore.avatarUrl"
              :src="userStore.avatarUrl"
              :alt="userStore.name"
              class="avatar-img"
            />

            <div v-else class="avatar-robot-fallback">
              <svg
                viewBox="0 0 100 100"
                class="robot-svg"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M42 20 L35 10 M58 20 L65 10"
                  stroke="#7f8c8d"
                  stroke-width="3"
                  stroke-linecap="round"
                />
                <circle
                  cx="35"
                  cy="10"
                  r="3"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                />
                <circle
                  cx="65"
                  cy="10"
                  r="3"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                />

                <rect
                  x="20"
                  y="42"
                  width="6"
                  height="16"
                  rx="2"
                  fill="#2c3e50"
                />
                <rect
                  x="74"
                  y="42"
                  width="6"
                  height="16"
                  rx="2"
                  fill="#2c3e50"
                />
                <circle
                  cx="23"
                  cy="50"
                  r="1.5"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                />
                <circle
                  cx="77"
                  cy="50"
                  r="1.5"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                />

                <rect
                  x="25"
                  y="25"
                  width="50"
                  height="50"
                  rx="14"
                  :fill="headColor"
                  stroke="#111115"
                  stroke-width="2"
                />

                <rect
                  x="32"
                  y="38"
                  width="36"
                  height="18"
                  rx="6"
                  fill="#0d0d11"
                  stroke="rgba(255,255,255,0.05)"
                  stroke-width="1"
                />

                <circle
                  cx="43"
                  cy="47"
                  r="4.5"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                  class="eye-glow"
                />
                <circle
                  cx="57"
                  cy="47"
                  r="4.5"
                  :fill="isNfcTransmitting ? '#00ffcc' : neonColor"
                  class="eye-glow"
                />
                <circle cx="44" cy="46" r="1.5" fill="#ffffff" />
                <circle cx="58" cy="46" r="1.5" fill="#ffffff" />

                <path
                  d="M42 63 L58 63 M45 67 L55 67 M48 71 L52 71"
                  stroke="rgba(255,255,255,0.2)"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
            </div>
          </div>
        </div>

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
          <div
            class="otp-glow-bg"
            :style="{ background: isNfcTransmitting ? '#00ffcc' : neonColor }"
          />
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
            <span class="otp-status-text">{{
              isNfcTransmitting
                ? "Acerque el teléfono a la antena de la tablet."
                : otpMessage
            }}</span>
          </div>
        </div>
      </div>

      <div class="carnet-footer">
        <div class="carnet-id-number">
          <font-awesome-icon
            icon="fa-solid fa-fingerprint"
            class="icon-glow-tech"
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
        <span class="btn-glow" v-if="isGeneratingOtp" />
        <span class="btn-shine" />
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

const getUniqueColor = (text, type) => {
  if (!text) return type === "head" ? "#5c4a42" : "#ffd700";
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }
  const headColors = ["#5c4a42", "#2c3e50", "#34495e", "#7f8c8d", "#1e3d59"];
  const neonColors = ["#ffd700", "#00ffcc", "#ff3366", "#3399ff", "#4ade80"];
  const index = Math.abs(hash);
  return type === "head"
    ? headColors[index % headColors.length]
    : neonColors[index % neonColors.length];
};

const headColor = computed(() => getUniqueColor(userStore.value.name, "head"));
const neonColor = computed(() => getUniqueColor(userStore.value.name, "neon"));
const idCode = computed(() => "2997671");

const particleStyle = (n) => {
  const angle = (n / 12) * 360;
  const r = 45 + (n % 3) * 15;
  return {
    left: `${50 + r * Math.cos((angle * Math.PI) / 180)}%`,
    top: `${50 + r * Math.sin((angle * Math.PI) / 180)}%`,
    animationDelay: `${n * 0.4}s`,
    width: `${4 + (n % 3) * 3}px`,
    height: `${4 + (n % 3) * 3}px`,
    opacity: 0.12 + (n % 4) * 0.04,
  };
};

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

// ── SIMULACIÓN DE EMISIÓN NFC DE HARDWARE ──
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

onUnmounted(() => {
  clearOtpTimer();
});
</script>

<style scoped>
/* Se mantienen todas tus directivas de diseño base intactas */
.carnet-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 32px 16px;
  background: #050d14;
  background-image:
    radial-gradient(
      circle at 50% 10%,
      rgba(0, 77, 115, 0.45) 0%,
      transparent 60%
    ),
    radial-gradient(
      circle at 80% 90%,
      rgba(57, 169, 0, 0.05) 0%,
      transparent 50%
    ),
    linear-gradient(to bottom, #050d14, #02060a);
  position: relative;
  overflow: hidden;
  font-family: var(--fuente-principal, "Inter", sans-serif);
}

.bg-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.particle {
  position: absolute;
  border-radius: 50%;
  background: #39a900;
  box-shadow: 0 0 10px rgba(57, 169, 0, 0.6);
  animation: float-advanced 6s ease-in-out infinite alternate;
}

@keyframes float-advanced {
  0% {
    transform: translateY(0) rotate(0deg) scale(1);
    opacity: 0.3;
  }
  100% {
    transform: translateY(-25px) rotate(180deg) scale(1.3);
    opacity: 0.8;
  }
}

.carnet {
  width: 100%;
  max-width: 365px;
  background: linear-gradient(
    160deg,
    rgba(13, 34, 51, 0.85) 0%,
    rgba(7, 18, 26, 0.95) 50%,
    rgba(10, 42, 24, 0.6) 100%
  );
  border-radius: 32px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow:
    0 40px 80px rgba(0, 0, 0, 0.7),
    0 0 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 1px rgba(255, 255, 255, 0.15);
  position: relative;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.carnet.is-validated {
  border-color: rgba(57, 169, 0, 0.35);
  box-shadow:
    0 40px 80px rgba(0, 0, 0, 0.7),
    0 0 40px rgba(57, 169, 0, 0.15),
    inset 0 1px 2px rgba(57, 169, 0, 0.3);
}

.holo-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.03) 25%,
    rgba(57, 169, 0, 0.04) 45%,
    rgba(0, 255, 204, 0.03) 55%,
    rgba(255, 255, 255, 0) 100%
  );
  pointer-events: none;
  z-index: 3;
}
.laser-scanner {
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(57, 169, 0, 0.5),
    transparent
  );
  box-shadow: 0 0 12px #39a900;
  animation: scan-action 4s linear infinite;
  z-index: 4;
  opacity: 0.3;
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
  padding: 22px 24px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: linear-gradient(
    180deg,
    rgba(0, 50, 77, 0.3) 0%,
    rgba(5, 13, 20, 0) 100%
  );
  position: relative;
}
.logo-container {
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0.01) 100%
  );
  padding: 8px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.1);
}
.logo-shine {
  position: absolute;
  top: -50%;
  left: -60%;
  width: 30%;
  height: 200%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.15),
    transparent
  );
  transform: rotate(35deg);
  animation: logo-flash 6s ease-in-out infinite;
}

@keyframes logo-flash {
  0%,
  80% {
    left: -60%;
  }
  90%,
  100% {
    left: 140%;
  }
}
.carnet-logo {
  height: 32px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}
.carnet-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.carnet-brand {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.brand-title-group {
  display: flex;
  align-items: center;
  gap: 6px;
}
.brand-name {
  font-size: 0.95rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: 0.04em;
}
.brand-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}
.brand-project {
  font-size: 0.95rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.02em;
}
.brand-sub {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.01em;
  font-weight: 500;
}

.carnet-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  background: rgba(4, 10, 15, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 30px;
  padding: 6px 14px 6px 10px;
  font-size: 0.68rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.06em;
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.badge-icon {
  font-size: 0.78rem;
  opacity: 0.6;
  transition: transform 0.3s ease;
}
.badge-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  transition: all 0.4s ease;
}
.carnet-badge.is-active {
  background: rgba(57, 169, 0, 0.08);
  border-color: rgba(57, 169, 0, 0.4);
  color: #4ade80;
  box-shadow:
    0 0 15px rgba(57, 169, 0, 0.15),
    inset 0 1px 0 rgba(57, 169, 0, 0.2);
}
.carnet-badge.is-active .badge-icon {
  opacity: 1;
  transform: scale(1.1);
  color: #39a900;
}

.carnet-identity {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 24px 18px;
}
.avatar-ring {
  position: relative;
  flex-shrink: 0;
  width: 78px;
  height: 78px;
  border-radius: 50%;
  background: linear-gradient(
    145deg,
    rgba(0, 50, 77, 0.3),
    rgba(0, 10, 15, 0.8)
  );
  border: 2px solid var(--neon-dynamic, rgba(255, 255, 255, 0.1));
  box-shadow: 0 0 14px var(--neon-dynamic);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s ease;
}
.avatar-inner {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: rgba(5, 13, 20, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-robot-fallback {
  background: radial-gradient(circle at center, #11151d 0%, #05070a 100%);
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.robot-svg {
  width: 82%;
  height: 82%;
}
.eye-glow {
  filter: drop-shadow(0 0 3px currentColor);
}

.user-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}
.user-email {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.35);
  margin: 0 0 12px;
}
.user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.meta-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 4px 10px;
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
}
.meta-tag svg {
  color: rgba(255, 255, 255, 0.35);
}

.carnet-scan-zone {
  padding: 0 24px 22px;
}
.otp-preview {
  position: relative;
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(4, 10, 15, 0.85);
  text-align: center;
  overflow: hidden;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
  transition: all 0.4s ease;
}
.otp-glow-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border-radius: 50%;
  filter: blur(45px);
  opacity: 0.04;
  pointer-events: none;
  transition: opacity 0.4s ease;
}
.otp-preview.otp-active .otp-glow-bg {
  opacity: 0.15;
}
.otp-title {
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.25em;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
}
.otp-value {
  font-size: 2.8rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: 0.15em;
  margin: 10px 0;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
  font-variant-numeric: tabular-nums;
}
.otp-preview.otp-active .otp-value {
  color: #c6ff9e;
  text-shadow: 0 0 15px rgba(198, 255, 158, 0.4);
}
.otp-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.otp-timer-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  align-self: center;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 2px 10px;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.6);
}
.otp-status-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.35);
}

.carnet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px 22px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}
.carnet-id-number {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.35);
  font-family: "Courier New", Courier, monospace;
  font-weight: 700;
}
.icon-glow-tech {
  color: #00ffcc;
  filter: drop-shadow(0 0 4px rgba(0, 255, 204, 0.6));
}
.carnet-validity {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.72rem;
  color: #39a900;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.live-dot {
  width: 6px;
  height: 6px;
  background-color: #39a900;
  border-radius: 50%;
  box-shadow: 0 0 8px #39a900;
  animation: pulse-dot 2s infinite alternate;
}

@keyframes pulse-dot {
  0% {
    transform: scale(0.9);
    opacity: 0.5;
    box-shadow: 0 0 2px #39a900;
  }
  100% {
    transform: scale(1.2);
    opacity: 1;
    box-shadow: 0 0 10px #39a900;
  }
}

/* ==========================================================================
   NUEVA ARQUITECTURA DISTRIBUIDA DE ACCIONES (ZONA NFC INCLUIDA)
   ========================================================================== */
.action-panel {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 365px;
}

.btn-scan,
.btn-nfc,
.btn-exit {
  border: none;
  border-radius: 16px;
  padding: 14px 8px;
  font-size: 0.8rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

/* Botón de PIN Tradicional */
.btn-scan {
  flex: 1.2;
  background: linear-gradient(135deg, #004d73 0%, #002b40 100%);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}
.btn-scan:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0, 77, 115, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 📡 NUEVO BOTÓN DE HARDWARE NFC CON EFECTO FLUORESCENTE */
.btn-nfc {
  flex: 1.2;
  background: linear-gradient(135deg, #112423 0%, #081212 100%);
  color: #00ffcc;
  border: 1px solid rgba(0, 255, 204, 0.2);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.btn-nfc:hover:not(:disabled) {
  transform: translateY(-2px);
  background: linear-gradient(135deg, #163533 0%, #0c1c1b 100%);
  border-color: rgba(0, 255, 204, 0.5);
  box-shadow: 0 12px 24px rgba(0, 255, 204, 0.15);
  color: #ffffff;
}

.btn-nfc:disabled {
  border-color: rgba(0, 255, 204, 0.1);
  color: rgba(0, 255, 204, 0.4);
  cursor: not-allowed;
}

/* Ondas electromagnéticas de radiofrecuencia (NFC Rings) */
.nfc-pulse-ring {
  position: absolute;
  inset: 0;
  border: 2px solid #00ffcc;
  border-radius: 16px;
  animation: nfc-wave 1.2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

@keyframes nfc-wave {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.15, 1.3);
    opacity: 0;
  }
}

.icon-broadcast {
  animation: pulse-icon 0.6s ease-in-out infinite alternate;
}

/* Botón Salir */
.btn-exit {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.btn-exit:hover:not(:disabled) {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-scan:disabled,
.btn-exit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Toasts */
.status-strip {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(5, 13, 20, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 12px 24px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(16px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  z-index: 100;
}
.status-strip.success {
  border-color: rgba(57, 169, 0, 0.5);
  color: #4ade80;
}
.status-strip.info {
  border-color: rgba(0, 255, 204, 0.3);
  color: #00ffcc;
}

.status-slide-enter-active,
.status-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.status-slide-enter-from,
.status-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.voltmind-watermark {
  position: absolute;
  bottom: 16px;
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.03);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  user-select: none;
}
.icon-pulse {
  animation: pulse-icon 2s infinite;
}

@keyframes pulse-icon {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}
</style>
