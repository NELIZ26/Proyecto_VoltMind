<template>
  <BaseModal :show="show" title="Todas las Notificaciones" @close="$emit('close')">
    <div class="notifications-modal-content">
      <div class="alert-list">
        <div 
          v-for="notif in notifications" 
          :key="notif.id" 
          class="alert-item"
          :class="notif.badge === 'Fallo' ? 'danger' : 'warning'"
        >
          <div class="alert-info">
            <h5 class="alert-title">{{ notif.title }}</h5>
            <p class="alert-desc">{{ notif.desc }}</p>
            <p class="alert-status">
              Estado: {{ notif.resolved ? 'Resuelto' : 'Pendiente' }}
            </p>
          </div>
        </div>
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
  },
  notifications: {
    type: Array,
    required: true
  }
});

defineEmits(['close']);
</script>

<style scoped>
.notifications-modal-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.alert-item {
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  background-color: var(--fondo-app);
}

.alert-item.danger {
  border-left: 5px solid #C53030;
}

.alert-item.warning {
  border-left: 5px solid #B7791F;
}

.alert-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--texto-principal);
}

.alert-desc {
  margin: 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.alert-status {
  margin: 4px 0 0 0;
  font-weight: bold;
  font-size: 0.75rem;
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
