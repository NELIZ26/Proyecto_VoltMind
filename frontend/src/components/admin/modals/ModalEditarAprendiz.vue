<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <header class="modal-header">
        <h2>
          <font-awesome-icon icon="fa-solid fa-pen-to-square" />
          Editar Aprendiz y Dispositivo
        </h2>
        <button class="btn-close" @click="closeModal">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </header>

      <div class="modal-body">
        <p class="modal-subtitle">Actualice la información del aprendiz y su vinculación IoT.</p>

        <form @submit.prevent="saveData" class="form-grid">
          <!-- Información Básica -->
          <div class="form-section-title full-width">
            <h3>Información del Aprendiz</h3>
            <hr />
          </div>

          <div class="form-group full-width">
            <label>Nombre Completo</label>
            <input type="text" v-model="formData.nombre" class="form-input" required />
          </div>

          <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" v-model="formData.correo" class="form-input" required />
          </div>

          <div class="form-group">
            <label>Teléfono</label>
            <input type="text" v-model="formData.telefono" class="form-input" />
          </div>

          <!-- Asignación Formativa -->
          <div class="form-section-title full-width" style="margin-top: 1rem;">
            <h3>Asignación Formativa</h3>
            <hr />
          </div>

          <div class="form-group">
            <label>Instructor Asignado</label>
            <input type="text" v-model="formData.instructor" class="form-input" placeholder="Ej: Inst. Marlon Monsalve" />
          </div>

          <div class="form-group">
            <label>Ambiente Asignado</label>
            <input type="text" v-model="formData.ambiente" class="form-input" placeholder="Ej: Sala 105 - sistemas" />
          </div>

          <!-- Dispositivo IoT -->
          <div class="form-section-title full-width" style="margin-top: 1rem;">
            <h3>Dispositivo IoT (MAC/ID)</h3>
            <hr />
          </div>

          <div class="form-group full-width">
            <label>Código o Mac Address del Dispositivo</label>
            <div class="input-with-icon">
              <font-awesome-icon icon="fa-solid fa-microchip" class="input-icon" />
              <input 
                type="text" 
                class="form-input with-icon" 
                v-model="formData.deviceId" 
                placeholder="Dejar en blanco para desvincular" 
              />
            </div>
          </div>

          <div class="form-group full-width" v-if="formData.deviceId">
            <label>Fecha de Asignación</label>
            <input type="date" v-model="formData.assignDate" class="form-input" />
          </div>

        </form>
      </div>

      <footer class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cancelar</button>
        <button class="btn-save" @click="saveData" :disabled="!isFormValid">
          <font-awesome-icon icon="fa-solid fa-save" />
          Guardar Cambios
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  aprendizData: Object
});

const emit = defineEmits(['update:show', 'close', 'save']);

const formData = reactive({
  nombre: '',
  correo: '',
  telefono: '',
  instructor: '',
  ambiente: '',
  deviceId: '',
  assignDate: ''
});

// Helper to convert DD/MM/YYYY to YYYY-MM-DD for date input
const formatDateForInput = (dateStr) => {
  if (!dateStr || !dateStr.includes('/')) return dateStr;
  const parts = dateStr.split('/');
  if (parts.length === 3) {
    return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
  }
  return dateStr;
};

// Helper to convert YYYY-MM-DD back to DD/MM/YYYY
const formatDateForSave = (dateStr) => {
  if (!dateStr || !dateStr.includes('-')) return dateStr;
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
};

watch(() => props.show, (newVal) => {
  if (newVal && props.aprendizData) {
    formData.nombre = props.aprendizData.nombre || '';
    formData.correo = props.aprendizData.correo || '';
    formData.telefono = props.aprendizData.telefono || '';
    formData.instructor = props.aprendizData.instructor || 'Inst. Marlon Monsalve';
    formData.ambiente = props.aprendizData.ambiente || 'Sala 105 - sistema';
    formData.deviceId = props.aprendizData.deviceId || '';
    formData.assignDate = props.aprendizData.assignDate ? formatDateForInput(props.aprendizData.assignDate) : new Date().toISOString().split('T')[0];
  }
});

const isFormValid = computed(() => {
  return formData.nombre.trim() !== '' && formData.correo.trim() !== '';
});

const closeModal = () => {
  emit('close');
  emit('update:show', false);
};

const saveData = () => {
  if (!isFormValid.value) return;
  
  const payload = {
    ...formData,
    documento: props.aprendizData.documento,
    assignDate: formData.deviceId ? formatDateForSave(formData.assignDate) : null
  };
  
  // If user cleared the deviceID, set to null
  if (!payload.deviceId || payload.deviceId.trim() === '') {
    payload.deviceId = null;
  }

  emit('save', payload);
  closeModal();
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 48, 64, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--fondo-tarjetas, #ffffff);
  width: 100%;
  max-width: 600px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-bottom: 1px solid var(--borde, #e0e0e0);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--sena-azul-oscuro, #00324b);
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--texto-secundario, #666);
  cursor: pointer;
  transition: color 0.2s;
}

.btn-close:hover {
  color: var(--sena-rojo, #d32f2f);
}

.modal-body {
  padding: 1.5rem;
  background: var(--fondo-app, #f8fafc);
  flex: 1;
  overflow-y: auto;
}

.modal-subtitle {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--texto-secundario, #666);
  font-size: 0.9rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.full-width {
  grid-column: 1 / -1;
}

.form-section-title h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--sena-azul-oscuro);
  font-weight: 700;
}

.form-section-title hr {
  margin: 8px 0 0 0;
  border: none;
  border-top: 1px solid var(--borde);
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-secundario, #666);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 0.65rem;
  border: 1px solid var(--borde, #e0e0e0);
  border-radius: 8px;
  background: var(--fondo-tarjetas, #ffffff);
  color: var(--texto-principal, #333);
  font-family: inherit;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--sena-verde, #39a900);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.input-with-icon {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
}

.form-input.with-icon {
  padding-left: 2.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-top: 1px solid var(--borde, #e0e0e0);
}

.btn-cancel {
  background: none;
  border: 1px solid var(--borde, #e0e0e0);
  color: var(--texto-secundario, #666);
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel:hover {
  background: var(--fondo-app, #f8fafc);
}

.btn-save {
  background: var(--sena-verde, #39a900);
  color: white;
  border: none;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: var(--sena-verde-oscuro, #2e8b57);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
