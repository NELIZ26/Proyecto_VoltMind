<template>
  <BaseModal
    :show="show"
    title="Registrar Módulo ESP32"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="form-grid">
      <div class="form-group">
        <label>Nombre del Módulo</label>
        <input 
          type="text" 
          class="form-input" 
          v-model="formData.name" 
          required 
          placeholder="Ej: ESP32 - Control Luces" 
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>MAC Address</label>
          <input 
            type="text" 
            class="form-input" 
            v-model="formData.mac" 
            required 
            placeholder="AA:BB:CC:DD:EE:FF" 
          />
        </div>
        <div class="form-group">
          <label>Dirección IP</label>
          <input 
            type="text" 
            class="form-input" 
            v-model="formData.ip" 
            required 
            placeholder="192.168.1.X" 
          />
        </div>
      </div>
      
      <div class="form-group">
        <label>Ambiente de Asignación</label>
        <select class="form-input" v-model="formData.room" required>
          <option value="">Seleccione un Ambiente...</option>
          <option value="Ambiente 401">Ambiente 401</option>
          <option value="Ambiente 402">Ambiente 402</option>
          <option value="Laboratorio de Redes">Laboratorio de Redes</option>
          <option value="Sala de Bilingüismo">Sala de Bilingüismo</option>
        </select>
      </div>
    </form>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
      <button class="btn-save" @click="handleSubmit">Registrar Módulo</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { reactive, watch, defineProps, defineEmits } from 'vue';
import BaseModal from './BaseModal.vue';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['update:show', 'close', 'save']);

const formData = reactive({
  name: '',
  mac: '',
  ip: '',
  room: ''
});

watch(() => props.show, (newVal) => {
  if (newVal) {
    Object.assign(formData, { name: '', mac: '', ip: '', room: '' });
  }
});

const handleSubmit = () => {
  if (!formData.name || !formData.mac) return;
  emit('save', { 
    ...formData, 
    id: Date.now(), 
    lastPing: 'Recién agregado', 
    online: true, 
    powerOn: false 
  });
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
