<template>
  <div class="admin-view-shell">
    <!-- Estado de carga del detalle -->
    <div v-if="store.cargandoDetalle && !ficha" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando el detalle de la ficha...</p>
    </div>

    <!-- Error de conexión o ficha inexistente -->
    <div v-else-if="!ficha" class="module-card estado-panel estado-error">
      <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="estado-icono" />
      <div>
        <strong>No se pudo abrir la ficha.</strong>
        <p>{{ store.errorConexion || 'La ficha solicitada no existe o fue eliminada.' }}</p>
      </div>
      <button class="btn-action" @click="volver">
        <font-awesome-icon icon="fa-solid fa-arrow-left" /> VOLVER AL LISTADO
      </button>
    </div>

    <template v-else>
      <!-- Encabezado de la ficha -->
      <header class="dash-header">
        <div class="header-left">
          <button class="btn-volver" title="Volver al listado de fichas tituladas" @click="volver">
            <font-awesome-icon icon="fa-solid fa-arrow-left" />
          </button>
          <div class="environment-badge">
            <h1>FICHA {{ ficha.codigo }} — {{ ficha.programa.toUpperCase() }}</h1>
            <p class="header-meta">
              <span>{{ ficha.nivel }}</span>
              <span>· Jornada {{ ficha.jornada }} ({{ horarioJornada(ficha.jornada) }})</span>
              <span>· {{ ficha.sede }}</span>
              <span>· {{ ficha.numero_aprendices }} aprendices</span>
              <span>· Lectiva: {{ formatearFecha(ficha.fecha_inicio) }} → {{ formatearFecha(ficha.fecha_fin) }}</span>
              <button class="chip-titular btn-asignar-titular" @click="showModalTitular = true" :disabled="store.actualizandoTitularId === ficha.id" title="Cambiar Instructor Titular">
                <template v-if="store.actualizandoTitularId === ficha.id">
                  <font-awesome-icon :icon="['fas', 'circle-notch']" spin />
                  Guardando...
                </template>
                <template v-else-if="ficha.instructor_titular">
                  <span class="punto-color" :style="{ background: ficha.instructor_titular.color }"></span>
                  Titular: {{ ficha.instructor_titular.nombre }}
                </template>
                <template v-else>
                  <font-awesome-icon icon="fa-solid fa-user-plus" />
                  Asignar Titular
                </template>
              </button>
              <span v-if="store.modoDemo" class="chip-demo">MODO DEMO</span>
            </p>
          </div>
        </div>
        <div class="header-actions">
          <div class="toggle-vista" role="group" aria-label="Cambiar de pestaña">
            <button
              class="btn-toggle"
              :class="{ activo: pestana === 'diagnostico' }"
              title="Competencias del programa y su avance"
              @click="pestana = 'diagnostico'"
            >
              <font-awesome-icon icon="fa-solid fa-list-check" /> Diagnóstico
            </button>
            <button
              class="btn-toggle"
              :class="{ activo: pestana === 'calendario' }"
              title="Calendario mensual de asignaciones"
              @click="pestana = 'calendario'"
            >
              <font-awesome-icon icon="fa-solid fa-calendar-days" /> Calendario
            </button>
            <button
              class="btn-toggle"
              :class="{ activo: pestana === 'archivos' }"
              title="Respaldo de los archivos de Excel históricos de la ficha"
              @click="pestana = 'archivos'"
            >
              <font-awesome-icon icon="fa-solid fa-paperclip" /> Archivos
              <span v-if="ficha.archivos?.length" class="conteo-archivos">{{ ficha.archivos.length }}</span>
            </button>
          </div>
          <button
            v-if="!ficha.tiene_diagnostico"
            class="btn-action btn-diagnostico"
            title="El flujo inicia aquí: sin la matriz de competencias la ficha no se puede programar"
            @click="showDiagnostico = true"
          >
            <font-awesome-icon icon="fa-solid fa-list-check" />
            <span>REGISTRAR DIAGNÓSTICO</span>
          </button>
          <button v-else class="btn-action" @click="abrirProgramar()">
            <font-awesome-icon icon="fa-solid fa-plus" />
            <span>PROGRAMAR</span>
          </button>
        </div>
      </header>

      <!-- Resumen del avance -->
      <section class="resumen-grid">
        <article class="module-card resumen-card">
          <p class="resumen-titulo">PROGRAMACIÓN GLOBAL</p>
          <div class="resumen-valor">
            <span class="resumen-numero" :class="{ alerta: ficha.porcentaje_programacion < META_PROGRAMACION }">
              {{ ficha.porcentaje_programacion }}%
            </span>
            <span class="resumen-contexto">meta {{ META_PROGRAMACION }}%</span>
          </div>
          <div class="barra">
            <div
              class="barra-relleno"
              :class="ficha.porcentaje_programacion >= META_PROGRAMACION ? 'barra-ok' : 'barra-alerta'"
              :style="{ width: Math.min(ficha.porcentaje_programacion, 100) + '%' }"
            ></div>
            <span class="barra-meta" :style="{ left: META_PROGRAMACION + '%' }"></span>
          </div>
        </article>

        <article class="module-card resumen-card">
          <p class="resumen-titulo">HORAS PROGRAMADAS</p>
          <div class="resumen-valor">
            <span class="resumen-numero">{{ ficha.horas_programadas }}</span>
            <span class="resumen-contexto">de {{ ficha.total_horas_programa }} h del programa</span>
          </div>
          <p class="resumen-nota">
            <font-awesome-icon icon="fa-solid fa-clock" />
            Cada día hábil programado suma 6 h del bloque de la jornada.
          </p>
        </article>

        <article class="module-card resumen-card" :class="{ 'card-alerta': ficha.alerta_tecnica }">
          <p class="resumen-titulo">PARTE TÉCNICA</p>
          <div class="resumen-valor">
            <span class="resumen-numero" :class="{ alerta: ficha.alerta_tecnica }">
              {{ ficha.porcentaje_tecnica }}%
            </span>
            <span class="resumen-contexto">de lo programado (mínimo {{ META_TECNICA }}%)</span>
          </div>
          <p v-if="ficha.alerta_tecnica" class="resumen-nota alerta">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
            Priorice competencias técnicas en la próxima programación.
          </p>
          <p v-else class="resumen-nota ok">
            <font-awesome-icon icon="fa-solid fa-circle-check" />
            La prioridad técnica se está cumpliendo.
          </p>
        </article>
      </section>

      <!-- ── PESTAÑA DIAGNÓSTICO ── -->
      <main v-if="pestana === 'diagnostico'" class="module-card">
        <div class="tabla-toolbar">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-list-check" /> DIAGNÓSTICO DE COMPETENCIAS
          </h2>
          <div class="toolbar-derecha">
            <!-- Leyenda de tipos (los colores institucionales del módulo) -->
            <div class="leyenda">
              <span v-for="(color, tipo) in COLORES_TIPO_COMPETENCIA" :key="tipo" class="leyenda-item">
                <span class="punto-color" :style="{ background: color }"></span>{{ tipo }}
              </span>
            </div>
            <button
              class="btn-secundario"
              title="Editar la matriz de competencias de la ficha"
              @click="showDiagnostico = true"
            >
              <font-awesome-icon icon="fa-solid fa-pen-to-square" />
              {{ ficha.tiene_diagnostico ? 'Editar matriz' : 'Registrar matriz' }}
            </button>
          </div>
        </div>

        <!-- Sin diagnóstico: el flujo real no permite programar todavía -->
        <div v-if="!ficha.tiene_diagnostico" class="estado-panel sin-diagnostico">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="estado-icono" />
          <div>
            <strong>Esta ficha aún no tiene su diagnóstico registrado.</strong>
            <p>
              Registre la matriz de competencias que envía el instructor titular (competencia,
              tipo y horas). Sin este paso la ficha <strong>no se puede programar</strong>.
            </p>
          </div>
          <button class="btn-action" @click="showDiagnostico = true">
            <font-awesome-icon icon="fa-solid fa-list-check" /> REGISTRAR DIAGNÓSTICO
          </button>
        </div>

        <div v-else class="tabla-scroll">
          <table class="tabla-diagnostico">
            <thead>
              <tr>
                <th>COMPETENCIA</th>
                <th class="text-center">TIPO</th>
                <th class="text-center">HORAS PROGRAMA</th>
                <th class="text-center">PROGRAMADAS</th>
                <th class="col-avance">AVANCE</th>
                <th>INSTRUCTORES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in ficha.diagnostico" :key="c.id">
                <td>
                  <span class="comp-nombre">
                    <span class="comp-franja" :style="{ background: colorTipo(c.tipo) }"></span>
                    {{ c.nombre }}
                  </span>
                </td>
                <td class="text-center">
                  <span class="badge-tipo" :style="estiloTipo(c.tipo)">{{ c.tipo }}</span>
                </td>
                <td class="text-center celda-horas">{{ c.horas }} h</td>
                <td class="text-center celda-horas">{{ c.horas_programadas }} h</td>
                <td class="col-avance">
                  <div class="progreso-celda">
                    <div class="barra">
                      <div
                        class="barra-relleno"
                        :style="{ width: Math.min(c.porcentaje, 100) + '%', background: colorTipo(c.tipo) }"
                      ></div>
                    </div>
                    <span class="progreso-texto">{{ c.porcentaje }}%</span>
                  </div>
                </td>
                <td>
                  <span v-if="c.instructores.length" class="celda-instructores">
                    {{ c.instructores.join(', ') }}
                  </span>
                  <span v-else class="celda-instructores vacio">Sin programar</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>

      <!-- ── PESTAÑA CALENDARIO ── -->
      <main v-else-if="pestana === 'calendario'" class="calendario-vista">
        <div class="module-card calendario-card">
          <!-- Navegación de meses -->
          <div class="calendario-toolbar">
            <h2 class="module-title">
              <font-awesome-icon icon="fa-solid fa-calendar-days" /> CALENDARIO DE PROGRAMACIÓN
            </h2>
            <div class="mes-nav">
              <button class="mes-flecha" aria-label="Mes anterior" @click="cambiarMes(-1)">
                <font-awesome-icon icon="fa-solid fa-chevron-left" />
              </button>
              <span class="mes-actual">{{ etiquetaMes }}</span>
              <button class="mes-flecha" aria-label="Mes siguiente" @click="cambiarMes(1)">
                <font-awesome-icon icon="fa-solid fa-chevron-right" />
              </button>
              <button class="btn-hoy" @click="irAHoy">Hoy</button>
            </div>
          </div>

          <!-- Grilla mensual -->
          <div class="calendario-scroll">
            <div class="calendario-grid">
              <div v-for="dia in DIAS_SEMANA" :key="dia" class="cal-encabezado">{{ dia }}</div>
              <div
                v-for="celda in celdasMes"
                :key="celda.iso"
                class="cal-dia"
                :class="{
                  'fuera-mes': !celda.esDelMes,
                  'fin-semana': celda.finDeSemana,
                  hoy: celda.iso === hoyIso,
                }"
              >
                <span class="cal-numero">{{ celda.dia }}</span>
                <button
                  v-for="a in celda.asignaciones"
                  :key="a.id"
                  class="cal-chip"
                  :style="estiloChip(a)"
                  :title="`${a.instructor?.nombre || 'Sin instructor'} · ${a.competencia?.nombre || 'Sin competencia'} (${a.competencia?.tipo || 'N/A'})\n` +
                    `${formatearFecha(a.fecha_inicio)} → ${formatearFecha(a.fecha_fin)} · ${a.horas || 0} h · ` +
                    `Ambiente: ${a.ambiente?.nombre || '—'}\nClic para editar la asignación`"
                  @click="abrirProgramar(a)"
                >
                  <div class="cal-chip-header">
                    <strong>{{ a.instructor?.iniciales || 'S/I' }}</strong>
                    <span class="cal-chip-ambiente">{{ a.ambiente?.nombre || 'Sin amb' }}</span>
                  </div>
                  <span class="cal-chip-texto">{{ a.competencia?.nombre || 'Sin competencia' }}</span>
                  <span class="cal-chip-horas">{{ a.horas || 0 }}h programadas</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Leyenda automática (las "convenciones" del Excel) -->
          <div v-if="leyendaMes.length" class="leyenda leyenda-calendario">
            <span class="leyenda-etiqueta">Convenciones del mes:</span>
            <span v-for="i in leyendaMes" :key="i.id" class="leyenda-item">
              <span class="punto-color" :style="{ background: i.color }"></span>
              <strong>{{ i.iniciales }}</strong> = {{ i.nombre }}
            </span>
          </div>
          <p v-else class="calendario-vacio">
            Este mes no tiene asignaciones. Use el botón <strong>PROGRAMAR</strong> para agregar la primera.
          </p>
        </div>

        <!-- Asignaciones del mes (edición y eliminación) -->
        <div v-if="asignacionesMes.length" class="module-card">
          <h2 class="module-title titulo-lista">
            <font-awesome-icon icon="fa-solid fa-table-list" /> ASIGNACIONES DE {{ etiquetaMes.toUpperCase() }}
          </h2>
          <ul class="lista-asignaciones">
            <li v-for="a in asignacionesMes" :key="a.id" class="asig-fila">
              <span class="asig-franja" :style="{ background: a.instructor?.color || 'var(--borde)' }"></span>
              <div class="asig-info">
                <span class="asig-principal">
                  <strong>{{ a.instructor?.nombre }}</strong> · {{ a.competencia?.nombre }}
                  <span class="badge-tipo" :style="estiloTipo(a.competencia?.tipo)">{{ a.competencia?.tipo }}</span>
                </span>
                <span class="asig-secundario">
                  {{ formatearFecha(a.fecha_inicio) }} → {{ formatearFecha(a.fecha_fin) }}
                  · {{ a.horas }} h · {{ a.ambiente?.nombre }} ({{ a.ambiente?.sede }})
                </span>
              </div>
              <div class="asig-acciones">
                <button class="btn-tabla" title="Editar la asignación" @click="abrirProgramar(a)">
                  <font-awesome-icon icon="fa-solid fa-pen-to-square" />
                </button>
                <button class="btn-tabla btn-eliminar" title="Eliminar la asignación" @click="confirmarEliminar(a)">
                  <font-awesome-icon icon="fa-solid fa-trash-can" />
                </button>
              </div>
            </li>
          </ul>
        </div>
      </main>

      <!-- ── PESTAÑA ARCHIVOS (respaldo de los Excel históricos) ── -->
      <main v-else class="module-card">
        <div class="tabla-toolbar">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-paperclip" /> RESPALDO DE ARCHIVOS DE LA FICHA
          </h2>
          <label class="btn-secundario btn-subir" :class="{ deshabilitado: subiendoArchivo }">
            <font-awesome-icon v-if="subiendoArchivo" :icon="['fas', 'circle-notch']" spin />
            <font-awesome-icon v-else icon="fa-solid fa-cloud-arrow-up" />
            {{ subiendoArchivo ? 'Subiendo...' : 'Subir archivo' }}
            <input
              type="file"
              class="input-archivo"
              accept=".xlsx,.xls,.xlsm,.csv,.pdf,.docx"
              :disabled="subiendoArchivo"
              @change="subirArchivo"
            />
          </label>
        </div>

        <p class="nota-archivos">
          <font-awesome-icon icon="fa-solid fa-circle-info" />
          Guarde aquí las matrices de Excel históricas y demás soportes de la ficha. Los archivos
          se conservan tal cual se subieron (solo lectura) y se pueden descargar cuando se necesiten.
          Formatos: Excel, CSV, PDF o Word · máximo 10 MB.
        </p>

        <ul v-if="ficha.archivos?.length" class="lista-archivos">
          <li v-for="a in ficha.archivos" :key="a.id" class="archivo-fila">
            <font-awesome-icon icon="fa-solid fa-paperclip" class="archivo-icono" />
            <div class="archivo-info">
              <span class="archivo-nombre">{{ a.nombre }}</span>
              <span class="archivo-datos">{{ formatearTamano(a.tamano) }} · subido el {{ a.fecha }}</span>
            </div>
            <div class="asig-acciones">
              <a
                class="btn-tabla btn-descarga"
                :href="tituladasService.urlArchivoFicha(ficha.id, a.id)"
                :download="a.nombre"
                title="Descargar el archivo"
              >
                <font-awesome-icon icon="fa-solid fa-download" />
              </a>
              <button class="btn-tabla btn-eliminar" title="Eliminar el archivo del respaldo" @click="confirmarEliminarArchivo(a)">
                <font-awesome-icon icon="fa-solid fa-trash-can" />
              </button>
            </div>
          </li>
        </ul>
        <p v-else class="calendario-vacio">
          Aún no hay archivos de respaldo. Use el botón <strong>Subir archivo</strong> para
          guardar las matrices de Excel históricas de esta ficha.
        </p>
      </main>

      <!-- Pantalla de programación (crear / editar asignaciones) -->
      <ModalProgramarAsignacion
        :show="showProgramar"
        :ficha="ficha"
        :asignacion="asignacionSeleccionada"
        @update:show="showProgramar = $event"
        @close="showProgramar = false"
      />

      <!-- Registro/edición de la matriz de diagnóstico -->
      <ModalDiagnostico
        :show="showDiagnostico"
        :ficha="ficha"
        @update:show="showDiagnostico = $event"
        @close="showDiagnostico = false"
      />

      <!-- Asignar Titular -->
      <ModalAsignarTitular
        :show="showModalTitular"
        :ficha="ficha"
        @update:show="showModalTitular = $event"
        @close="showModalTitular = false"
      />
    </template>
  </div>
