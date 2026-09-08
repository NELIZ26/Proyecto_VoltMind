<template>
  <div class="modal-diagnostico">
    <BaseModal
      :show="show"
      title="MATRIZ DE DIAGNÓSTICO DE COMPETENCIAS"
      :closeOnBackdrop="false"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div v-if="ficha" class="cuerpo" style="position: relative;">
        <!-- Bloqueo y Spinner Overlay -->
        <div v-if="guardando" class="overlay-bloqueo">
          <font-awesome-icon icon="fa-solid fa-circle-notch" spin class="spinner-grande" />
          <p>Guardando matriz de horas...</p>
        </div>

        <p class="contexto">
          Ficha <strong>{{ ficha.codigo }}</strong> • {{ ficha.programa }}.
        </p>



        <EditorCompetencias v-model="competencias" />

        <p v-if="error" class="banner banner-error">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ error }}
        </p>
        <p class="banner banner-info">
          <font-awesome-icon icon="fa-solid fa-circle-info" />
          Las competencias que ya tienen asignaciones en el calendario no se pueden eliminar.
        </p>
      </div>

      <template #footer>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cancelar</button>
        <button class="btn-guardar" :disabled="guardando" @click="guardar">
          <font-awesome-icon v-if="guardando" icon="fa-solid fa-circle-notch" spin />
          <font-awesome-icon v-else icon="fa-solid fa-check" />
          {{ guardando ? 'Guardando...' : 'Guardar diagnóstico' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
// Registro/edición de la matriz de diagnóstico de una ficha titulada:
// es el punto de partida del flujo real (sin diagnóstico no hay programación).
import { ref, watch } from 'vue';
import { useToast } from 'vue-toastification';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import EditorCompetencias from '@/components/admin/EditorCompetencias.vue';
import { useTituladasStore } from '@/stores/tituladas';

const props = defineProps({
  show: { type: Boolean, required: true },
  ficha: { type: Object, default: null },
});
const emit = defineEmits(['update:show', 'close']);

const store = useTituladasStore();
const toast = useToast();

const competencias = ref([]);
const competenciasOriginal = ref('');
const error = ref('');
const guardando = ref(false);

// Al abrir, se carga la matriz actual de la ficha
watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    error.value = '';
    competencias.value = (props.ficha?.diagnostico || []).map(({ id, nombre, tipo, horas }) => ({
      id, nombre, tipo, horas,
    }));
    // Guardar copia exacta de cómo llegó la información
    competenciasOriginal.value = JSON.stringify(competencias.value);
  }
);

async function guardar() {
  if (guardando.value) return; // Previene doble clic
  error.value = '';
  const filas = competencias.value;

  // Si no se hizo ningún cambio, cerramos el modal silenciosamente sin gastar servidor
  if (JSON.stringify(filas) === competenciasOriginal.value) {
    emit('close');
    return;
  }
  if (!filas.length) {
    error.value = 'Agregue al menos una competencia a la matriz.';
    return;
  }
  
  // Validar nombre (mínimo 3 letras)
  const sinNombre = filas.find((c) => !c.nombre || c.nombre.trim().length < 3);
  if (sinNombre) {
    error.value = 'Cada competencia necesita un nombre válido (mínimo 3 caracteres).';
    return;
  }
  
  // Validar horas >= 0
  const sinHoras = filas.find((c) => c.horas === null || c.horas === undefined || c.horas < 0);
  if (sinHoras) {
    error.value = 'Las horas de las competencias no pueden ser negativas ni estar vacías (pueden ser 0).';
    return;
  }

  guardando.value = true;
  const start = Date.now();
  const resultado = await store.actualizarDiagnostico(props.ficha.id, filas);
  const elapsed = Date.now() - start;
  if (elapsed < 500) {
    await new Promise(r => setTimeout(r, 500 - elapsed));
  }
  guardando.value = false;

  if (resultado.success) {
    toast.success('Diagnóstico guardado: la ficha ya se puede programar.');
    emit('close');
  } else {
    error.value = resultado.error;
  }
}
</script>

<style scoped>
.modal-diagnostico :deep(.modal-container) {
  max-width: 760px;
}

.cuerpo {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.contexto {
  margin: 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-left: 4px solid var(--sena-verde);
  border-radius: 10px;
  padding: 0.7rem 1rem;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.83rem;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.banner {
  margin: 0;
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.banner-error {
  background: rgba(229, 62, 62, 0.1);
  border: 1px solid rgba(229, 62, 62, 0.4);
  color: #c53030;
}

[data-theme="dark"] .banner-error { color: #fc8181; }

.nota {
  margin: 0;
  font-size: 0.72rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
  font-style: italic;
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

.overlay-bloqueo {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  backdrop-filter: blur(2px);
}

.spinner-grande {
  font-size: 3rem;
  color: var(--sena-verde);
  margin-bottom: 1rem;
}
</style>
