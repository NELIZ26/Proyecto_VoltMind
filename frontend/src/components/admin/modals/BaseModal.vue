<template>
  <Transition name="modal">
    <div v-if="show" class="modal-backdrop" @click="handleBackdropClick">
      <div class="modal-container animate-slide-up" @click.stop>
        <header class="modal-header">
          <h3 class="modal-title">{{ title }}</h3>
          <button class="btn-close" @click="close">
            <font-awesome-icon icon="fa-solid fa-xmark" />
          </button>
        </header>
        
        <main class="modal-body">
          <slot></slot>
        </main>
        
        <footer class="modal-footer" v-if="$slots.footer">
          <slot name="footer"></slot>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Modal'
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:show', 'close']);

const close = () => {
  emit('update:show', false);
  emit('close');
};

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    close();
  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 48, 64, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: var(--fondo-tarjetas);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  border-radius: 16px;
  border: 1px solid var(--borde);
  box-shadow: 0 12px 24px rgba(0, 48, 64, 0.28);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: var(--fuente-principal);
}

@media (max-width: 768px) {
  .modal-container {
    width: 95%;
  }
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--borde);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--fondo-app);
}

.modal-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--texto-principal);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--texto-secundario);
  font-size: 1.2rem;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background-color: rgba(229, 62, 62, 0.1);
  color: #E53E3E;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  color: var(--texto-principal);
}

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid var(--borde);
  background-color: var(--fondo-app);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container {
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.modal-leave-active .modal-container {
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
