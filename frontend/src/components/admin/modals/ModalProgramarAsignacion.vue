<template>
  <div class="modal-programar">
    <BaseModal
      :show="show"
      :title="esEdicion ? 'EDITAR ASIGNACIÓN' : 'PROGRAMAR LA FICHA'"
      :closeOnBackdrop="false"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div v-if="ficha" class="cuerpo">
        <!-- Contexto de la ficha -->
        <p class="contexto">
          Ficha <strong>{{ ficha.codigo }}</strong> · {{ ficha.programa }} ·
          Jornada <strong>{{ ficha.jornada }}</strong> ({{ horarioJornada(ficha.jornada) }})
        </p>

        <!-- 1. Rango de días -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-calendar-days" /> 1. Rango de días
          </h4>
          <div class="fila-fechas">
            <label class="campo">
              <span>Desde</span>
              <input
                v-model="form.fecha_inicio"
                type="date"
                class="form-input"
              />
            </label>
            <label class="campo">
              <span>Hasta</span>
              <input
                v-model="form.fecha_fin"
                type="date"
                class="form-input"
                :min="form.fecha_inicio || undefined"
              />
            </label>
            <div v-if="disponibilidad" class="chip-horas" title="Días lunes a viernes × bloque de 6 horas">
              <font-awesome-icon icon="fa-solid fa-clock" />
              {{ disponibilidad.dias_habiles }} días hábiles = <strong>{{ disponibilidad.horas_estimadas }} h</strong>
            </div>
          </div>

          <p v-if="errorRango" class="banner banner-error">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ errorRango }}
          </p>
          <p v-else-if="disponibilidad?.ficha_ocupada" class="banner banner-aviso">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
            {{ disponibilidad.ficha_ocupada.detalle }}
          </p>
        </section>

        <!-- 2. Competencia -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-list-check" /> 2. Competencia del programa
          </h4>
          <select v-model="form.competencia_id" class="form-input select-completo" :disabled="disponibilidad?.ficha_ocupada != null">
            <option value="" disabled>Seleccione la competencia a programar...</option>
            <option v-for="c in ficha.diagnostico" :key="c.id" :value="c.id">
              {{ c.nombre }} — {{ c.tipo }} ({{ c.horas_programadas }}/{{ c.horas }} h programadas)
            </option>
          </select>
        </section>

        <!-- 3. Instructor (semáforo de disponibilidad) -->
        <section v-if="!disponibilidad?.ficha_ocupada" class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-chalkboard-user" /> 3. Instructor
            <span v-if="consultando" class="consultando">
              <font-awesome-icon :icon="['fas', 'circle-notch']" spin /> calculando disponibilidad...
            </span>
          </h4>

          <p v-if="!disponibilidad && !consultando" class="ayuda">
            Seleccione primero el rango de días para calcular la disponibilidad
            de instructores y ambientes en la jornada {{ ficha.jornada }}.
          </p>

          <ul v-if="disponibilidad" class="lista-opciones">
            <li v-for="i in disponibilidad.instructores" :key="i.id" class="opcion-instructor">
              <label
                class="opcion"
                :class="{
                  seleccionada: form.instructor_id === i.id,
                  deshabilitada: i.estado !== 'disponible',
                }"
              >
                <input
                  v-model="form.instructor_id"
                  type="radio"
                  name="instructor"
                  :value="i.id"
                  :disabled="i.estado !== 'disponible'"
                />
                <span class="semaforo" :class="`semaforo-${i.estado}`" aria-hidden="true"></span>
                <span class="punto-color" :style="{ background: i.color }"></span>
                <span class="opcion-info">
                  <span class="opcion-nombre">
                    {{ i.nombre }} <small>({{ i.iniciales }} · {{ i.tipo_vinculacion }})</small>
                  </span>
                  <span class="opcion-detalle" :class="`texto-${i.estado}`">{{ i.detalle }}</span>
                </span>
              </label>
              <!-- Mini-horario: aparece al pasar el cursor sobre el instructor -->
              <div class="mini-horario">
                <p class="mini-titulo">
                  <font-awesome-icon icon="fa-solid fa-calendar-days" />
                  Mini horario de {{ i.iniciales }} en el rango elegido
                </p>
                <ul v-if="i.ocupaciones?.length" class="mini-lista">
                  <li v-for="(o, indice) in i.ocupaciones" :key="indice">
                    <strong>{{ formatearFecha(o.fecha_inicio) }} → {{ formatearFecha(o.fecha_fin) }}</strong>
                    · Ficha {{ o.ficha_codigo }} ({{ o.jornada }})
                    <span class="mini-detalle">{{ o.competencia || o.programa }}</span>
                  </li>
                </ul>
                <p v-else class="mini-libre">
                  <font-awesome-icon icon="fa-solid fa-circle-check" />
                  Sin ocupaciones en estas fechas (en ninguna jornada).
                </p>
              </div>
            </li>
          </ul>

          <p v-if="disponibilidad" class="leyenda-semaforo">
            <span><span class="semaforo semaforo-disponible"></span> Disponible</span>
            <span><span class="semaforo semaforo-ocupado"></span> Ocupado (se indica la ficha)</span>
            <span><span class="semaforo semaforo-contrato_vencido"></span> Contrato vencido</span>
          </p>
        </section>

        <!-- 4. Ambiente (semáforo de disponibilidad) -->
        <section v-if="!disponibilidad?.ficha_ocupada" class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-location-dot" /> 4. Ambiente de formación
          </h4>
          <ul v-if="disponibilidad" class="lista-opciones">
            <li v-for="a in disponibilidad.ambientes" :key="a.id">
              <label
                class="opcion"
                :class="{
                  seleccionada: form.ambiente_id === a.id,
                  deshabilitada: a.estado !== 'disponible' || !a.sede_coincide,
                }"
                :title="a.detalle"
              >
                <input
                  v-model="form.ambiente_id"
                  type="radio"
                  name="ambiente"
                  :value="a.id"
                  :disabled="a.estado !== 'disponible' || !a.sede_coincide"
                />
                <span class="semaforo" :class="`semaforo-${a.estado}`" aria-hidden="true"></span>
                <span class="opcion-info">
                  <span class="opcion-nombre">
                    {{ a.nombre }} <small>({{ a.sede }} · {{ a.tipo }} · {{ a.capacidad }} puestos)</small>
                    <font-awesome-icon
                      v-if="!a.capacidad_suficiente"
                      icon="fa-solid fa-triangle-exclamation"
                      class="icono-capacidad"
                      :title="`Capacidad menor al número de aprendices de la ficha (${ficha.numero_aprendices})`"
                    />
                  </span>
                  <span class="opcion-detalle" :class="`texto-${a.estado}`">{{ a.detalle }}</span>
                </span>
              </label>
            </li>
          </ul>
          <p v-else class="ayuda">La lista de ambientes aparece al definir el rango de días.</p>
        </section>

        <!-- Error de guardado (conflictos 409 del backend) -->
        <p v-if="errorGuardar" class="banner banner-error">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ errorGuardar }}
        </p>
      </div>

      <template #footer>
        <button
          v-if="esEdicion"
          class="btn-eliminar"
          :disabled="guardando"
          @click="eliminar"
        >
          <font-awesome-icon icon="fa-solid fa-trash-can" /> Eliminar
        </button>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cancelar</button>
        <button class="btn-guardar" :disabled="guardando || disponibilidad?.ficha_ocupada != null" @click="guardar">
          <font-awesome-icon v-if="guardando" :icon="['fas', 'circle-notch']" spin />
          <font-awesome-icon v-else icon="fa-solid fa-check" />
          {{ esEdicion ? 'Guardar cambios' : 'Programar' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
// Pantalla de programación de una Ficha Titulada: rango de días + competencia +
// instructor + ambiente. La disponibilidad (🟢 disponible / 🔴 ocupado con qué
// ficha / ⚪ contrato vencido) la calcula el backend para la jornada de la ficha;
// al guardar, el propio backend actualiza ficha, horario del instructor y
// ambiente en una sola operación (los cruces responden 409 con mensaje claro).
import { reactive, ref, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import Swal from 'sweetalert2';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import { useTituladasStore, horarioJornada, formatearFecha } from '@/stores/tituladas';

const props = defineProps({
  show: { type: Boolean, required: true },
  ficha: { type: Object, default: null },
  // null = nueva asignación; objeto = edición de una existente
  asignacion: { type: Object, default: null },
});

const emit = defineEmits(['update:show', 'close']);

const store = useTituladasStore();
const toast = useToast();

const esEdicion = computed(() => !!props.asignacion);

const form = reactive({
  fecha_inicio: '',
  fecha_fin: '',
  competencia_id: '',
  instructor_id: '',
  ambiente_id: '',
});

const disponibilidad = ref(null);
const consultando = ref(false);
const errorRango = ref('');
const errorGuardar = ref('');
const guardando = ref(false);

// Al abrir el modal se carga el formulario (vacío o con la asignación a editar)
watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    errorRango.value = '';
    errorGuardar.value = '';
    disponibilidad.value = null;
    form.fecha_inicio = props.asignacion?.fecha_inicio || '';
    form.fecha_fin = props.asignacion?.fecha_fin || '';
    form.competencia_id = props.asignacion?.competencia?.id || '';
    form.instructor_id = props.asignacion?.instructor?.id || '';
    form.ambiente_id = props.asignacion?.ambiente?.id || '';
    consultarDisponibilidad();
  }
);

// Cada cambio del rango recalcula el semáforo de disponibilidad
watch(() => [form.fecha_inicio, form.fecha_fin], consultarDisponibilidad);

// Pre-selección inteligente: Si la competencia es "Técnica" y la ficha tiene un titular, se auto-asigna
watch(() => form.competencia_id, (nuevoId) => {
  if (!nuevoId || !props.ficha || !props.ficha.instructor_titular_id) return;
  // Solo auto-completar si no estamos en modo edición o si el instructor está vacío
  if (esEdicion.value && props.asignacion?.instructor?.id) return;
  
  const comp = props.ficha.diagnostico?.find(c => c.id === nuevoId);
  if (comp && comp.tipo === 'Técnica') {
    form.instructor_id = props.ficha.instructor_titular_id;
  }
});

async function consultarDisponibilidad() {
  errorRango.value = '';
  if (!props.ficha || !form.fecha_inicio || !form.fecha_fin) {
    disponibilidad.value = null;
    return;
  }
  if (form.fecha_fin < form.fecha_inicio) {
    disponibilidad.value = null;
    errorRango.value = 'La fecha final no puede ser anterior a la inicial.';
    return;
  }

  consultando.value = true;
  const resultado = await store.consultarDisponibilidad({
    fichaId: props.ficha.id,
    fechaInicio: form.fecha_inicio,
    fechaFin: form.fecha_fin,
    excluirAsignacion: props.asignacion?.id || null,
  });
  consultando.value = false;

  if (!resultado.success) {
    disponibilidad.value = null;
    errorRango.value = resultado.error;
    return;
  }
  disponibilidad.value = resultado.datos;

  // Si la selección actual dejó de estar disponible en el nuevo rango, se limpia
  const instructor = resultado.datos.instructores.find((i) => i.id === form.instructor_id);
  if (instructor && instructor.estado !== 'disponible') form.instructor_id = '';
  const ambiente = resultado.datos.ambientes.find((a) => a.id === form.ambiente_id);
  if (ambiente && (ambiente.estado !== 'disponible' || !ambiente.sede_coincide)) form.ambiente_id = '';
}

async function guardar() {
  errorGuardar.value = '';
  if (!form.fecha_inicio || !form.fecha_fin) {
    errorGuardar.value = 'Seleccione el rango de días a programar.';
    return;
  }
  if (!form.competencia_id) {
    errorGuardar.value = 'Seleccione la competencia del programa.';
    return;
  }
  if (!form.instructor_id) {
    errorGuardar.value = 'Seleccione un instructor disponible.';
    return;
  }
  if (!form.ambiente_id) {
    errorGuardar.value = 'Seleccione un ambiente disponible.';
    return;
  }

  guardando.value = true;
  const datos = {
    instructor_id: form.instructor_id,
    competencia_id: form.competencia_id,
    ambiente_id: form.ambiente_id,
    fecha_inicio: form.fecha_inicio,
    fecha_fin: form.fecha_fin,
  };
  const resultado = esEdicion.value
    ? await store.actualizarAsignacion(props.asignacion.id, datos, props.ficha.id)
    : await store.crearAsignacion({ ficha_id: props.ficha.id, ...datos });
  guardando.value = false;

  if (resultado.success) {
    toast.success(
      esEdicion.value
        ? 'Asignación actualizada: ficha, instructor y ambiente al día.'
        : 'Programación guardada: ficha, instructor y ambiente actualizados.'
    );
    emit('close');
  } else {
    // Conflictos 409 (cruce de ficha/instructor/ambiente, contrato, período)
    errorGuardar.value = resultado.error;
  }
}

async function eliminar() {
  const a = props.asignacion;
  const { isConfirmed } = await Swal.fire({
    title: '¿Eliminar la asignación?',
    text: `Se eliminará "${a.competencia?.nombre}" de ${a.instructor?.nombre} ` +
      `(${formatearFecha(a.fecha_inicio)} → ${formatearFecha(a.fecha_fin)}). ` +
      'La ficha, el instructor y el ambiente quedarán liberados.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#E53E3E',
    cancelButtonColor: '#39A900',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  });
  if (!isConfirmed) return;

  guardando.value = true;
  const resultado = await store.eliminarAsignacion(a.id, props.ficha.id);
  guardando.value = false;

  if (resultado.success) {
    toast.success('Asignación eliminada. Horarios y ambiente liberados.');
    emit('close');
  } else {
    errorGuardar.value = resultado.error;
  }
}
</script>

<style scoped>
/* La pantalla de programación necesita más ancho que el modal base */
.modal-programar :deep(.modal-container) {
  max-width: 820px;
}

.cuerpo {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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

.consultando {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--texto-secundario);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.fila-fechas {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
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
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.select-completo { width: 100%; box-sizing: border-box; cursor: pointer; }

.chip-horas {
  background: rgba(57, 169, 0, 0.1);
  border: 1px solid rgba(57, 169, 0, 0.35);
  color: var(--sena-verde-oscuro);
  border-radius: 8px;
  padding: 0.55rem 0.9rem;
  font-size: 0.78rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

[data-theme="dark"] .chip-horas { color: var(--sena-verde); }

.ayuda {
  margin: 0;
  font-size: 0.76rem;
  color: var(--texto-secundario);
  font-style: italic;
  border: 1px dashed var(--borde);
  border-radius: 10px;
  padding: 0.8rem 1rem;
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

.banner-aviso {
  background: rgba(230, 126, 34, 0.1);
  border: 1px solid rgba(230, 126, 34, 0.4);
  color: #b35c0e;
}

[data-theme="dark"] .banner-aviso { color: #f0a35e; }

/* ── Opciones de instructor / ambiente ── */
.lista-opciones {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 220px;
  overflow-y: auto;
}

.opcion {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 0.55rem 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.opcion:hover { border-color: var(--sena-verde); }

.opcion.seleccionada {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 1px var(--sena-verde);
}

.opcion.deshabilitada {
  opacity: 0.55;
  cursor: not-allowed;
}

.opcion.deshabilitada:hover { border-color: var(--borde); }

.opcion input[type='radio'] { accent-color: var(--sena-verde); }

.semaforo {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.semaforo-disponible { background: #39a900; }
.semaforo-ocupado { background: #e53e3e; }
.semaforo-contrato_vencido { background: #b8c2c8; }

.punto-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.opcion-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.opcion-nombre {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.opcion-nombre small { font-weight: 600; color: var(--texto-secundario); }

.opcion-detalle {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}

.texto-ocupado { color: #c53030; font-weight: 700; }
[data-theme="dark"] .texto-ocupado { color: #fc8181; }
.texto-contrato_vencido { font-style: italic; }

/* ── Mini-horario del instructor (se despliega al pasar el cursor) ── */
.opcion-instructor .mini-horario {
  display: none;
  margin: 4px 0 2px 30px;
  background: var(--fondo-tarjetas);
  border: 1px dashed var(--borde);
  border-radius: 10px;
  padding: 0.6rem 0.9rem;
}

.opcion-instructor:hover .mini-horario,
.opcion-instructor:focus-within .mini-horario {
  display: block;
}

.mini-titulo {
  margin: 0 0 6px;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.4px;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-titulo svg { color: var(--sena-verde); }

.mini-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.72rem;
}

.mini-lista strong { font-family: monospace; font-size: 0.72rem; }

.mini-detalle {
  display: block;
  color: var(--texto-secundario);
  font-size: 0.68rem;
}

.mini-libre {
  margin: 0;
  font-size: 0.72rem;
  color: var(--sena-verde);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.icono-capacidad { color: #e67e22; font-size: 0.8rem; }

.leyenda-semaforo {
  margin: 0;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 0.68rem;
  color: var(--texto-secundario);
}

.leyenda-semaforo > span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* ── Botones del pie ── */
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

.btn-eliminar {
  margin-right: auto; /* se separa de Cancelar/Guardar en el pie del modal */
  background: transparent;
  border: 1px solid rgba(229, 62, 62, 0.5);
  color: #e53e3e;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-eliminar:hover:not(:disabled) { background: rgba(229, 62, 62, 0.08); }

.btn-guardar:disabled,
.btn-cancelar:disabled,
.btn-eliminar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
