<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <header class="modal-header">
        <h2>
          <font-awesome-icon icon="fa-solid fa-users" />
          Vincular Aprendices
        </h2>
        <button class="btn-close" @click="closeModal">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </header>

      <div class="modal-body">
        <p class="modal-subtitle" v-if="fichaData">Ficha: <strong>{{ fichaData?.code }} - {{ fichaData?.name }}</strong></p>

        <div class="method-selector">
          <label class="radio-label">
            <input type="radio" v-model="uploadMethod" value="manual" />
            Registro Manual
          </label>
          <label class="radio-label">
            <input type="radio" v-model="uploadMethod" value="xml" />
            Carga por Archivo (XML)
          </label>
        </div>

        <!-- Registro Manual -->
        <div v-if="uploadMethod === 'manual'" class="manual-form">
          <div class="form-group">
            <label>Tipo de Documento</label>
            <select v-model="manualData.docType" class="form-input">
              <option value="CC">Cédula de Ciudadanía</option>
              <option value="TI">Tarjeta de Identidad</option>
              <option value="CE">Cédula de Extranjería</option>
            </select>
          </div>
          <div class="form-group">
            <label>Número de Documento</label>
            <input type="text" v-model="manualData.docNumber" class="form-input" placeholder="Ej. 1000222333" />
          </div>
          <div class="form-group">
            <label>Nombres</label>
            <input type="text" v-model="manualData.names" class="form-input" placeholder="Nombres del aprendiz" />
          </div>
          <div class="form-group">
            <label>Apellidos</label>
            <input type="text" v-model="manualData.lastNames" class="form-input" placeholder="Apellidos del aprendiz" />
          </div>
          <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" v-model="manualData.email" class="form-input" placeholder="correo@soy.sena.edu.co" />
          </div>
        </div>

        <!-- Carga XML -->
        <div v-if="uploadMethod === 'xml'" class="xml-upload">
          <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
            <font-awesome-icon icon="fa-solid fa-file-arrow-up" class="upload-icon" />
            <p>Haz clic o arrastra un archivo <strong>.xml</strong> aquí</p>
            <input 
              type="file" 
              ref="fileInput" 
              accept=".xml" 
              class="hidden-input" 
              @change="handleFileChange" 
            />
          </div>
          <div v-if="selectedFile" class="selected-file">
            <font-awesome-icon icon="fa-solid fa-file-code" />
            <span>{{ selectedFile.name }}</span>
            <button class="btn-remove-file" @click="selectedFile = null">
              <font-awesome-icon icon="fa-solid fa-times" />
            </button>
          </div>
        </div>
      </div>

      <footer class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cancelar</button>
        <button class="btn-save" @click="saveData" :disabled="!isFormValid">
          <font-awesome-icon icon="fa-solid fa-save" />
          Vincular
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  fichaData: Object
});

const emit = defineEmits(['update:show', 'close', 'save']);

const uploadMethod = ref('manual');
const fileInput = ref(null);
const selectedFile = ref(null);

const manualData = reactive({
  docType: 'CC',
  docNumber: '',
  names: '',
  lastNames: '',
  email: ''
});

const isFormValid = computed(() => {
  if (uploadMethod.value === 'xml') {
    return selectedFile.value !== null;
  }
  return (
    manualData.docNumber.trim() !== '' &&
    manualData.names.trim() !== '' &&
    manualData.lastNames.trim() !== '' &&
    manualData.email.trim() !== ''
  );
});

const closeModal = () => {
  emit('close');
  emit('update:show', false);
  resetForm();
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file && file.name.endsWith('.xml')) {
    selectedFile.value = file;
  } else {
    alert('Por favor selecciona un archivo XML válido.');
  }
};

const handleDrop = (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.xml')) {
    selectedFile.value = file;
  } else {
    alert('Por favor arrastra un archivo XML válido.');
  }
};

const saveData = () => {
  if (uploadMethod.value === 'xml') {
    emit('save', { method: 'xml', file: selectedFile.value, ficha: props.fichaData });
  } else {
    emit('save', { method: 'manual', data: { ...manualData }, ficha: props.fichaData });
  }
  closeModal();
};

const resetForm = () => {
  uploadMethod.value = 'manual';
  selectedFile.value = null;
  manualData.docType = 'CC';
  manualData.docNumber = '';
  manualData.names = '';
  manualData.lastNames = '';
  manualData.email = '';
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
  background: var(--fondo-app, #ffffff);
  width: 100%;
  max-width: 500px;
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

.method-selector {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  color: var(--texto-principal, #333);
}

.form-group {
  margin-bottom: 1rem;
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

.upload-area {
  border: 2px dashed var(--borde, #e0e0e0);
  border-radius: 12px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--fondo-tarjetas, #ffffff);
}

.upload-area:hover {
  border-color: var(--sena-verde, #39a900);
  background: rgba(57, 169, 0, 0.02);
}

.upload-icon {
  font-size: 2.5rem;
  color: var(--sena-verde, #39a900);
  margin-bottom: 1rem;
}

.hidden-input {
  display: none;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(57, 169, 0, 0.1);
  border: 1px solid rgba(57, 169, 0, 0.2);
  border-radius: 8px;
  color: var(--sena-verde-oscuro, #2e8b57);
  font-size: 0.9rem;
  font-weight: 600;
}

.btn-remove-file {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--sena-verde-oscuro, #2e8b57);
  cursor: pointer;
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
