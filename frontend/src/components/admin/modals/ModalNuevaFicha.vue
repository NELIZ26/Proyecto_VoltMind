<template>
  <div class="modal-nueva-ficha">
    <BaseModal
      :show="show"
      title="NUEVA FICHA TITULADA"
      :closeOnBackdrop="false"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div class="cuerpo" :class="{ 'cuerpo-bloqueado': guardando }">
        <p class="contexto">
          La ficha nace con su <strong>diagnóstico de competencias</strong> copiado del programa
          elegido en el catálogo (el flujo real: primero la matriz, después la programación).
        </p>

        <!-- 1. Programa del catálogo -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-graduation-cap" /> 1. Programa de formación
          </h4>
          <select v-model="form.programa_id" class="form-input">
            <option value="" disabled>Seleccione el programa del catálogo...</option>
            <option v-for="p in store.programas" :key="p.id" :value="p.id">
              {{ p.nombre }} — versión {{ p.version }} ({{ p.nivel }} · {{ p.total_horas }} h)
            </option>
          </select>
          <ul v-if="programaElegido" class="vista-previa">
            <li v-for="(c, i) in programaElegido.competencias" :key="i">
              <span class="punto-color" :style="{ background: colorTipo(c.tipo) }"></span>
              {{ c.nombre }} <small>({{ c.tipo }} · {{ c.horas }} h)</small>
            </li>
          </ul>
          <p v-else class="ayuda">
            ¿El programa no está en el catálogo? Regístrelo primero con el botón
            <strong>Catálogo de programas</strong> del listado.
          </p>
        </section>

        <!-- 2. Datos de la ficha -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-clipboard-list" /> 2. Datos de la ficha
          </h4>
          <div class="rejilla">
            <label class="campo">
              <span>Código de la ficha (Sofía Plus) *</span>
              <input v-model.trim="form.codigo" type="text" class="form-input" placeholder="Ej: 3411495" />
            </label>
            <label class="campo">
              <span>Jornada *</span>
              <select v-model="form.jornada" class="form-input">
                <option value="" disabled>Seleccione...</option>
                <option v-for="j in JORNADAS_TITULADAS" :key="j.valor" :value="j.valor">
                  {{ j.valor }} ({{ j.horario }})
                </option>
              </select>
            </label>
            <label class="campo">
              <span>Municipio *</span>
              <select v-model="form.municipio" class="form-input">
                <option value="" disabled>Seleccione...</option>
                <option v-for="m in store.municipiosCatalogo" :key="m" :value="m">{{ m }}</option>
              </select>
            </label>
            <label class="campo" v-show="false">
              <span>Vocero</span>
              <input v-model.trim="form.vocero" type="text" class="form-input" placeholder="Nombre del vocero" />
            </label>
            <label class="campo" v-show="false">
              <span>Número de aprendices</span>
              <input v-model.number="form.numero_aprendices" type="number" min="1" max="60" class="form-input" />
            </label>
            <label class="campo">
              <span>Horas del programa *</span>
              <input v-model.number="form.horas_programa_formacion" type="number" min="1" class="form-input" />
            </label>
            <label class="campo">
              <span>Instructor titular (opcional)</span>
              <select v-model="form.instructor_titular_id" class="form-input">
                <option value="">Definir más adelante...</option>
                <option v-for="i in store.instructores" :key="i.id" :value="i.id">
                  {{ i.nombre }} ({{ i.tipo_vinculacion }})
                </option>
              </select>
            </label>
          </div>
          
          <div class="rejilla" style="margin-top: 12px; grid-template-columns: 1fr 1fr;">
            <label class="campo">
              <span>Inicio etapa lectiva *</span>
              <input v-model="form.fecha_inicio" type="date" class="form-input" />
            </label>
            <label class="campo">
              <span>Fin etapa lectiva *</span>
              <input v-model="form.fecha_fin" type="date" class="form-input" :min="form.fecha_inicio || undefined" />
            </label>
          </div>
          
          <div class="rejilla" style="margin-top: 12px; grid-template-columns: 1fr 1fr;">
            <label class="campo">
              <span>Inicio etapa productiva *</span>
              <input v-model="form.fecha_inicio_practicas" type="date" class="form-input" :min="form.fecha_fin || undefined" />
            </label>
            <label class="campo">
              <span>Fin etapa productiva *</span>
              <input v-model="form.fecha_fin_practicas" type="date" class="form-input" :min="form.fecha_inicio_practicas || undefined" />
            </label>
          </div>
        </section>

        <p v-if="error" class="banner banner-error">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ error }}
        </p>
      </div>

      <template #footer>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cancelar</button>
        <button class="btn-guardar" :disabled="guardando" @click="guardar">
          <font-awesome-icon v-if="guardando" :icon="['fas', 'circle-notch']" spin />
          <font-awesome-icon v-else icon="fa-solid fa-check" />
          {{ guardando ? 'Creando...' : 'Crear ficha' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
// Alta de una Ficha Titulada: los datos básicos + el programa del catálogo,
// cuya matriz de competencias se copia como diagnóstico inicial de la ficha.
import { reactive, ref, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import {
  useTituladasStore,
  JORNADAS_TITULADAS,
  COLORES_TIPO_COMPETENCIA,
} from '@/stores/tituladas';

const props = defineProps({
  show: { type: Boolean, required: true },
});
const emit = defineEmits(['update:show', 'close', 'creada']);

const store = useTituladasStore();
const toast = useToast();

const formVacio = () => ({
  codigo: '',
  programa_id: '',
  jornada: '',
  municipio: '',
  vocero: '',
  instructor_titular_id: '',
  fecha_inicio: '',
  fecha_fin: '',
  fecha_inicio_practicas: '',
  fecha_fin_practicas: '',
  numero_aprendices: 25,
  horas_programa_formacion: 0,
});

const form = reactive(formVacio());
const error = ref('');
const guardando = ref(false);

watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    Object.assign(form, formVacio());
    error.value = '';
  }
);

const programaElegido = computed(() =>
  store.programas.find((p) => p.id === form.programa_id) || null
);

const colorTipo = (tipo) => COLORES_TIPO_COMPETENCIA[tipo] || 'var(--borde)';

async function guardar() {
  if (guardando.value) return; // Previene doble clic
  error.value = '';
  if (!form.programa_id) return (error.value = 'Seleccione el programa del catálogo.');
  if (!form.codigo || form.codigo.length < 4) return (error.value = 'El código de la ficha debe tener al menos 4 caracteres.');
  
  const fichaExistente = store.fichas.some(f => String(f.codigo).trim() === String(form.codigo).trim());
  if (fichaExistente) return (error.value = 'Ya existe una ficha registrada con este código (Sofía Plus).');

  if (!form.jornada) return (error.value = 'Seleccione la jornada.');
  if (!form.municipio || form.municipio.length < 3) return (error.value = 'Escriba el municipio de la ficha.');
  if (!form.fecha_inicio || !form.fecha_fin) return (error.value = 'Defina las fechas de la etapa lectiva.');
  if (!form.fecha_inicio_practicas || !form.fecha_fin_practicas) return (error.value = 'Defina las fechas de la etapa de prácticas.');

  if (!form.horas_programa_formacion || form.horas_programa_formacion < 1) return (error.value = 'Indique las horas de duración del programa.');

  guardando.value = true;
  const start = Date.now();
  const resultado = await store.crearFicha({
    ...form,
    instructor_titular_id: form.instructor_titular_id || null,
  });
  const elapsed = Date.now() - start;
  if (elapsed < 500) {
    await new Promise(r => setTimeout(r, 500 - elapsed));
  }
  guardando.value = false;

  if (resultado.success) {
    toast.success(`Ficha ${resultado.ficha.codigo} creada con su diagnóstico del catálogo.`);
    emit('creada', resultado.ficha);
    emit('update:show', false);
    emit('close');
  } else {
    error.value = resultado.error;
  }
}
</script>

<style scoped>
.modal-nueva-ficha :deep(.modal-container) {
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

.seccion {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.seccion-titulo {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.seccion-titulo svg { color: var(--sena-verde); }

.rejilla {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
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
  box-sizing: border-box;
  width: 100%;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

select.form-input { cursor: pointer; }

.vista-previa {
  list-style: none;
  margin: 0;
  padding: 0.6rem 0.9rem;
  border: 1px dashed var(--borde);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  max-height: 150px;
  overflow-y: auto;
  font-size: 0.76rem;
}

.vista-previa li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.vista-previa small { color: var(--texto-secundario); font-weight: 500; }

.punto-color {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.ayuda {
  margin: 0;
  font-size: 0.74rem;
  color: var(--texto-secundario);
  font-style: italic;
  border: 1px dashed var(--borde);
  border-radius: 10px;
  padding: 0.7rem 1rem;
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

.cuerpo-bloqueado {
  pointer-events: none;
  opacity: 0.6;
}
</style>
