<template>
  <BaseModal :show="show" title="Historial Completo de Actividades" @close="$emit('close')">
    <div class="activities-modal-content">
      <div class="activity-history-list">
        <div 
          v-for="act in activities" 
          :key="act.id" 
          class="activity-history-item"
        >
          <div class="activity-header">
            <span class="activity-time">{{ act.timestamp }}</span>
            <span :class="['status-badge', act.statusClass]">{{ act.statusText }}</span>
          </div>
          <div class="activity-details">
            <p><strong>Ubicación:</strong> {{ act.campus }} — {{ act.room }}</p>
            <p><strong>Instructor:</strong> {{ act.instructor }}</p>
            <p><strong>Evento:</strong> {{ act.event }}</p>
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
  activities: {
    type: Array,
    required: true
  }
});

defineEmits(['close']);
</script>

<style scoped>
.activities-modal-content {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.activity-history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.activity-history-item {
  border-bottom: 1px solid var(--borde);
  padding-bottom: 12px;
}

.activity-history-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.activity-time {
  font-family: monospace;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  font-weight: bold;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
}

.status-green {
  background-color: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
}

.status-orange {
  background-color: rgba(253, 195, 0, 0.1);
  color: var(--sena-naranja);
}

.status-red {
  background-color: rgba(229, 62, 62, 0.1);
  color: #E53E3E;
}

.activity-details p {
  margin: 4px 0;
  font-size: 0.85rem;
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
