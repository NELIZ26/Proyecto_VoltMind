<template>
  <div class="modal-diagnostico">
    <BaseModal
      :show="show"
      title="MATRIZ DE DIAGNÓSTICO DE COMPETENCIAS"
      :closeOnBackdrop="false"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div v-if="ficha" class="cuerpo">
        <p class="contexto">
          Ficha <strong>{{ ficha.codigo }}</strong> · {{ ficha.programa }} — registre aquí la
          matriz que envía el instructor titular: competencia, clasificación y horas del programa.
          <strong>Sin este diagnóstico la ficha no se puede programar.</strong>
        </p>

        <!-- Cargar la matriz desde el catálogo de programas -->
        <div class="fila-catalogo">
          <label class="campo-catalogo">
            <span>Cargar competencias desde el catálogo (opcional)</span>
            <select v-model="programaElegido" class="form-input">
              <option value="">Mantener la matriz actual...</option>
              <option v-for="p in store.programas" :key="p.id" :value="p.id">
                {{ p.nombre }} — versión {{ p.version }} ({{ p.nivel }} · {{ p.total_horas }} h)
              </option>
            </select>
          </label>
        </div>

        <EditorCompetencias v-model="competencias" />

        <p v-if="error" class="banner banner-error">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ error }}
        </p>
        <p class="nota">
          <font-awesome-icon icon="fa-solid fa-circle-info" />
          Las competencias que ya tienen asignaciones en el calendario no se pueden eliminar.
        </p>
      </div>

      <template #footer>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cancelar</button>
        <button class="btn-guardar" :disabled="guardando" @click="guardar">
          <font-awesome-icon v-if="guardando" :icon="['fas', 'circle-notch']" spin />
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
const programaElegido = ref('');
const error = ref('');
const guardando = ref(false);

// Al abrir, se carga la matriz actual de la ficha
watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    error.value = '';
    programaElegido.value = '';
    competencias.value = (props.ficha?.diagnostico || []).map(({ id, nombre, tipo, horas }) => ({
      id, nombre, tipo, horas,
    }));
  }
);

// Elegir un programa del catálogo reemplaza las filas por su matriz
watch(programaElegido, (id) => {
  if (!id) return;
  const programa = store.programas.find((p) => p.id === id);
  if (!programa) return;
  competencias.value = programa.competencias.map(({ nombre, tipo, horas }) => ({
    id: null, nombre, tipo, horas,
  }));
});

async function guardar() {
  if (guardando.value) return; // Previene doble clic
  error.value = '';
  const filas = competencias.value;
  if (!filas.length) {
    error.value = 'Agregue al menos una competencia a la matriz.';
    return;
  }
  const invalida = filas.find((c) => !c.nombre || c.nombre.length < 3 || !c.horas || c.horas < 1);
  if (invalida) {
    error.value = 'Cada competencia necesita un nombre (mínimo 3 letras) y horas mayores a cero.';
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

.fila-catalogo { display: flex; }

.campo-catalogo {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
  flex: 1;
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
</style>
