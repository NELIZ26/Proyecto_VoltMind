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
        <input v-model="form.nombre_completo" type="text" required placeholder="Ej: Carlos Díaz" class="form-input" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Documento</label>
          <input v-model="form.nro_documento" type="text" required placeholder="1098765432" class="form-input" />
        </div>
        <div class="form-group">
          <label>Correo Institucional</label>
          <input v-model="form.correo_institucional" type="email" required placeholder="correo@ejemplo.com" class="form-input" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Contacto (Teléfono)</label>
          <input v-model="form.nro_telefono" type="text" placeholder="3000000000" class="form-input" />
        </div>
        <div class="form-group">
          <label>Perfil Profesional</label>
          <input v-model="form.perfil_profesional" type="text" required placeholder="Ej: Desarrollo de Software" class="form-input" />
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
          <label>Municipio Contratación</label>
          <input v-model="form.municipio_contratacion" type="text" placeholder="Ej: Bogotá" class="form-input" />
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Inicio de Contrato</label>
          <input 
            v-model="form.fecha_inicio_contrato" 
            type="date" 
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Fin de Contrato</label>
          <input 
            v-model="form.fecha_fin_contrato" 
            type="date" 
            class="form-input"
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
  nombre_completo: '',
  nro_documento: '',
  correo_institucional: '',
  nro_telefono: '',
  perfil_profesional: '',
  tipo_vinculacion: 'PLANTA',
  municipio_contratacion: '',
  fecha_inicio_contrato: '',
  fecha_fin_contrato: ''
});

// Limpia todos los campos del formulario
const resetForm = () => {
  form.nombre_completo = '';
  form.nro_documento = '';
  form.correo_institucional = '';
  form.nro_telefono = '';
  form.perfil_profesional = '';
  form.tipo_vinculacion = 'PLANTA';
  form.municipio_contratacion = '';
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