</template>

<script setup>
// Detalle de una Ficha Titulada: diagnóstico de competencias (con colores por
// tipo) + calendario mensual de asignaciones (con colores por instructor),
// equivalente a la "matriz de la ficha" del Excel del coordinador.
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import Swal from 'sweetalert2';
import ModalProgramarAsignacion from '@/components/admin/modals/ModalProgramarAsignacion.vue';
import ModalDiagnostico from '@/components/admin/modals/ModalDiagnostico.vue';
import ModalAsignarTitular from '@/components/admin/modals/ModalAsignarTitular.vue';
import { tituladasService } from '@/services/tituladasService';
import {
  useTituladasStore,
  COLORES_TIPO_COMPETENCIA,
  META_PROGRAMACION,
  META_TECNICA,
  horarioJornada,
  formatearFecha,
} from '@/stores/tituladas';

const store = useTituladasStore();
const route = useRoute();
const router = useRouter();
const toast = useToast();

const ficha = computed(() => store.fichaActual);

const pestana = ref('diagnostico');
const showProgramar = ref(false);
const showDiagnostico = ref(false);
const showModalTitular = ref(false);
const asignacionSeleccionada = ref(null);
const subiendoArchivo = ref(false);

const NOMBRES_MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];
const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

// ── Colores por tipo de competencia ──
const colorTipo = (tipo) => COLORES_TIPO_COMPETENCIA[tipo] || 'var(--borde)';

