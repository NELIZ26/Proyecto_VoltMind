<script setup>
import { ref } from "vue";

const props = defineProps({
  isLoading: Boolean
});

const emit = defineEmits(["close", "submit"]);

const pinDigits = ref("");

const pressKey = (num) => {
  if (pinDigits.value.length < 4) pinDigits.value += num;
};

const clearPin = () => {
  pinDigits.value = pinDigits.value.slice(0, -1);
};

const submitPin = () => {
  if (pinDigits.value.length === 4) {
    emit("submit", pinDigits.value);
    pinDigits.value = ""; // Limpiamos para el próximo
  }
};
</script>

<template>
  <div class="qr-overlay" @click="emit('close')">
    <div class="qr-modal pin-modal" @click.stop>
      <h3>VALIDACIÓN POR PIN DINÁMICO</h3>
      <p class="pin-instruction">Digite el código generado en el dispositivo del aprendiz.</p>

      <div class="pin-display" :class="{ 'is-loading': isLoading }">
        {{ isLoading ? "Sincronizando..." : pinDigits.padEnd(4, "•").split("").join(" ") }}
      </div>

      <div class="keypad" :style="{ pointerEvents: isLoading ? 'none' : 'auto', opacity: isLoading ? 0.5 : 1 }">
        <button v-for="n in 9" :key="n" class="btn-key" @click="pressKey(n)">{{ n }}</button>
        <button class="btn-key action-key" @click="clearPin">
          <font-awesome-icon icon="fa-solid fa-arrow-left" />
        </button>
        <button class="btn-key" @click="pressKey(0)">0</button>
        <button class="btn-key submit-key" @click="submitPin" :disabled="pinDigits.length !== 4">
          <font-awesome-icon icon="fa-solid fa-check" />
        </button>
      </div>

      <button class="btn-close-overlay" @click="emit('close')">CANCELAR</button>
    </div>
  </div>
</template>

<style scoped>
/* Fondo oscuro compartido */
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

/* Caja blanca base */
.qr-modal {
  background: var(--sena-blanco);
  color: var(--sena-azul-oscuro);
  text-align: center;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.qr-modal h3 {
  font-size: 1rem;
  font-weight: 800;
  margin: 0;
}

.btn-close-overlay {
  background: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  border: none;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
}

.btn-close-overlay:hover {
  background: var(--sena-verde-oscuro);
}

/* Estilos específicos del Teclado */
.pin-modal {
  max-width: 360px;
  padding: 2rem 1.5rem;
}

.pin-instruction {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0.5rem 0 1.5rem;
  line-height: 1.4;
}

.pin-display {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 16px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  letter-spacing: 0.1em;
  transition: all 0.3s ease;
}

.pin-display.is-loading {
  font-size: 1rem;
  letter-spacing: normal;
  color: var(--sena-verde);
  background: rgba(57, 169, 0, 0.1);
  border-color: var(--sena-verde);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 1.5rem;
  transition: opacity 0.3s ease;
}

.btn-key {
  aspect-ratio: 1 / 1;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-key:hover {
  background: var(--sena-blanco);
  border-color: var(--sena-verde);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 48, 64, 0.05);
}

.btn-key:active {
  transform: translateY(0);
}

.action-key {
  font-size: 1.1rem;
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.05);
  border-color: transparent;
}

.action-key:hover {
  background: #e53e3e;
  color: white;
  border-color: #e53e3e;
}

.submit-key {
  font-size: 1.2rem;
  background: var(--sena-verde);
  color: white;
  border-color: var(--sena-verde-oscuro);
}

.submit-key:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
}

.submit-key:disabled {
  background: var(--borde);
  border-color: var(--borde);
  color: var(--texto-secundario);
  cursor: not-allowed;
  opacity: 0.5;
}
</style>