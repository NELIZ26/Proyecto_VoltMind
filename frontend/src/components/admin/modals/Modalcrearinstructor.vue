<template>
  <BaseModal
    :show="isOpen"
    title="Crear Nuevo Instructor"
    @update:show="$emit('close')"
    @close="closeModal"
  >
    <form @submit.prevent="handleSubmit" class="form-grid" id="create-instructor-form">
      <div class="form-group">
        <label>Nombre Completo</label>
        <input v-model="form.nombre" type="text" required placeholder="Ej: Carlos Díaz" class="form-input" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Documento</label>
          <input v-model="form.documento" type="text" required placeholder="1098765432" class="form-input" />
        </div>
        <div class="form-group">
          <label>Correo</label>
          <input v-model="form.correo" type="email" required placeholder="correo@ejemplo.com" class="form-input" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Teléfono</label>
          <input v-model="form.telefono" type="tel" placeholder="+57 300..." class="form-input" />
        </div>
        <div class="form-group">
          <label>Área / Especialidad</label>
          <input v-model="form.area_especialidad" type="text" required placeholder="Ej: Desarrollo de Software" class="form-input" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Tipo de Vinculación</label>
          <select v-model="form.tipo_vinculacion" class="form-select">
            <option value="PLANTA">Planta</option>
            <option value="CONTRATISTA">Contratista</option>
          </select>
        </div>
        <div class="form-group">
          <label>Jornada</label>
          <select v-model="form.jornada" class="form-select">
            <option value="MAÑANA">Mañana</option>
            <option value="TARDE">Tarde</option>
            <option value="NOCHE">Noche</option>
            <option value="MIXTA">Mixta</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Horas Máximas Mensuales</label>
        <input v-model.number="form.max_horas_mensuales" type="number" required placeholder="160" class="form-input" />
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Inicio de Contrato</label>
          <input 
            v-model="form.fecha_inicio_contrato" 
            type="date" 
            class="form-input"
            required 
          />
        </div>

        <div class="form-group">
          <label>Fin de Contrato</label>
          <input 
            v-model="form.fecha_fin_contrato" 
            type="date" 
            class="form-input"
            required 
          />
        </div>
      </div>
    </form>

    <template #footer>
      <button class="btn-cancel" @click="closeModal">Cancelar</button>
      <button type="submit" form="create-instructor-form" class="btn-save" :disabled="isSaving">{{ isSaving ? 'Guardando...' : 'Guardar Instructor' }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { reactive, watch } from 'vue';
import BaseModal from './BaseModal.vue';

const props = defineProps({
  isOpen: Boolean,
  isSaving: Boolean
});

const emit = defineEmits(['close', 'created']);

const form = reactive({
  nombre: '',
  documento: '',
  correo: '',
  telefono: '',
  area_especialidad: '',
  tipo_vinculacion: 'PLANTA',
  jornada: 'MAÑANA',
  max_horas_mensuales: 160,
  fecha_inicio_contrato: '',
  fecha_fin_contrato: ''
});

// Limpia todos los campos del formulario
const resetForm = () => {
  form.nombre = '';
  form.documento = '';
  form.correo = '';
  form.telefono = '';
  form.area_especialidad = '';
  form.tipo_vinculacion = 'PLANTA';
  form.jornada = 'MAÑANA';
  form.max_horas_mensuales = 160;
  form.fecha_inicio_contrato = '';
  form.fecha_fin_contrato = '';
};

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      resetForm();
    }
  }
);

const closeModal = () => {
  resetForm();
  emit('close');
};

const handleSubmit = () => {
  if (props.isSaving) return;

  emit('created', { ...form });
};
</script>

<style scoped>
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--verde-principal);
  outline: none;
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.1);
}

.btn-cancel {
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 0.65rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background-color: var(--borde);
}

.btn-save {
  background-color: var(--verde-principal);
  color: #ffffff;
  border: none;
  padding: 0.65rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-save:hover {
  background-color: #2e8800;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>