const estiloTipo = (tipo) => ({
  background: hexARgba(colorTipo(tipo), 0.14),
  color: colorTipo(tipo),
  border: `1px solid ${hexARgba(colorTipo(tipo), 0.4)}`,
});

/** #RRGGBB → rgba(r,g,b,alfa) para fondos suaves de chips y badges. */
function hexARgba(hex, alfa) {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alfa})`;
}

// ── Calendario mensual ──
const hoy = new Date();
const hoyIso = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;
const periodo = ref({ anio: hoy.getFullYear(), mes: hoy.getMonth() }); // mes: 0-11

const etiquetaMes = computed(() => `${NOMBRES_MESES[periodo.value.mes]} ${periodo.value.anio}`);

const cambiarMes = (delta) => {
  const fecha = new Date(periodo.value.anio, periodo.value.mes + delta, 1);
  periodo.value = { anio: fecha.getFullYear(), mes: fecha.getMonth() };
};

const irAHoy = () => {
  periodo.value = { anio: hoy.getFullYear(), mes: hoy.getMonth() };
};

const aIso = (fecha) =>
  `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;

/** Asignaciones que cubren un día (solo días hábiles: el fin de semana no suma). */
const asignacionesDe = (iso, finDeSemana) => {
  if (finDeSemana || !ficha.value) return [];
  return ficha.value.asignaciones.filter((a) => a.fecha_inicio <= iso && iso <= a.fecha_fin);
};

