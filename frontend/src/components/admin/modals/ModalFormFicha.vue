<template>
  <BaseModal
    :show="show"
    :title="fichaData ? 'Editar Ficha' : 'Nueva Ficha'"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="form-grid">
      <div class="form-group">
        <label>Código de Ficha</label>
        <input type="text" class="form-input" v-model="formData.code" required placeholder="Ej: 2693821" />
      </div>
      
      <div class="form-group">
        <label>Programa de Formación</label>
        <input type="text" class="form-input" v-model="formData.name" required placeholder="Ej: Análisis y Desarrollo..." />
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Fecha Inicio</label>
          <input type="date" class="form-input" v-model="formData.startDate" required />
        </div>
        <div class="form-group">
          <label>Fecha Fin</label>
          <input type="date" class="form-input" v-model="formData.endDate" required />
        </div>
      </div>
      
      <div class="form-group">
        <label>Estado Operativo</label>
        <select class="form-input" v-model="formData.status">
          <option value="En Lectiva">En Lectiva</option>
          <option value="En Productiva">En Productiva</option>
          <option value="Terminada">Terminada</option>
        </select>
      </div>
    </form>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
      <button class="btn-save" @click="handleSubmit">Guardar Ficha</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { reactive, watch, defineProps, defineEmits } from 'vue';
import BaseModal from './BaseModal.vue';

const props = defineProps({
  show: Boolean,
  fichaData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close', 'save']);

const formData = reactive({
  code: '',
  name: '',
  startDate: '',
  endDate: '',
  status: 'En Lectiva'
});

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.fichaData) {
      Object.assign(formData, props.fichaData);
    } else {
      // Reset
      Object.assign(formData, { code: '', name: '', startDate: '', endDate: '', status: 'En Lectiva' });
    }
  }
});

const handleSubmit = () => {
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

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row > .form-group {
  flex: 1;
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
