<template>
  <BaseModal
    :show="show"
    title="Asignar Device ID (NFC/IoT)"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="form-grid">
      <div class="user-info-box" v-if="aprendizData">
        <p class="user-name"><strong>{{ aprendizData.nombre }}</strong></p>
        <p class="user-doc">Doc: {{ aprendizData.documento }} - Ficha: {{ aprendizData.ficha }}</p>
      </div>

      <div class="form-group">
        <label>Código o Mac Address del Dispositivo</label>
        <div class="input-with-icon">
          <font-awesome-icon icon="fa-solid fa-microchip" class="input-icon" />
          <input 
            type="text" 
            class="form-input with-icon" 
            v-model="deviceId" 
            required 
            placeholder="Ej: A1:B2:C3:D4:E5" 
          />
        </div>
      </div>
    </form>

    <template #footer>
      <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
      <button class="btn-save" @click="handleSubmit">Vincular Dispositivo</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import BaseModal from './BaseModal.vue';

const props = defineProps({
  show: Boolean,
  aprendizData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close', 'save']);

const deviceId = ref('');

watch(() => props.show, (newVal) => {
  if (newVal) {
    deviceId.value = props.aprendizData?.deviceId || '';
  }
});

const handleSubmit = () => {
  if (!deviceId.value) return;
  emit('save', deviceId.value);
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
  background-color: rgba(80, 229, 249, 0.1);
  border: 1px solid var(--sena-azul-claro);
  padding: 1rem;
  border-radius: 8px;
}

[data-theme="dark"] .user-info-box {
  border-color: #81d4fa;
}

.user-name {
  margin: 0;
  font-size: 1rem;
  color: var(--texto-principal);
}

.user-doc {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
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

.form-input.with-icon {
  padding-left: 2.5rem;
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