const celdasMes = computed(() => {
  if (!ficha.value) return [];
  const { anio, mes } = periodo.value;
  const primerDia = new Date(anio, mes, 1);
  const desplazamiento = (primerDia.getDay() + 6) % 7; // lunes = 0
  const celdas = [];
  for (let i = 0; i < 42; i++) {
    const fecha = new Date(anio, mes, 1 - desplazamiento + i);
    const finDeSemana = fecha.getDay() === 0 || fecha.getDay() === 6;
    const iso = aIso(fecha);
    celdas.push({
      iso,
      dia: fecha.getDate(),
      esDelMes: fecha.getMonth() === mes,
      finDeSemana,
      asignaciones: asignacionesDe(iso, finDeSemana),
    });
  }
  // Se descartan las semanas finales que quedan completamente fuera del mes
  const semanas = [];
  for (let i = 0; i < 42; i += 7) semanas.push(celdas.slice(i, i + 7));
  return semanas.filter((s) => s.some((c) => c.esDelMes)).flat();
});

/** Asignaciones que tocan el mes visible (para la lista y la leyenda). */
const asignacionesMes = computed(() => {
  if (!ficha.value) return [];
  const { anio, mes } = periodo.value;
  const inicioMes = aIso(new Date(anio, mes, 1));
  const finMes = aIso(new Date(anio, mes + 1, 0));
  return ficha.value.asignaciones.filter(
    (a) => a.fecha_inicio <= finMes && inicioMes <= a.fecha_fin
  );
});

