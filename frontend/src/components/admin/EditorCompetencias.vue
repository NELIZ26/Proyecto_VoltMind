<template>
  <div class="editor-competencias">
    <div class="editor-encabezado">
      <span class="col-nombre">COMPETENCIA</span>
      <span class="col-tipo">TIPO</span>
      <span class="col-horas">HORAS</span>
      <span class="col-quitar"></span>
    </div>

    <div v-for="(c, indice) in filas" :key="c._clave" class="editor-fila">
      <span class="franja" :style="{ background: colorTipo(c.tipo) }"></span>
      <input
        v-model.trim="c.nombre"
        type="text"
        class="form-input col-nombre"
        placeholder="Nombre de la competencia (como está en Sofía Plus)"
        @input="emitir"
      />
      <select v-model="c.tipo" class="form-input col-tipo" @change="emitir">
        <option v-for="t in TIPOS_COMPETENCIA" :key="t" :value="t">{{ t }}</option>
      </select>
      <input
        v-model.number="c.horas"
        type="number"
        min="1"
        max="2000"
        class="form-input col-horas"
        @input="emitir"
      />
      <button
        class="btn-quitar col-quitar"
        type="button"
        title="Quitar esta competencia"
        @click="quitar(indice)"
      >
        <font-awesome-icon icon="fa-solid fa-xmark" />
      </button>
    </div>

    <div class="editor-pie">
      <button class="btn-agregar" type="button" @click="agregar">
        <font-awesome-icon icon="fa-solid fa-plus" /> Agregar competencia
      </button>
      <span class="total">
        Total del programa: <strong>{{ totalHoras }} h</strong>
        · {{ filas.length }} {{ filas.length === 1 ? 'competencia' : 'competencias' }}
      </span>
    </div>
  </div>
</template>

<script setup>
// Editor de la matriz de diagnóstico (competencia + tipo + horas). Lo comparten
// el modal de diagnóstico de la ficha y el catálogo de programas.
import { ref, computed, watch } from 'vue';
import { COLORES_TIPO_COMPETENCIA, TIPOS_COMPETENCIA } from '@/stores/tituladas';

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});
const emit = defineEmits(['update:modelValue']);

let contadorClaves = 0;
const nuevaFila = (base = {}) => ({
  _clave: `fila-${contadorClaves++}`,
  id: base.id || null,
  nombre: base.nombre || '',
  tipo: base.tipo || 'Técnica',
  horas: base.horas || null,
});

const filas = ref(props.modelValue.map(nuevaFila));

// Si el padre reinicia el listado (p. ej. al reabrir el modal), se re-sincroniza
watch(
  () => props.modelValue,
  (nuevas) => {
    const actuales = filas.value.map(({ id, nombre, tipo, horas }) => ({ id, nombre, tipo, horas }));
    if (JSON.stringify(actuales) !== JSON.stringify(nuevas)) {
      filas.value = (nuevas || []).map(nuevaFila);
    }
  },
  { deep: true }
);

const totalHoras = computed(() =>
  filas.value.reduce((suma, c) => suma + (Number(c.horas) || 0), 0)
);

const colorTipo = (tipo) => COLORES_TIPO_COMPETENCIA[tipo] || 'var(--borde)';

const emitir = () => {
  emit(
    'update:modelValue',
    filas.value.map(({ id, nombre, tipo, horas }) => ({ id, nombre, tipo, horas }))
  );
};

const agregar = () => {
  filas.value.push(nuevaFila());
  emitir();
};

const quitar = (indice) => {
  filas.value.splice(indice, 1);
  emitir();
};
</script>

<style scoped>
.editor-competencias {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-encabezado {
  display: grid;
  grid-template-columns: 10px 1fr 130px 90px 34px;
  gap: 8px;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  padding: 0 2px;
}

.editor-encabezado .col-nombre { grid-column: 2; }

.editor-fila {
  display: grid;
  grid-template-columns: 10px 1fr 130px 90px 34px;
  gap: 8px;
  align-items: center;
}

.franja {
  width: 4px;
  height: 30px;
  border-radius: 2px;
  justify-self: center;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.5rem 0.7rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.8rem;
  outline: none;
  box-sizing: border-box;
  width: 100%;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.col-tipo { cursor: pointer; }
.col-horas { text-align: center; }

.btn-quitar {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  width: 30px;
  height: 30px;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-quitar:hover { border-color: #e53e3e; color: #e53e3e; }

.editor-pie {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.btn-agregar {
  background: transparent;
  border: 1px dashed var(--borde);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-agregar:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.total {
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.total strong { color: var(--sena-verde); }
</style>
