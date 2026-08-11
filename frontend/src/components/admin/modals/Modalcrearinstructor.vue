<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
    <!-- Encabezado -->
<div class="modal-header">
  <h2 class="modal-title">Crear Nuevo Instructor</h2>
  <button type="button" class="btn-close" @click="closeModal" aria-label="Cerrar">
    &times;
  </button>
</div>




      <form @submit.prevent="handleSubmit" class="modal-body">
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

        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="closeModal">Cancelar</button>
          <button type="submit" class="btn-primary">Guardar Instructor</button>
        </div>
      </form>
    </div>
  </div>
  
</template>

<script setup>
import { reactive } from 'vue';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close', 'created']);

const form = reactive({
  nombre: '',
  documento: '',
  correo: '',
  telefono: '',
  area_especialidad: '',
  tipo_vinculacion: 'PLANTA',
  jornada: 'Manana',
  max_horas_mensuales: 160,
  fecha_inicio_contrato: '',
  fecha_fin_contrato: ''
});

const closeModal = () => {
  emit('close');
};

const handleSubmit = () => {
  // Aquí se enviarán los datos a la API o al Store
  emit('created', { ...form });
  closeModal();

};

</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-card {
  background-color: #1e1e1e;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  width: 90%;
  max-width: 580px;
  padding: 1.8rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: #ffffff;
}

.btn-close {
  background: transparent !important;
  border: none !important;
  font-size: 1.6rem !important;
  line-height: 1 !important;
  color: #9ca3af !important;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #ffffff !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group.full-width {
  width: 100%;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #d1d5db;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background-color: #2a2a2a;
  border: 1px solid #3d3d3d;
  color: #ffffff;
  font-size: 0.9rem;
  box-sizing: border-box;
  outline: none;
}

.form-input:focus,
.form-select:focus {
  border-color: #39a900;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1.8rem;
}

.btn-cancel {
  background-color: #383838 !important;
  border: 1px solid #4a4a4a !important;
  color: #ffffff !important;
  padding: 0.65rem 1.4rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
}

.btn-cancel:hover {
  background-color: #4a4a4a !important;
}

.btn-submit {
  background-color: #39a900 !important;
  color: #ffffff !important;
  border: none !important;
  padding: 0.65rem 1.4rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
}

.btn-submit:hover {
  background-color: #2e8800 !important;
}

/* Modo claro automático */
:global(.light) .modal-card,
:global(.light-mode) .modal-card {
  background-color: #ffffff !important;
  color: #1f2937 !important;
  border-color: #e5e7eb !important;
}

:global(.light) .modal-title,
:global(.light-mode) .modal-title,
:global(.light) .form-group label,
:global(.light-mode) .form-group label {
  color: #1f2937 !important;
}

:global(.light) .form-input,
:global(.light-mode) .form-input,
:global(.light) .form-select,
:global(.light-mode) .form-select {
  background-color: #f9fafb !important;
  border-color: #d1d5db !important;
  color: #111827 !important;
}

:global(.light) .btn-close,
:global(.light-mode) .btn-close {
  color: #6b7280 !important;
}

:global(.light) .btn-cancel,
:global(.light-mode) .btn-cancel {
  background-color: #e5e7eb !important;
  border-color: #d1d5db !important;
  color: #374151 !important;
}
</style>