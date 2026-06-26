<template>
  <BaseModal
    :show="show"
    title="Confirmar Acción"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <div class="confirm-content">
      <div class="warning-icon">
        <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
      </div>
      <p class="confirm-message">{{ message }}</p>
    </div>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
      <button class="btn-danger" @click="handleConfirm">Confirmar</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import BaseModal from './BaseModal.vue';

const props = defineProps({
  show: Boolean,
  message: {
    type: String,
    default: '¿Estás seguro de realizar esta acción?'
  }
});

const emit = defineEmits(['update:show', 'close', 'confirm']);

const handleConfirm = () => {
  emit('confirm');
  emit('close');
};
</script>

<style scoped>
.confirm-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.5rem;
  padding: 1rem 0;
}

.warning-icon {
  font-size: 3rem;
  color: #E53E3E;
}

.confirm-message {
  font-size: 1rem;
  font-weight: 600;
  color: var(--texto-principal);
  margin: 0;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: var(--fondo-app);
}

.btn-danger {
  background: #E53E3E;
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.2);
}

.btn-danger:hover {
  background: #C53030;
  transform: translateY(-2px);
}
</style>
