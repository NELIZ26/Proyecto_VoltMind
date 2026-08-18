<template>
  <div class="modal-asignar-titular">
    <BaseModal
      :show="show"
      title="ASIGNAR INSTRUCTOR TITULAR"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div v-if="ficha" class="cuerpo">
        <p class="contexto">
          Seleccione el <strong>Instructor Titular</strong> para la ficha <strong>{{ ficha.codigo }}</strong>.
          <br />El titular se usará como sugerencia rápida al programar las competencias técnicas.
        </p>

        <label class="campo">
          <span>Instructor Titular</span>
          <select v-model="form.instructor_id" class="form-input">
            <option value="">-- Sin titular asignado --</option>
            <option v-for="inst in store.instructores" :key="inst.id" :value="inst.id">
              {{ inst.nombre }}
            </option>
          </select>
        </label>

        <p v-if="error" class="banner banner-error">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ error }}
        </p>
      </div>

      <template #footer>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cancelar</button>
        <button class="btn-guardar" :disabled="guardando" @click="guardar">
          <font-awesome-icon v-if="guardando" :icon="['fas', 'circle-notch']" spin />
          <font-awesome-icon v-else icon="fa-solid fa-check" />
          {{ guardando ? 'Guardando...' : 'Asignar Titular' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useToast } from 'vue-toastification';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import { useTituladasStore } from '@/stores/tituladas';

const props = defineProps({
  show: { type: Boolean, required: true },
  ficha: { type: Object, default: null },
});
const emit = defineEmits(['update:show', 'close']);

const store = useTituladasStore();
const toast = useToast();

const error = ref('');
const guardando = ref(false);

const form = reactive({
  instructor_id: '',
});

watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    error.value = '';
    form.instructor_id = props.ficha?.instructor_titular_id || '';
  }
);

async function guardar() {
  if (guardando.value || !props.ficha) return;
  error.value = '';
  
  const fichaId = props.ficha.id;
  const instructorId = form.instructor_id;

  // Cerramos el modal inmediatamente
  emit('close');

  // Ejecutamos la acción en background
  const resultado = await store.asignarTitular(fichaId, instructorId);

  if (resultado.success) {
    toast.success('Instructor titular actualizado correctamente.');
  } else {
    toast.error('Error al asignar titular: ' + resultado.error);
  }
}
</script>

<style scoped>
.cuerpo {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.contexto {
  color: var(--texto-secundario);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}
.contexto strong {
  color: var(--texto-principal);
}
.campo {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.campo span {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.form-input {
  background: var(--fondo-oscuro);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 0.85rem;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.form-input:focus {
  border-color: var(--acento);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.15);
}
.banner-error {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.btn-guardar {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.7rem 1.4rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-guardar:hover:not(:disabled) { background: var(--sena-verde-oscuro); }

.btn-cancelar {
  background: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancelar:hover:not(:disabled) { border-color: var(--texto-secundario); }

.btn-guardar:disabled,
.btn-cancelar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
