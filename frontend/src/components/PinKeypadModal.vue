<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  show: { type: Boolean, required: true },
  isLoading: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'submit']);
const pinDigits = ref("");

const pressKey = (num) => {
  if (pinDigits.value.length < 4) pinDigits.value += num;
};

const clearPin = () => { pinDigits.value = pinDigits.value.slice(0, -1); };
const handleCancel = () => { pinDigits.value = ""; emit('close'); };

const handleConfirm = () => {
  if (pinDigits.value.length === 4) {
    emit('submit', pinDigits.value);
    pinDigits.value = "";
  }
};

const handleKeyDown = (e) => {
  if (!props.show || props.isLoading) return;
  if (/[0-9]/.test(e.key)) pressKey(e.key);
  else if (e.key === 'Backspace') clearPin();
  else if (e.key === 'Enter') handleConfirm();
  else if (e.key === 'Escape') handleCancel();
};

onMounted(() => window.addEventListener('keydown', handleKeyDown));
onUnmounted(() => window.removeEventListener('keydown', handleKeyDown));
</script>

<template>
  <div v-if="show" class="pin-overlay flex-center animate-fade-in" @click="handleCancel">
    <div class="pin-modal-card animate-scale-in" @click.stop>
      
      <header class="pin-card-header text-center">
        <h3>VALIDACIÓN POR PIN</h3>
        <p class="text-secondary text-xs">Digite el código dinámico del aprendiz</p>
      </header>

      <div class="pin-display flex-center" :class="{ 'is-loading-state': isLoading }">
        <template v-if="isLoading">
          <font-awesome-icon :icon="['fas', 'circle-notch']" class="animate-pulse" />
          <span class="text-xs font-semibold m-xs">Sincronizando...</span>
        </template>
        <template v-else>
          <span v-for="(digit, idx) in 4" :key="idx" class="digit-slot" :class="{ 'has-value': pinDigits[idx] !== undefined }">
            {{ pinDigits[idx] !== undefined ? pinDigits[idx] : '•' }}
          </span>
        </template>
      </div>

      <div class="keypad-grid" :style="{ pointerEvents: isLoading ? 'none' : 'auto', opacity: isLoading ? 0.4 : 1 }">
        <button v-for="n in 9" :key="n" class="key-btn font-bold" @click="pressKey(n)">{{ n }}</button>
        <button class="key-btn action-key-btn back-btn flex-center" title="Borrar" @click="clearPin">
          <font-awesome-icon :icon="['fas', 'arrow-left']" />
        </button>
        <button class="key-btn font-bold" @click="pressKey(0)">0</button>
        <button class="key-btn action-key-btn confirm-btn flex-center" :disabled="pinDigits.length !== 4" @click="handleConfirm">
          <font-awesome-icon :icon="['fas', 'check']" />
        </button>
      </div>

      <button class="cancel-action-link text-xs font-bold" :disabled="isLoading" @click="handleCancel">
        CANCELAR OPERACIÓN
      </button>
    </div>
  </div>
</template>

<style scoped>
.pin-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.45);
  backdrop-filter: blur(6px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}
.pin-modal-card {
  width: 100%;
  max-width: 310px;
  background: var(--fondo-tarjetas);
  border-radius: var(--border-radius-lg, 16px);
  padding: 1.5rem;
  box-shadow: 0 20px 40px rgba(0, 48, 64, 0.16);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid var(--borde);
}
.pin-card-header h3 {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--texto-principal);
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}
.pin-card-header p { margin-bottom: 1.25rem; }
.pin-display {
  width: 100%;
  height: 90px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.pin-display.is-loading-state {
  gap: 6px;
  background: rgba(57, 169, 0, 0.04);
  border-color: rgba(57, 169, 0, 0.2);
  color: var(--sena-verde);
}
.digit-slot {
  width: 55px;
  height: 55px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  line-height: 1;
}
.digit-slot:not(.has-value) {
  font-size: 1.5rem;
  font-weight: 400;
  color: var(--borde);
  opacity: 0.7;
}
.digit-slot.has-value {
  background-color: transparent;
  border-color: transparent;
  color: var(--texto-principal);
  font-size: 2.2rem;
  font-weight: 700;
}
.keypad-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  width: 100%;
  margin-bottom: 1.25rem;
}
.key-btn {
  height: 54px;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  font-size: 1.15rem;
  color: var(--texto-principal);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.key-btn:hover {
  background: var(--fondo-app);
  border-color: var(--texto-principal);
}
.action-key-btn { font-size: 0.95rem; border-color: transparent; }
.back-btn { background: rgba(229, 62, 62, 0.05); color: #E53E3E; }
.back-btn:hover { background: #E53E3E; color: #ffffff; }
.confirm-btn { background: rgba(57, 169, 0, 0.08); color: var(--sena-verde); }
.confirm-btn:hover:not(:disabled) { background: var(--sena-verde); color: #ffffff; }
.confirm-btn:disabled { background: var(--fondo-app); color: rgba(0, 48, 64, 0.25); cursor: not-allowed; }
.cancel-action-link { background: transparent; border: none; color: var(--texto-principal); opacity: 0.7; cursor: pointer; padding: 4px 8px; transition: color 0.2s; }
.cancel-action-link:hover:not(:disabled) { color: #E53E3E; opacity: 1; }
.cancel-action-link:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