/** Leyenda automática: las "convenciones" (color + iniciales) del mes visible. */
const leyendaMes = computed(() => {
  const vistos = new Map();
  for (const a of asignacionesMes.value) {
    if (a.instructor && !vistos.has(a.instructor.id)) vistos.set(a.instructor.id, a.instructor);
  }
  return [...vistos.values()];
});

const estiloChip = (a) => {
  const tipoColor = a.competencia?.tipo ? colorTipo(a.competencia.tipo) : null;
  const color = tipoColor && tipoColor !== 'var(--borde)' ? tipoColor : (a.instructor?.color || '#39A900');
  
  return {
    background: hexARgba(color, 0.14),
    borderLeft: `3px solid ${color}`,
    color: 'var(--texto-principal)',
  };
};

// ── Acciones ──
const abrirProgramar = (asignacion = null) => {
  asignacionSeleccionada.value = asignacion;
  showProgramar.value = true;
};

const confirmarEliminar = async (a) => {
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

  const resultado = await store.eliminarAsignacion(a.id, ficha.value.id);
  if (resultado.success) {
    toast.success('Asignación eliminada. Horarios y ambiente liberados.');
  } else {
    toast.error(resultado.error);
  }
};

// ── Respaldo de archivos ──
const formatearTamano = (bytes) => {
  if (!bytes) return '0 KB';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const subirArchivo = async (evento) => {
  const archivo = evento.target.files?.[0];
  evento.target.value = ''; // permite volver a subir el mismo archivo
  if (!archivo) return;
  if (archivo.size > 10 * 1024 * 1024) {
    toast.error('El archivo supera el tamaño máximo permitido (10 MB).');
    return;
  }

  subiendoArchivo.value = true;
  const resultado = await store.subirArchivo(ficha.value.id, archivo);
  subiendoArchivo.value = false;

  if (resultado.success) {
    toast.success(`Archivo "${archivo.name}" guardado en el respaldo de la ficha.`);
  } else {
    toast.error(resultado.error);
  }
};

const confirmarEliminarArchivo = async (a) => {
  const { isConfirmed } = await Swal.fire({
    title: '¿Eliminar el archivo?',
    text: `Se eliminará "${a.nombre}" del respaldo de la ficha. Esta acción no se puede deshacer.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#E53E3E',
    cancelButtonColor: '#39A900',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  });
  if (!isConfirmed) return;

  const resultado = await store.eliminarArchivo(ficha.value.id, a.id);
  if (resultado.success) {
    toast.success('Archivo eliminado del respaldo.');
  } else {
    toast.error(resultado.error);
  }
};

const volver = () => {
  if (window.history.state && window.history.state.back) {
    router.back();
  } else {
    // Si abrieron el link directo y no hay historial, lo mandamos al directorio
    router.push('/programador-academico/directorio');
  }
};

// ── Carga del detalle ──
const cargar = async () => {
  await store.initStore();
  const resultado = await store.cargarDetalle(route.params.id);
  if (!resultado.success && resultado.noEncontrada) {
    toast.error('La ficha solicitada no existe.');
    volver();
  }
};

onMounted(cargar);
watch(() => route.params.id, (nuevo, anterior) => {
  if (nuevo && nuevo !== anterior) cargar();
});
</script>

<style scoped>
.admin-view-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
  box-sizing: border-box;
}

/* ── Encabezado ── */
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  border-left: 5px solid var(--sena-verde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  gap: 1rem;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.btn-volver {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  width: 42px;
  height: 42px;
  color: var(--texto-secundario);
  cursor: pointer;
  font-size: 1rem;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.btn-volver:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.environment-badge h1 {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}

.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.chip-titular {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 2px 8px;
  font-weight: 700;
}

.chip-demo {
  background: rgba(253, 195, 0, 0.18);
  color: #8a6d00;
  border: 1px solid rgba(253, 195, 0, 0.5);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

[data-theme="dark"] .chip-demo { color: var(--sena-amarillo); }

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toggle-vista {
  display: flex;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  overflow: hidden;
}

.btn-toggle {
  background: transparent;
  border: none;
  padding: 0.65rem 1rem;
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-toggle.activo {
  background: var(--sena-verde);
  color: var(--sena-blanco);
}

.btn-action {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-action:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.3);
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

/* ── Resumen ── */
.resumen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.resumen-card {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding: 1.1rem 1.4rem;
}

.card-alerta { border-left: 4px solid #e67e22; }

.resumen-titulo {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-secundario);
}

.resumen-valor {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.resumen-numero {
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--sena-verde);
  line-height: 1;
}

.resumen-numero.alerta { color: #e67e22; }

.resumen-contexto {
  font-size: 0.74rem;
  color: var(--texto-secundario);
}

.resumen-nota {
  margin: 0;
  font-size: 0.72rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
}

.resumen-nota.alerta { color: #e67e22; font-weight: 700; }
.resumen-nota.ok { color: var(--sena-verde); font-weight: 700; }

/* Barra con marca de meta */
.barra {
  position: relative;
  height: 8px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  overflow: hidden;
  flex: 1;
}

.barra-relleno { height: 100%; border-radius: 6px; transition: width 0.4s ease; }
.barra-ok { background: var(--sena-verde); }
.barra-alerta { background: #e67e22; }

.barra-meta {
  position: absolute;
  top: -2px;
  bottom: -2px;
  width: 2px;
  background: var(--sena-azul-oscuro);
  opacity: 0.55;
}

/* ── Diagnóstico ── */
.tabla-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.module-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-title svg { color: var(--sena-verde); }

.leyenda {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  font-size: 0.72rem;
  color: var(--texto-secundario);
}

.leyenda-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
}

.punto-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.tabla-scroll { overflow-x: auto; }

.tabla-diagnostico {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

.tabla-diagnostico th {
  text-align: left;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid var(--borde);
  white-space: nowrap;
}

.tabla-diagnostico td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--fondo-app);
  vertical-align: middle;
  font-size: 0.82rem;
}

.text-center { text-align: center; }

.comp-nombre {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  min-width: 220px;
}

.comp-franja {
  width: 4px;
  height: 26px;
  border-radius: 2px;
  flex-shrink: 0;
}

.badge-tipo {
  display: inline-block;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.68rem;
  font-weight: 800;
  white-space: nowrap;
}

.celda-horas { font-family: monospace; font-size: 0.85rem; }

.col-avance { min-width: 160px; }

.progreso-celda { display: flex; align-items: center; gap: 8px; }

.progreso-texto {
  font-size: 0.75rem;
  font-weight: 800;
  min-width: 38px;
  text-align: right;
}

.celda-instructores { font-size: 0.76rem; color: var(--texto-secundario); }
.celda-instructores.vacio { font-style: italic; }

/* ── Calendario ── */
.calendario-vista {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.calendario-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.mes-nav { display: flex; align-items: center; gap: 6px; }

.mes-flecha {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  width: 30px;
  height: 30px;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.mes-flecha:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.mes-actual {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--texto-principal);
  min-width: 140px;
  text-align: center;
}

.btn-hoy {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.35rem 0.8rem;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hoy:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.calendario-scroll { overflow-x: auto; }

.calendario-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(120px, 1fr));
  gap: 4px;
  min-width: 860px;
}

.cal-encabezado {
  text-align: center;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  padding: 0.4rem 0;
}

.cal-dia {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  min-height: 86px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cal-dia.fuera-mes { opacity: 0.35; }

.cal-dia.fin-semana {
  background: repeating-linear-gradient(
    -45deg,
    var(--fondo-app),
    var(--fondo-app) 6px,
    rgba(0, 48, 64, 0.04) 6px,
    rgba(0, 48, 64, 0.04) 12px
  );
}

.cal-dia.hoy { border-color: var(--sena-verde); box-shadow: inset 0 0 0 1px var(--sena-verde); }

.cal-numero {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--texto-secundario);
}

.cal-dia.hoy .cal-numero { color: var(--sena-verde); }

.cal-chip {
  border: none;
  border-radius: 6px;
  padding: 4px 6px;
  font-size: 0.64rem;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-family: inherit;
  line-height: 1.25;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.cal-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 48, 64, 0.18);
}

.cal-chip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 4px;
  width: 100%;
}

.cal-chip strong { 
  font-size: 0.7rem; 
  color: inherit;
}

.cal-chip-ambiente {
  font-size: 0.58rem;
  font-weight: 700;
  opacity: 0.8;
  color: inherit;
  text-align: right;
}

.cal-chip-horas {
  font-size: 0.55rem;
  opacity: 0.9;
  font-style: italic;
  color: inherit;
  margin-top: 2px;
}

.cal-chip-texto {
  font-size: 0.6rem;
  line-height: 1.2;
  color: inherit;
  opacity: 0.85;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 1px;
}

.leyenda-calendario {
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px dashed var(--borde);
}

.leyenda-etiqueta { font-weight: 800; color: var(--texto-principal); }

.calendario-vacio {
  margin: 1rem 0 0;
  padding: 1.25rem;
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  border: 1px dashed var(--borde);
  border-radius: 12px;
}

/* ── Lista de asignaciones del mes ── */
.titulo-lista { margin-bottom: 1rem; }

.lista-asignaciones {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asig-fila {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 0.7rem 0.9rem;
}

.asig-franja {
  width: 5px;
  align-self: stretch;
  border-radius: 3px;
  flex-shrink: 0;
}

.asig-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.asig-principal {
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.asig-secundario { font-size: 0.72rem; color: var(--texto-secundario); }

.asig-acciones { display: flex; gap: 8px; flex-shrink: 0; }

.btn-tabla {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  width: 34px;
  height: 34px;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-tabla:hover { border-color: var(--sena-verde); color: var(--sena-verde); }
.btn-tabla.btn-eliminar:hover { border-color: #e53e3e; color: #e53e3e; }

/* ── Encabezado del diagnóstico y botón secundario ── */
.toolbar-derecha {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.btn-secundario {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.55rem 1rem;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-secundario);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-secundario:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.btn-diagnostico { background: #e67e22; box-shadow: 0 4px 12px rgba(230, 126, 34, 0.25); }
.btn-diagnostico:hover { background: #cf6d16; box-shadow: 0 6px 16px rgba(230, 126, 34, 0.3); }

.sin-diagnostico { border: 1px dashed rgba(230, 126, 34, 0.5); border-radius: 12px; }
.sin-diagnostico .estado-icono { color: #e67e22; }

.conteo-archivos {
  background: rgba(255, 255, 255, 0.25);
  border-radius: 6px;
  padding: 0 6px;
  font-size: 0.66rem;
}

.btn-toggle:not(.activo) .conteo-archivos {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
}

/* ── Respaldo de archivos ── */
.btn-subir { position: relative; overflow: hidden; }
.btn-subir.deshabilitado { opacity: 0.6; cursor: wait; }

.input-archivo {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.nota-archivos {
  margin: 0 0 1rem;
  font-size: 0.74rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: flex-start;
  gap: 8px;
  border: 1px dashed var(--borde);
  border-radius: 10px;
  padding: 0.7rem 1rem;
}

.nota-archivos svg { margin-top: 2px; color: var(--sena-verde); }

.lista-archivos {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.archivo-fila {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 0.7rem 0.9rem;
}

.archivo-icono { color: var(--sena-verde); font-size: 1rem; flex-shrink: 0; }

.archivo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.archivo-nombre {
  font-size: 0.82rem;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archivo-datos { font-size: 0.7rem; color: var(--texto-secundario); }

.btn-descarga {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  box-sizing: border-box;
}

/* ── Estados ── */
.estado-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  padding: 2.5rem 2rem;
  text-align: center;
  flex-wrap: wrap;
  color: var(--texto-secundario);
}

.estado-panel strong { color: var(--texto-principal); display: block; margin-bottom: 4px; }
.estado-panel p { margin: 0; font-size: 0.85rem; }
.estado-icono { font-size: 1.8rem; color: var(--sena-verde); }
.estado-error .estado-icono { color: var(--sena-amarillo); }

/* ── Responsive ── */
@media (max-width: 992px) {
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    text-align: left;
  }

  .header-actions { justify-content: center; }
}
</style>
