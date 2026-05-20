<script setup>
import { ref } from "vue";

defineProps({
  apprentice: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "confirm"]);

const exitReason = ref("");
const waitingNfcExit = ref(false);

const enableNfcForExit = () => {
  waitingNfcExit.value = true;
  // Simulación temporal de lectura NFC tras 2.5s
  setTimeout(() => {
    if (waitingNfcExit.value) {
      emit("confirm", exitReason.value);
      waitingNfcExit.value = false;
    }
  }, 2500);
};
</script>

<template>
  <div class="modal-backdrop" @click="!waitingNfcExit && $emit('close')">
    <div class="modal-card" @click.stop>
      <div class="modal-header">
        <div class="header-indicator alert-glow"></div>
        <h3>REGISTRO DE SALIDA ANTICIPADA</h3>
      </div>

      <div class="modal-body">
        <p class="warning-text">
          Va a autorizar el retiro de <strong>{{ apprentice.name }}</strong> del
          ambiente de formación.
        </p>

        <div class="form-group">
          <label>MOTIVO DEL RETIRO TEMPRANO</label>
          <textarea
            v-model="exitReason"
            placeholder="Ej: Cita médica, retiro autorizado, indisposición..."
            :disabled="waitingNfcExit"
          ></textarea>
        </div>

        <div v-if="!waitingNfcExit" class="nfc-trigger-zone">
          <p class="nfc-notice">
            Para confirmar la salida, se requiere que el aprendiz valide su
            identidad físicamente acercando su carnet a la tablet.
          </p>
          <button
            class="btn-nfc-enable"
            :disabled="!exitReason.trim()"
            @click="enableNfcForExit"
          >
            <font-awesome-icon icon="fa-solid fa-wifi" class="icon-rotate" />
            HABILITAR ANTENA NFC DE LA TABLET
          </button>
        </div>

        <div v-else class="nfc-waiting-zone">
          <div class="nfc-radar-container">
            <div class="radar-wave wave-1"></div>
            <div class="radar-wave wave-2"></div>
            <div class="radar-core">
              <font-awesome-icon icon="fa-solid fa-wifi" />
            </div>
          </div>
          <p class="text-blink">LECTOR INTEGRADO ESPERANDO TARJETA...</p>
          <small class="nfc-subtext"
            >Acerque el dispositivo móvil o carnet físico a la zona trasera de
            la tableta.</small
          >
        </div>
      </div>

      <div class="modal-footer">
        <button
          class="btn-modal-cancel"
          :disabled="waitingNfcExit"
          @click="$emit('close')"
        >
          CANCELAR
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   INTERFAZ TÉCNICA - MODAL DE SALIDA DE HARDWARE (NFC)
   ========================================================================== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  font-family: var(--fuente-principal, "Inter", sans-serif);
}

.modal-card {
  background: #0d0d0f;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
}

/* Encabezado */
.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.25rem;
}

.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--sena-naranja, #ff6b00);
  border-radius: 2px;
}

.alert-glow {
  box-shadow: 0 0 10px rgba(255, 107, 0, 0.5);
}

.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  letter-spacing: 0.08em;
}

/* Texto Informativo */
.warning-text {
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--texto-principal, #ffffff);
  text-align: left;
}

.warning-text strong {
  color: var(--sena-naranja, #ff6b00);
  font-weight: 600;
}

/* Formulario */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 1.25rem 0;
  text-align: left;
}

.form-group label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario, #a0aec0);
  letter-spacing: 0.03em;
}

.form-group textarea {
  background: #121215;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  border-radius: 8px;
  color: var(--texto-principal, #ffffff);
  padding: 12px;
  font-family: var(--fuente-principal, "Inter", sans-serif);
  font-size: 0.8rem;
  resize: none;
  height: 72px;
  transition: all 0.3s ease;
}

.form-group textarea:focus:not(:disabled) {
  outline: none;
  border-color: var(--sena-verde, #39a900);
  background: #151519;
  box-shadow: 0 0 8px rgba(57, 169, 0, 0.15);
}

.form-group textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Zona Activación NFC */
.nfc-trigger-zone {
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed var(--borde, rgba(255, 255, 255, 0.08));
  padding: 14px;
  border-radius: 10px;
  text-align: center;
}

.nfc-notice {
  font-size: 0.7rem;
  color: var(--texto-secundario, #a0aec0);
  line-height: 1.4;
  margin-bottom: 12px;
  opacity: 0.8;
}

/* Botón de Activación de Hardware */
.btn-nfc-enable {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--sena-verde, #39a900);
  color: #fff;
  border: none;
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  width: 100%;
  transition: all 0.3s ease;
}

.btn-nfc-enable:hover:not(:disabled) {
  background-color: #2d8500;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.btn-nfc-enable:disabled {
  background: #16161a;
  border: 1px solid rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.2);
  cursor: not-allowed;
}

.icon-rotate {
  transform: rotate(
    90deg
  ); /* Voltear icono wifi para simular ondas horizontales */
}

/* ==========================================================================
   ANIMACIÓN EXCLUSIVA DE RADAR / ESCANEO NFC
   ========================================================================== */
.nfc-waiting-zone {
  text-align: center;
  padding: 1rem 0 0.5rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nfc-radar-container {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.radar-core {
  width: 32px;
  height: 32px;
  background: var(--sena-verde, #39a900);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  z-index: 3;
  transform: rotate(90deg);
  box-shadow: 0 0 10px var(--sena-verde, #39a900);
}

.radar-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: transparent;
  border: 1.5px solid var(--sena-verde, #39a900);
  opacity: 0;
  z-index: 1;
}

.wave-1 {
  animation: radarPulse 1.6s cubic-bezier(0.1, 0.8, 0.3, 1) infinite;
}

.wave-2 {
  animation: radarPulse 1.6s cubic-bezier(0.1, 0.8, 0.3, 1) infinite;
  animation-delay: 0.8s;
}

@keyframes radarPulse {
  0% {
    transform: scale(0.5);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}

.text-blink {
  font-size: 0.7rem;
  color: var(--sena-verde-claro, #deff9a);
  font-weight: 800;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
  animation: telemetryBlink 1.4s infinite;
}

@keyframes telemetryBlink {
  50% {
    opacity: 0.3;
  }
}

.nfc-subtext {
  font-size: 0.65rem;
  color: var(--texto-secundario, #a0aec0);
  opacity: 0.6;
  max-width: 260px;
}

/* Footer y Botón Cancelar */
.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.btn-modal-cancel {
  background: transparent;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  color: var(--texto-secundario, #a0aec0);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.btn-modal-cancel:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.02);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--texto-principal, #ffffff);
}

.btn-modal-cancel:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
