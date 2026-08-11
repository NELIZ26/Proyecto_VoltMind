<template>
  <BaseModal :show="show" title="Perfil del Administrador" @close="$emit('close')">
    <div class="profile-modal-content">
      <div class="avatar-large">
        <font-awesome-icon :icon="['fas', 'user']" />
      </div>
      <h4 class="profile-name">Nelson Contreras</h4>
      <p class="profile-email">n.contreras@sena.edu.co</p>
      <hr class="divider" />
      <div class="profile-details">
        <p><strong>Rol:</strong> Administrador de Sede</p>
        <p><strong>Sede:</strong> Sede Principal Puerto Asís</p>
        <p><strong>Estado:</strong> En línea (Activo)</p>
      </div>
    </div>
    <template #footer>
      <button class="btn-secondary" @click="$emit('close')">Cerrar</button>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue';

defineProps({
  show: {
    type: Boolean,
    required: true
  }
});

defineEmits(['close']);
</script>

<style scoped>
.profile-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 9999px;
  background-color: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.875rem;
  margin-bottom: 1rem;
}

.profile-name {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
  color: var(--texto-principal);
}

.profile-email {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin: 4px 0 0 0;
}

.divider {
  width: 100%;
  border: none;
  border-top: 1px solid var(--borde);
  margin: 1rem 0;
}

.profile-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
  text-align: left;
}

.profile-details p {
  margin: 0;
  color: var(--texto-principal);
}

.btn-secondary {
  background-color: transparent;
  color: var(--texto-secundario);
  border: 1px solid var(--borde);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--borde);
  color: var(--texto-principal);
}
</style>
