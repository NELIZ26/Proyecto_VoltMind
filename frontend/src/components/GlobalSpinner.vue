<template>
  <div v-if="isModal" class="spinner-modal-overlay">
    <div class="spinner-modal-content">
      <div class="spinner"></div>
      <p v-if="message" class="spinner-message">{{ message }}</p>
    </div>
  </div>
  <div v-else class="loading-state">
    <div class="spinner"></div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Cargando...',
  },
  isModal: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
/* ── MODO INLINE (Como estaba en el Dashboard de Complementarias) ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: var(--texto-secundario);
  gap: 1rem;
}

/* ── MODO MODAL (Bloquea la pantalla) ── */
.spinner-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-modal-content {
  background: var(--fondo-tarjetas, #ffffff);
  padding: 2.5rem 3.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner-message {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro, #00324d);
  text-align: center;
}

[data-theme="dark"] .spinner-modal-content {
  background: var(--fondo-tarjetas, #1e293b);
  border: 1px solid var(--borde, #334155);
}

[data-theme="dark"] .spinner-message {
  color: var(--texto-principal, #f1f5f9);
}

/* ── EL SPINNER ANIMADO ── */
.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(57, 169, 0, 0.2);
  border-top-color: var(--sena-verde, #39A900);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
