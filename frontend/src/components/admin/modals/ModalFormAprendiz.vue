<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <header class="modal-header">
        <h2>
          <font-awesome-icon icon="fa-solid fa-user-plus" />
          Registrar Nuevo Aprendiz
        </h2>
        <button class="btn-close" @click="closeModal">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </header>

      <div class="modal-body">
        <p class="modal-subtitle">Ingrese los datos del nuevo aprendiz para registrarlo en el sistema.</p>

        <form @submit.prevent="saveData" class="form-grid">
          <div class="form-group">
            <label>Nombres</label>
            <input type="text" v-model="formData.nombres" class="form-input" placeholder="Nombres completos" required />
          </div>
          
          <div class="form-group">
            <label>Apellidos</label>
            <input type="text" v-model="formData.apellidos" class="form-input" placeholder="Apellidos completos" required />
          </div>

          <div class="form-group">
            <label>Tipo de Documento</label>
            <select v-model="formData.tipoDocumento" class="form-input" required>
              <option value="CC">Cédula de Ciudadanía</option>
              <option value="TI">Tarjeta de Identidad</option>
              <option value="CE">Cédula de Extranjería</option>
              <option value="PEP">PEP</option>
            </select>
          </div>

          <div class="form-group">
            <label>Número de Documento</label>
            <input type="text" v-model="formData.documento" class="form-input" placeholder="Ej. 1000222333" required />
          </div>

          <div class="form-group full-width">
            <label>Ficha</label>
            <select v-model="formData.ficha" class="form-input" required>
              <option value="" disabled>Seleccione una ficha</option>
              <option value="2693821">2693821 - ADSO</option>
              <option value="2693822">2693822 - ADSO</option>
            </select>
          </div>

          <div class="form-group full-width">
            <label>Correo Electrónico Institucional</label>
            <input type="email" v-model="formData.correo" class="form-input" placeholder="correo@soy.sena.edu.co" required />
          </div>
        </form>
      </div>

      <footer class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cancelar</button>
        <button class="btn-save" @click="saveData" :disabled="!isFormValid">
          <font-awesome-icon icon="fa-solid fa-save" />
          Registrar
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['update:show', 'close', 'save']);

const formData = reactive({
  nombres: '',
  apellidos: '',
  tipoDocumento: 'CC',
  documento: '',
  ficha: '',
  correo: ''
});

const isFormValid = computed(() => {
  return (
    formData.nombres.trim() !== '' &&
    formData.apellidos.trim() !== '' &&
    formData.documento.trim() !== '' &&
    formData.ficha !== '' &&
    formData.correo.trim() !== ''
  );
});

const closeModal = () => {
  emit('close');
  emit('update:show', false);
  resetForm();
};

const saveData = () => {
  if (!isFormValid.value) return;
  emit('save', { ...formData });
  closeModal();
};

const resetForm = () => {
  formData.nombres = '';
  formData.apellidos = '';
  formData.tipoDocumento = 'CC';
  formData.documento = '';
  formData.ficha = '';
  formData.correo = '';
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
  max-width: 550px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  font-size: 1.1rem;
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

select.form-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
  padding-right: 2.5rem;
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
