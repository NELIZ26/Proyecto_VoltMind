<template>
  <BaseModal
    :show="show"
    title="Asignar Carga a Instructor"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="form-grid">
      <div class="user-info-box" v-if="instructorData">
        <div class="avatar-circle">
          {{ getInitials(instructorData.name) }}
        </div>
        <div class="info-texts">
          <p class="user-name"><strong>{{ instructorData.name }}</strong></p>
          <p class="user-doc">{{ instructorData.specialty }} - {{ instructorData.type }}</p>
        </div>
      </div>

      <div class="form-group">
        <label>Ficha a Asignar</label>
        <select class="form-input" v-model="formData.ficha" required>
          <option value="">Seleccione una Ficha...</option>
          <option value="2693821">2693821 - ADSO</option>
          <option value="2693822">2693822 - Multimedia</option>
          <option value="2710100">2710100 - Cocina</option>
        </select>
      </div>

      <div class="form-group">
        <label>Bloque Horario</label>
        <select class="form-input" v-model="formData.bloque" required>
          <option value="">Seleccione un Bloque...</option>
          <option v-for="bloque in configStore.bloquesHorarios" :key="bloque" :value="bloque">
            {{ bloque }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Ambiente</label>
        <select class="form-input" v-model="formData.ambiente" required>
          <option value="">Seleccione un Ambiente...</option>
          <option v-for="ambiente in store.ambientes" :key="ambiente.id" :value="ambiente.id">
            {{ ambiente.name }}
          </option>
        </select>
      </div>
    </form>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
      <button class="btn-save" @click="handleSubmit">Asignar Horario</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { reactive, watch, defineProps, defineEmits, onMounted } from 'vue';
import BaseModal from './BaseModal.vue';
import { useProgramacionStore } from '@/stores/programacion';
import { useConfigStore } from '@/stores/config';

const store = useProgramacionStore();
const configStore = useConfigStore();

onMounted(() => {
  store.initStore();
});

const props = defineProps({
  show: Boolean,
  instructorData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close', 'save']);

const formData = reactive({
  ficha: '',
  bloque: '',
  ambiente: ''
});

watch(() => props.show, (newVal) => {
  if (newVal) {
    formData.ficha = '';
    formData.bloque = '';
    formData.ambiente = '';
  }
});

const getInitials = (name) => {
  if (!name) return '';
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const handleSubmit = () => {
  if (!formData.ficha || !formData.bloque || !formData.ambiente) return;
  emit('save', { ...formData });
  emit('close');
};
</script>

<style scoped>
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.user-info-box {
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
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

.btn-save {
  background: var(--sena-verde);
  border: none;
  color: var(--sena-blanco);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-save:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
}
</style>
