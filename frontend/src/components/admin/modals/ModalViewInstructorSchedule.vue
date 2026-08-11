<template>
  <BaseModal
    :show="show"
    title="Horario del Instructor"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <div class="user-info-box" v-if="instructorData">
      <div class="avatar-circle">
        {{ getInitials(instructorData.name) }}
      </div>
      <div class="info-texts">
        <p class="user-name"><strong>{{ instructorData.name }}</strong></p>
        <p class="user-doc">{{ instructorData.specialty }} - {{ instructorData.type }}</p>
      </div>
    </div>

    <div class="schedule-container" v-if="instructorSchedule.length > 0">
      <div class="schedule-card" v-for="item in instructorSchedule" :key="item.id">
        <div class="schedule-card-header">
          <span class="bloque-badge"><font-awesome-icon :icon="['fas', 'clock']" /> {{ item.bloque }}</span>
          <span class="sede-badge"><font-awesome-icon :icon="['fas', 'building']" /> Sede CAAA</span>
        </div>
        <div class="schedule-card-body">
          <div class="detail-item">
            <span class="detail-label">Ambiente:</span>
            <span class="detail-value"><strong>{{ getAmbienteName(item.ambienteId) }}</strong></span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Ficha:</span>
            <span class="detail-value">{{ item.ficha }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <font-awesome-icon :icon="['fas', 'calendar-days']" class="empty-icon" />
      <p>Este instructor aún no tiene horarios asignados.</p>
    </div>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cerrar</button>
      <button class="btn-action-green" @click="goToMatrix">Ir a Matriz General</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import BaseModal from './BaseModal.vue';
import { useProgramacionStore } from '@/stores/programacion';

const props = defineProps({
  show: Boolean,
  instructorData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close']);
const router = useRouter();
const store = useProgramacionStore();

const getInitials = (name) => {
  if (!name) return '';
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const instructorSchedule = computed(() => {
  if (!props.instructorData) return [];
  return store.schedule.filter(s => s.instructorId === props.instructorData.id);
});

const getAmbienteName = (ambienteId) => {
  const amb = store.ambientes.find(a => a.id === ambienteId);
  return amb ? amb.name : 'Desconocido';
};

const goToMatrix = () => {
  emit('close');
  if (props.instructorData) {
    router.push({ path: '/admin/ambientes', query: { q: props.instructorData.name } });
  } else {
    router.push({ path: '/admin/ambientes' });
  }
};
</script>

<style scoped>
.user-info-box {
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.5rem;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: var(--sena-verde);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
}

.user-name {
  margin: 0;
  font-size: 1rem;
  color: var(--texto-principal);
}

.user-doc {
  margin: 2px 0 0 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.schedule-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 350px;
  overflow-y: auto;
  padding-right: 5px;
}

.schedule-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  border-left: 4px solid var(--sena-verde);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.schedule-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--borde);
  padding-bottom: 0.5rem;
}

.bloque-badge {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  display: flex;
  align-items: center;
  gap: 6px;
}

.sede-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--texto-secundario);
  background: var(--fondo-app);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.schedule-card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
}

.detail-value {
  font-size: 0.95rem;
  color: var(--texto-principal);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  color: var(--texto-secundario);
  text-align: center;
}

.empty-icon {
  font-size: 2.5rem;
  color: var(--borde);
  margin-bottom: 1rem;
}

.btn-cancel {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.btn-cancel:hover {
  background: var(--borde);
}

.btn-action-green {
  background: var(--sena-verde);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.btn-action-green:hover {
  background: var(--sena-verde-oscuro);
}
</style>
