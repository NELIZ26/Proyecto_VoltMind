<template>
  <div v-if="isModal" class="spinner-modal-overlay">
    <div class="spinner-modal-content">
      <div class="spinner" :class="sizeClass"></div>
      <p v-if="message" class="spinner-message">{{ message }}</p>
    </div>
  </div>
  <div v-else-if="inline" class="spinner-inline">
    <div class="spinner" :class="sizeClass"></div>
    <span v-if="message" class="spinner-message-inline">{{ message }}</span>
  </div>
  <div v-else class="loading-state">
    <div class="spinner" :class="sizeClass"></div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: {
    type: String,
    default: '',
  },
  isModal: {
    type: Boolean,
    default: false,
  },
  inline: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
  }
});

const sizeClass = computed(() => `spinner-${props.size}`);
</script>

<style scoped>
/* ── MODO INLINE (Para botones y textos) ── */
.spinner-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.spinner-message-inline {
  font-size: inherit;
  font-weight: inherit;
}

/* ── MODO BLOQUE (Para secciones o páginas) ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--texto-secundario);
  gap: 1rem;
  width: 100%;
}

/* ── MODO MODAL (Bloquea la pantalla o un contenedor relativo) ── */
.spinner-modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 48, 64, 0.7);
  backdrop-filter: blur(2px);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: inherit;
}

.spinner-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: white;
}

.spinner-message {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  text-align: center;
}

/* ── EL SPINNER ANIMADO ── */
.spinner {
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  opacity: 0.8;
}

.spinner-medium {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(57, 169, 0, 0.2);
  border-top-color: var(--sena-verde, #39A900);
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(57, 169, 0, 0.2);
  border-top-color: var(--sena-verde, #39A900);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
