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
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.25rem;
}
.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--sena-naranja);
  border-radius: 2px;
}
.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}

.warning-text {
  font-size: 0.85rem;
  color: var(--texto-principal);
  line-height: 1.5;
}
.warning-text strong {
  color: var(--sena-naranja);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 1.25rem 0;
}
.form-group label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
}
.form-group textarea {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 12px;
  font-size: 0.8rem;
  resize: none;
  height: 72px;
  color: var(--texto-principal);
}

.nfc-trigger-zone {
  background: var(--fondo-app);
  border: 1px dashed var(--borde);
  padding: 14px;
  border-radius: 10px;
  text-align: center;
}
.nfc-notice {
  font-size: 0.7rem;
  color: var(--texto-secundario);
  margin-bottom: 12px;
}

.btn-nfc-enable {
  background-color: var(--sena-verde);
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 8px;
  width: 100%;
  font-weight: 700;
  cursor: pointer;
}
.btn-nfc-enable:disabled {
  background: var(--borde);
  color: var(--texto-secundario);
}

.nfc-waiting-zone {
  text-align: center;
  padding: 1rem 0;
}
.radar-core {
  background: var(--sena-verde);
  color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
}
.text-blink {
  color: var(--sena-verde);
  font-weight: 800;
  font-size: 0.75rem;
}

.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}
.btn-modal-cancel {
  background: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
