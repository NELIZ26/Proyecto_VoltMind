<template>
  <div class="admin-view-shell">
    <!-- Encabezado institucional -->
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>FICHAS COMPLEMENTARIAS</h1>
          <p class="header-meta">
            Seguimiento de solicitudes de formación complementaria
            <span v-if="store.indicadores">
              | {{ store.indicadores.total }} solicitudes · {{ store.indicadores.inscritos_total }} inscritos
            </span>
            <span v-if="store.modoDemo" class="chip-demo">MODO DEMO</span>
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="toggle-vista" role="group" aria-label="Cambiar tipo de vista">
          <button
            class="btn-toggle"
            :class="{ activo: vista === 'tablero' }"
            title="Vista de tablero por estado"
            @click="vista = 'tablero'"
          >
            <font-awesome-icon icon="fa-solid fa-table-columns" /> Tablero
          </button>
          <button
            class="btn-toggle"
            :class="{ activo: vista === 'carpetas' }"
            title="Carpetas por mes de solicitud (respaldo tipo OneDrive)"
            @click="vista = 'carpetas'"
          >
            <font-awesome-icon icon="fa-solid fa-folder-open" /> Meses
          </button>
        </div>
        <button class="btn-action" @click="abrirNueva">
          <font-awesome-icon icon="fa-solid fa-plus" />
          <span>NUEVA SOLICITUD</span>
        </button>
      </div>
      <!-- Campana de notificaciones: vive solo en esta sección,
           en la esquina superior derecha del encabezado -->
      <NotificacionesBell class="campana-header" />
    </header>

    <!-- Filtros -->
    <div class="module-card filtros-card">
      <div class="filters-group">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por programa o código de ficha..."
          />
        </div>
        <select v-model="filtroEstado" class="form-input select-filter">
          <option value="">Todos los estados</option>
          <option v-for="e in ESTADOS_TABLERO" :key="e" :value="e">{{ e }}</option>
        </select>
        <select v-model="filtroMunicipio" class="form-input select-filter">
          <option value="">Todos los municipios</option>
          <option v-for="m in store.municipios" :key="m" :value="m">{{ m }}</option>
        </select>
        <select v-model="filtroJornada" class="form-input select-filter">
          <option value="">Todas las jornadas</option>
          <option v-for="j in JORNADAS" :key="j" :value="j">{{ j }}</option>
        </select>
        <select v-model="filtroInstructor" class="form-input select-filter">
          <option value="">Todos los instructores</option>
          <option v-for="i in store.instructores" :key="i" :value="i">{{ i }}</option>
        </select>
        <button v-if="hayFiltros" class="btn-limpiar" @click="limpiarFiltros">
          <font-awesome-icon icon="fa-solid fa-xmark" /> Limpiar
        </button>
      </div>
    </div>

    <!-- Estado de error de conexión -->
    <div v-if="store.errorConexion" class="module-card estado-panel estado-error">
      <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="estado-icono" />
      <div>
        <strong>No se pudieron cargar las solicitudes.</strong>
        <p>{{ store.errorConexion }}</p>
      </div>
      <button class="btn-action" @click="store.cargarTodo()">
        <font-awesome-icon icon="fa-solid fa-arrows-rotate" /> Reintentar
      </button>
    </div>

    <!-- Estado de carga -->
    <div v-else-if="store.cargando && store.solicitudes.length === 0" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando solicitudes de formación complementaria...</p>
    </div>

    <!-- Estado vacío global -->
    <div v-else-if="store.solicitudes.length === 0" class="module-card estado-panel">
      <font-awesome-icon icon="fa-solid fa-file-circle-plus" class="estado-icono" />
      <div>
        <strong>Aún no hay solicitudes registradas.</strong>
        <p>Cree la primera solicitud para dejar atrás la matriz de Excel.</p>
      </div>
      <button class="btn-action" @click="abrirNueva">
        <font-awesome-icon icon="fa-solid fa-plus" /> NUEVA SOLICITUD
      </button>
    </div>

    <!-- ── VISTA TABLERO ── -->
    <main v-else-if="vista === 'tablero'" class="tablero">
      <section
        v-for="estado in columnasVisibles"
        :key="estado"
        class="columna"
        :class="claseColumna(estado)"
      >
        <header class="columna-header">
          <h2>{{ estado }}</h2>
          <span class="columna-contador">{{ agrupadas[estado].length }}</span>
        </header>

        <p v-if="agrupadas[estado].length === 0" class="columna-vacia">
          Sin solicitudes {{ hayFiltros ? 'con los filtros aplicados' : 'en este estado' }}.
        </p>

        <TarjetaComplementaria
          v-for="s in agrupadas[estado]"
          :key="s.id"
          :solicitud="s"
          @abrir="abrirDetalle"
        />
      </section>
    </main>

    <!-- ── VISTA CARPETAS POR MES (respaldo tipo OneDrive) ── -->
    <main v-else class="carpetas-vista">
      <!-- Nivel 1: el archivo mensual (carpetas por período) -->
      <template v-if="!mesSeleccionado">
        <!-- Barra del archivo -->
        <div class="module-card archivo-toolbar">
          <div class="archivo-titulos">
            <p class="archivo-eyebrow">
              <font-awesome-icon icon="fa-solid fa-folder-open" /> Archivo por mes
            </p>
            <p class="archivo-hint">
              Cada solicitud se archiva automáticamente en la carpeta del mes en que fue solicitada.
            </p>
          </div>
          <button
            class="btn-nueva-carpeta"
            :class="{ abierto: showCreadorCarpeta }"
            :title="showCreadorCarpeta ? 'Cerrar el selector de período' : 'Crear la carpeta de un mes y año'"
            @click="alternarCreadorCarpeta"
          >
            <font-awesome-icon :icon="showCreadorCarpeta ? 'fa-solid fa-xmark' : 'fa-solid fa-plus'" />
            {{ showCreadorCarpeta ? 'Cancelar' : 'Nueva carpeta' }}
          </button>
        </div>

        <!-- Selector de período (mes + año) -->
        <Transition name="creador">
          <div
            v-if="showCreadorCarpeta"
            class="module-card creador-carpeta"
            role="group"
            aria-label="Crear la carpeta de un período"
          >
            <div class="creador-anio">
              <button
                class="anio-flecha"
                :disabled="anioCreador <= ANIO_MINIMO"
                aria-label="Año anterior"
                @click="anioCreador--"
              >
                <font-awesome-icon icon="fa-solid fa-chevron-left" />
              </button>
              <span class="anio-actual">{{ anioCreador }}</span>
              <button
                class="anio-flecha"
                :disabled="anioCreador >= ANIO_MAXIMO"
                aria-label="Año siguiente"
                @click="anioCreador++"
              >
                <font-awesome-icon icon="fa-solid fa-chevron-right" />
              </button>
            </div>
            <div class="creador-meses">
              <button
                v-for="(nombre, i) in NOMBRES_MESES"
                :key="nombre"
                type="button"
                class="mes-opcion"
                :class="{
                  existente: carpetaExiste(claveDe(anioCreador, i)),
                  actual: claveDe(anioCreador, i) === claveMesActual,
                }"
                :title="carpetaExiste(claveDe(anioCreador, i))
                  ? `${nombre} ${anioCreador} ya tiene carpeta; clic para abrirla`
                  : `Crear la carpeta de ${nombre} ${anioCreador}`"
                @click="crearCarpeta(i)"
              >
                {{ nombre.slice(0, 3) }}
                <span
                  v-if="carpetaExiste(claveDe(anioCreador, i))"
                  class="mes-marca"
                  aria-hidden="true"
                >
                  <font-awesome-icon icon="fa-solid fa-folder" />
                </span>
              </button>
            </div>
            <p class="creador-nota">
              Los meses con <font-awesome-icon icon="fa-solid fa-folder" /> ya tienen carpeta;
              selecciónelos para abrirla directamente.
            </p>
          </div>
        </Transition>

        <!-- Carpetas agrupadas por año -->
        <template v-if="carpetasPorAnio.length">
          <section v-for="grupo in carpetasPorAnio" :key="grupo.anio" class="archivo-anio">
            <h2 class="anio-etiqueta">{{ grupo.anio }}</h2>
            <div class="carpetas-grid">
              <div
                v-for="carpeta in grupo.carpetas"
                :key="carpeta.clave"
                class="carpeta"
                :class="{ vacia: carpeta.items.length === 0 }"
                role="button"
                tabindex="0"
                :title="`Abrir las solicitudes de ${carpeta.etiqueta}`"
                @click="abrirCarpeta(carpeta.clave)"
                @keydown.enter="abrirCarpeta(carpeta.clave)"
              >
                <span v-if="carpeta.clave === claveMesActual" class="chip-mes-actual">Mes actual</span>
                <button
                  v-if="carpeta.items.length === 0 && esManual(carpeta.clave)"
                  class="carpeta-borrar"
                  title="Eliminar esta carpeta vacía"
                  :aria-label="`Eliminar la carpeta vacía de ${carpeta.etiqueta}`"
                  @click.stop="eliminarCarpeta(carpeta.clave)"
                >
                  <font-awesome-icon icon="fa-solid fa-trash-can" />
                </button>
                <font-awesome-icon icon="fa-solid fa-folder" class="carpeta-icono" />
                <span class="carpeta-nombre">{{ carpeta.mes }}</span>
                <span class="carpeta-conteo">
                  {{ carpeta.items.length }} {{ carpeta.items.length === 1 ? 'solicitud' : 'solicitudes' }}
                </span>
              </div>
            </div>
          </section>
        </template>
        <div v-else class="module-card estado-panel">
          <font-awesome-icon icon="fa-solid fa-folder-open" class="estado-icono" />
          <div>
            <strong>El archivo está vacío.</strong>
            <p>No hay solicitudes con los filtros aplicados. Cree una carpeta para preparar un período.</p>
          </div>
          <button class="btn-nueva-carpeta" @click="showCreadorCarpeta = true">
            <font-awesome-icon icon="fa-solid fa-plus" /> Nueva carpeta
          </button>
        </div>
      </template>

      <!-- Nivel 2: contenido de la carpeta abierta -->
      <template v-else>
        <div class="carpeta-abierta-header">
          <button class="btn-volver" @click="mesSeleccionado = null">
            <font-awesome-icon icon="fa-solid fa-arrow-left" /> Todos los meses
          </button>
          <h2 class="carpeta-titulo">
            <font-awesome-icon icon="fa-solid fa-folder-open" />
            {{ etiquetaMes(mesSeleccionado) }}
            <span class="columna-contador">{{ solicitudesDelMes.length }}</span>
          </h2>
        </div>

        <div v-if="solicitudesDelMes.length === 0" class="module-card estado-panel">
          <font-awesome-icon icon="fa-solid fa-folder-open" class="estado-icono" />
          <div>
            <strong>Esta carpeta aún está vacía.</strong>
            <p>
              Las solicitudes registradas en {{ etiquetaMes(mesSeleccionado) }} se archivarán aquí
              automáticamente.
            </p>
          </div>
          <button class="btn-action" @click="abrirNueva">
            <font-awesome-icon icon="fa-solid fa-plus" /> NUEVA SOLICITUD
          </button>
        </div>

        <div v-else class="carpeta-contenido">
          <TarjetaComplementaria
            v-for="s in solicitudesDelMes"
            :key="s.id"
            :solicitud="s"
            mostrar-estado
            @abrir="abrirDetalle"
          />
        </div>
      </template>
    </main>

    <!-- Modal detalle (todos los campos + checklist) -->
    <ModalDetalleComplementaria
      :show="showDetalle"
      :solicitud="solicitudSeleccionada"
      :enviando-aviso="enviandoAviso"
      :subiendo-resultados="subiendoResultados"
      @update:show="showDetalle = $event"
      @close="showDetalle = false"
      @actualizar="handleActualizar"
      @editar="abrirEditar"
      @eliminar="confirmarEliminar"
      @reenviar-aviso="handleReenviarAviso"
      @subir-resultados="handleSubirResultados"
    />

    <!-- Modal crear / editar -->
    <ModalFormComplementaria
      :show="showForm"
      :solicitudData="solicitudEnEdicion"
      @update:show="showForm = $event"
      @close="showForm = false"
      @save="handleGuardar"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import Swal from 'sweetalert2';
import ModalDetalleComplementaria from '@/components/admin/modals/ModalDetalleComplementaria.vue';
import ModalFormComplementaria from '@/components/admin/modals/ModalFormComplementaria.vue';
import TarjetaComplementaria from '@/components/admin/TarjetaComplementaria.vue';
import NotificacionesBell from '@/components/admin/NotificacionesBell.vue';
import {
  useComplementariasStore,
  ESTADOS_TABLERO,
  JORNADAS,
} from '@/stores/complementarias';

const toast = useToast();
const store = useComplementariasStore();
const route = useRoute();
const router = useRouter();

onMounted(async () => {
  await store.initStore();
  abrirDesdeQuery();
});

// Abre el detalle cuando se llega desde una notificación (?solicitud=<id>)
const abrirDesdeQuery = async () => {
  const id = route.query.solicitud;
  if (!id) return;
  let solicitud = store.solicitudes.find((s) => s.id === id);
  if (!solicitud) {
    // Puede ser una solicitud recién enviada: recargar antes de rendirse
    await store.cargarTodo();
    solicitud = store.solicitudes.find((s) => s.id === id);
  }
  if (solicitud) {
    abrirDetalle(solicitud);
  } else {
    toast.warning('La solicitud de la notificación ya no existe.');
  }
  // Limpiar el query para que recargar la página no reabra el modal
  router.replace({ query: {} });
};

// Si ya se está en la vista y llega otra notificación, también debe abrirse
watch(() => route.query.solicitud, (id) => {
  if (id) abrirDesdeQuery();
});

// ── Vista y filtros ──
const vista = ref('tablero');
const busqueda = ref('');
const filtroEstado = ref('');
const filtroMunicipio = ref('');
const filtroJornada = ref('');
const filtroInstructor = ref('');

const hayFiltros = computed(
  () =>
    busqueda.value ||
    filtroEstado.value ||
    filtroMunicipio.value ||
    filtroJornada.value ||
    filtroInstructor.value
);

const limpiarFiltros = () => {
  busqueda.value = '';
  filtroEstado.value = '';
  filtroMunicipio.value = '';
  filtroJornada.value = '';
  filtroInstructor.value = '';
};

const filtradas = computed(() => {
  let lista = store.solicitudes;
  if (filtroEstado.value) lista = lista.filter((s) => s.estado === filtroEstado.value);
  if (filtroMunicipio.value) lista = lista.filter((s) => s.municipio === filtroMunicipio.value);
  if (filtroJornada.value) lista = lista.filter((s) => s.jornada === filtroJornada.value);
  if (filtroInstructor.value) lista = lista.filter((s) => s.nombre_instructor === filtroInstructor.value);
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase();
    lista = lista.filter(
      (s) =>
        (s.nombre_programa || '').toLowerCase().includes(q) ||
        (s.codigo_programa || '').toLowerCase().includes(q) ||
        (s.codigo_ficha || '').toLowerCase().includes(q)
    );
  }
  return lista;
});

// Agrupación por estado para el tablero (orden: Publicada → En Ejecución → Cancelada)
const agrupadas = computed(() => {
  const grupos = Object.fromEntries(ESTADOS_TABLERO.map((e) => [e, []]));
  for (const s of filtradas.value) {
    if (grupos[s.estado]) grupos[s.estado].push(s);
  }
  return grupos;
});

// Con filtro de estado activo, el tablero muestra solo esa columna
const columnasVisibles = computed(() =>
  filtroEstado.value ? [filtroEstado.value] : ESTADOS_TABLERO
);

// ── Archivo por mes (respaldo ordenado, tipo carpetas de OneDrive) ──
const mesSeleccionado = ref(null); // clave 'YYYY-MM' de la carpeta abierta

const NOMBRES_MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

const etiquetaMes = (clave) => {
  if (clave === 'sin-fecha') return 'Sin fecha de solicitud';
  const [anio, mes] = clave.split('-');
  return `${NOMBRES_MESES[Number(mes) - 1]} ${anio}`;
};

const nombreMes = (clave) =>
  clave === 'sin-fecha' ? 'Sin fecha' : NOMBRES_MESES[Number(clave.slice(5, 7)) - 1];

// Carpetas creadas por el administrador (períodos preparados de antemano).
// Se guardan en el navegador; cuando el período recibe solicitudes, la carpeta
// pasa a alimentarse de los datos reales sin que se note la diferencia.
const CLAVE_ALMACEN_CARPETAS = 'voltmind_carpetas_complementarias';

const cargarCarpetasManuales = () => {
  try {
    const lista = JSON.parse(localStorage.getItem(CLAVE_ALMACEN_CARPETAS) || '[]');
    return Array.isArray(lista) ? lista.filter((c) => /^\d{4}-\d{2}$/.test(c)) : [];
  } catch {
    return [];
  }
};

const carpetasManuales = ref(cargarCarpetasManuales());

watch(carpetasManuales, (lista) => {
  localStorage.setItem(CLAVE_ALMACEN_CARPETAS, JSON.stringify(lista));
});

// ── Selector de período (mes + año) para "Nueva carpeta" ──
const hoy = new Date();
const claveMesActual = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`;
const ANIO_MINIMO = 2020;
const ANIO_MAXIMO = hoy.getFullYear() + 2;

const showCreadorCarpeta = ref(false);
const anioCreador = ref(hoy.getFullYear());

const alternarCreadorCarpeta = () => {
  showCreadorCarpeta.value = !showCreadorCarpeta.value;
  if (showCreadorCarpeta.value) anioCreador.value = hoy.getFullYear();
};

const claveDe = (anio, mesIndice) => `${anio}-${String(mesIndice + 1).padStart(2, '0')}`;
const carpetaExiste = (clave) => carpetasMeses.value.some((c) => c.clave === clave);
const esManual = (clave) => carpetasManuales.value.includes(clave);

const abrirCarpeta = (clave) => {
  showCreadorCarpeta.value = false;
  mesSeleccionado.value = clave;
};

const crearCarpeta = (mesIndice) => {
  const clave = claveDe(anioCreador.value, mesIndice);
  if (carpetaExiste(clave)) {
    abrirCarpeta(clave);
    toast.info(`La carpeta de ${etiquetaMes(clave)} ya existía; se abrió su contenido.`);
    return;
  }
  carpetasManuales.value = [...carpetasManuales.value, clave];
  abrirCarpeta(clave);
  toast.success(`Carpeta de ${etiquetaMes(clave)} creada.`);
};

const eliminarCarpeta = (clave) => {
  carpetasManuales.value = carpetasManuales.value.filter((c) => c !== clave);
  toast.success(`Carpeta de ${etiquetaMes(clave)} eliminada.`);
};

/** Une las carpetas creadas por el administrador con las que nacen de las solicitudes. */
const carpetasMeses = computed(() => {
  const grupos = new Map();
  for (const clave of carpetasManuales.value) grupos.set(clave, []);
  for (const s of filtradas.value) {
    const clave = (s.fecha_creacion || '').slice(0, 7) || 'sin-fecha';
    if (!grupos.has(clave)) grupos.set(clave, []);
    grupos.get(clave).push(s);
  }
  return [...grupos.entries()]
    .sort(([a], [b]) => (a === 'sin-fecha' ? 1 : b === 'sin-fecha' ? -1 : b.localeCompare(a)))
    .map(([clave, items]) => ({ clave, etiqueta: etiquetaMes(clave), mes: nombreMes(clave), items }));
});

/** Agrupa las carpetas por año para mostrar el archivo con separadores. */
const carpetasPorAnio = computed(() => {
  const grupos = [];
  for (const carpeta of carpetasMeses.value) {
    const anio = carpeta.clave === 'sin-fecha' ? 'Sin fecha' : carpeta.clave.slice(0, 4);
    const ultimo = grupos[grupos.length - 1];
    if (ultimo && ultimo.anio === anio) ultimo.carpetas.push(carpeta);
    else grupos.push({ anio, carpetas: [carpeta] });
  }
  return grupos;
});

const solicitudesDelMes = computed(() => {
  const carpeta = carpetasMeses.value.find((c) => c.clave === mesSeleccionado.value);
  return carpeta ? carpeta.items : [];
});

// ── Helpers de presentación (la tarjeta vive en TarjetaComplementaria.vue) ──
const claseColumna = (estado) => ({
  'col-pendiente': estado === 'Pendiente',
  'col-publicada': estado === 'Publicada',
  'col-ejecucion': estado === 'En Ejecución',
  'col-cancelada': estado === 'Cancelada',
});

// ── Modales ──
const showDetalle = ref(false);
const showForm = ref(false);
const solicitudSeleccionadaId = ref(null);
const solicitudEnEdicion = ref(null);

// Se toma siempre del store para que el modal refleje los PATCH al instante
const solicitudSeleccionada = computed(
  () => store.solicitudes.find((s) => s.id === solicitudSeleccionadaId.value) || null
);

const abrirDetalle = (solicitud) => {
  solicitudSeleccionadaId.value = solicitud.id;
  showDetalle.value = true;
};

const abrirNueva = () => {
  solicitudEnEdicion.value = null;
  showForm.value = true;
};

const abrirEditar = (solicitud) => {
  solicitudEnEdicion.value = { ...solicitud };
  showDetalle.value = false;
  showForm.value = true;
};

// ── Acciones contra el backend ──
const handleGuardar = async (datos) => {
  const resultado = solicitudEnEdicion.value
    ? await store.actualizarSolicitud(solicitudEnEdicion.value.id, datos)
    : await store.crearSolicitud(datos);

  if (resultado.success) {
    toast.success(
      solicitudEnEdicion.value ? 'Solicitud actualizada con éxito.' : 'Solicitud creada con éxito.'
    );
    showForm.value = false;
  } else {
    toast.error(resultado.error);
  }
};

/** PATCH puntual desde el modal de detalle (estado o paso del checklist). */
const handleActualizar = async (id, datos) => {
  const resultado = await store.actualizarSolicitud(id, datos);
  if (!resultado.success) {
    toast.error(resultado.error);
    return;
  }
  if (datos.estado === 'Publicada') {
    toast.success('Ficha publicada. El instructor recibirá el aviso por correo y por la campana.');
  }
};

/** Adjunta (o reemplaza) el Excel de resultados de inscritos de la ficha. */
const subiendoResultados = ref(false);
const handleSubirResultados = async (id, archivo) => {
  if (subiendoResultados.value) return;
  subiendoResultados.value = true;
  const resultado = await store.subirResultados(id, archivo);
  subiendoResultados.value = false;
  if (resultado.success) {
    toast.success('Resultados de inscritos adjuntados a la ficha.');
  } else {
    toast.error(resultado.error);
  }
};

/** Reenvía el aviso de publicación al instructor (correo + campana). */
const enviandoAviso = ref(false);
const handleReenviarAviso = async (solicitud) => {
  if (enviandoAviso.value) return;
  enviandoAviso.value = true;
  const resultado = await store.reenviarAviso(solicitud.id);
  enviandoAviso.value = false;
  if (resultado.success) {
    toast.success(resultado.mensaje);
  } else {
    toast.error(resultado.error);
  }
};

const confirmarEliminar = async (solicitud) => {
  const { isConfirmed } = await Swal.fire({
    title: '¿Eliminar la solicitud?',
    text: `Se eliminará "${solicitud.nombre_programa}" de ${solicitud.nombre_instructor}. Esta acción no se puede deshacer.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#E53E3E',
    cancelButtonColor: '#39A900',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  });
  if (!isConfirmed) return;

  const resultado = await store.eliminarSolicitud(solicitud.id);
  if (resultado.success) {
    toast.success('Solicitud eliminada con éxito.');
    showDetalle.value = false;
  } else {
    toast.error(resultado.error);
  }
};
</script>

<style scoped>
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL (SENA 2024) — mismo shell del panel
   ========================================================================== */
.admin-view-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
  box-sizing: border-box;
}

.dash-header {
  position: relative; /* referencia para la campana de notificaciones */
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  padding-right: 5.5rem; /* reserva la esquina para la campana */
  border-radius: 16px;
  border: 1px solid var(--borde);
  border-left: 5px solid var(--sena-verde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  gap: 1rem;
  flex-wrap: wrap;
}

.environment-badge h1 {
  font-size: 1.4rem;
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

/* La campana deja de flotar sobre toda la app (position: fixed del componente)
   y se ancla a la esquina superior derecha del encabezado de esta sección. */
.dash-header .campana-header {
  position: absolute;
  top: 1.1rem;
  right: 1.25rem;
  bottom: auto;
}

/* El panel de avisos siempre se despliega hacia abajo, pegado a la campana */
.dash-header .campana-header :deep(.panel) {
  top: 56px;
  bottom: auto;
  right: 0;
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

/* ── Tarjetas contenedoras ── */
.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

.filtros-card {
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}

/* ── Filtros ── */
.filters-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  position: relative;
  min-width: 260px;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
  font-size: 0.9rem;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.65rem 1rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input {
  width: 100%;
  padding-left: 2.2rem;
  box-sizing: border-box;
}

.select-filter {
  min-width: 150px;
  cursor: pointer;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.btn-limpiar {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-limpiar:hover {
  border-color: #e53e3e;
  color: #e53e3e;
}

/* ── Estados de carga / vacío / error ── */
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

.estado-panel strong {
  color: var(--texto-principal);
  display: block;
  margin-bottom: 4px;
}

.estado-panel p {
  margin: 0;
  font-size: 0.85rem;
}

.estado-icono {
  font-size: 1.8rem;
  color: var(--sena-verde);
}

.estado-error .estado-icono {
  color: var(--sena-amarillo);
}

/* ══ TABLERO POR ESTADO ══ */
.tablero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  align-items: start;
}

.columna {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.col-pendiente { border-top: 4px solid #fdc300; }
.col-publicada { border-top: 4px solid var(--sena-azul-oscuro); }
.col-ejecucion { border-top: 4px solid var(--sena-verde); }
.col-cancelada { border-top: 4px solid #e53e3e; }

.columna-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0.5rem;
}

.columna-header h2 {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin: 0;
  color: var(--texto-principal);
}

.columna-contador {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  min-width: 28px;
  text-align: center;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario);
}

.columna-vacia {
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  font-style: italic;
  padding: 1.5rem 0.5rem;
  margin: 0;
  border: 1px dashed var(--borde);
  border-radius: 12px;
}

/* La tarjeta de solicitud y sus estilos viven en TarjetaComplementaria.vue */

/* ══ CARPETAS POR MES ══ */
.carpetas-vista {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.carpetas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.carpeta {
  position: relative;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem 1rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  box-shadow: 0 4px 12px var(--sombra-suave);
  transition: all 0.2s ease;
}

.carpeta:hover,
.carpeta:focus-visible {
  border-color: var(--sena-verde);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(57, 169, 0, 0.15);
  outline: none;
}

.carpeta-icono {
  font-size: 2.4rem;
  color: #fdc300;
}

.carpeta-nombre {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

.carpeta-conteo {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

/* Carpeta creada de antemano, todavía sin solicitudes */
.carpeta.vacia {
  border-style: dashed;
  box-shadow: none;
}

.carpeta.vacia .carpeta-icono {
  opacity: 0.45;
}

.chip-mes-actual {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(57, 169, 0, 0.14);
  color: var(--sena-verde-oscuro);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 99px;
}

[data-theme="dark"] .chip-mes-actual {
  color: var(--sena-verde);
}

.carpeta-borrar {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--texto-secundario);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.carpeta:hover .carpeta-borrar,
.carpeta-borrar:focus-visible {
  opacity: 1;
}

.carpeta-borrar:hover {
  background: rgba(229, 62, 62, 0.12);
  color: #e53e3e;
}

/* ── Barra del archivo mensual ── */
.archivo-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.5rem;
  border-left: 4px solid #fdc300;
}

.archivo-eyebrow {
  margin: 0;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.archivo-eyebrow svg {
  color: #fdc300;
}

.archivo-hint {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.btn-nueva-carpeta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  border: 1.5px dashed var(--sena-verde);
  background: transparent;
  color: var(--sena-verde-oscuro);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-nueva-carpeta:hover,
.btn-nueva-carpeta:focus-visible {
  background: rgba(57, 169, 0, 0.08);
  border-style: solid;
  outline: none;
}

.btn-nueva-carpeta.abierto {
  border-style: solid;
  color: var(--texto-secundario);
  border-color: var(--borde);
}

[data-theme="dark"] .btn-nueva-carpeta {
  color: var(--sena-verde);
}

/* ── Selector de período (mes + año) ── */
.creador-carpeta {
  padding: 1.2rem 1.5rem;
}

.creador-anio {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.2rem;
  margin-bottom: 1rem;
}

.anio-actual {
  min-width: 64px;
  text-align: center;
  font-size: 1.15rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--texto-principal);
}

.anio-flecha {
  width: 34px;
  height: 34px;
  border: 1px solid var(--borde);
  border-radius: 10px;
  background: var(--fondo-app);
  color: var(--texto-principal);
  cursor: pointer;
  transition: all 0.2s ease;
}

.anio-flecha:hover:not(:disabled) {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.anio-flecha:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.creador-meses {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

.mes-opcion {
  position: relative;
  padding: 0.65rem 0.25rem;
  border: 1px solid var(--borde);
  border-radius: 10px;
  background: var(--fondo-app);
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mes-opcion:hover,
.mes-opcion:focus-visible {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.06);
  outline: none;
}

.mes-opcion.actual {
  border-color: var(--sena-verde);
  box-shadow: inset 0 0 0 1px var(--sena-verde);
}

.mes-opcion.existente {
  background: rgba(253, 195, 0, 0.12);
  border-color: rgba(253, 195, 0, 0.55);
}

.mes-marca {
  position: absolute;
  top: 3px;
  right: 6px;
  font-size: 0.58rem;
  color: #fdc300;
}

.creador-nota {
  margin: 0.9rem 0 0;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  text-align: center;
}

.creador-nota svg {
  color: #fdc300;
}

.creador-enter-active,
.creador-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.creador-enter-from,
.creador-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Carpetas agrupadas por año ── */
.archivo-anio {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.anio-etiqueta {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 10px;
}

.anio-etiqueta::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--borde);
}

@media (prefers-reduced-motion: reduce) {
  .creador-enter-active,
  .creador-leave-active {
    transition: none;
  }
  .carpeta:hover,
  .carpeta:focus-visible {
    transform: none;
  }
}

.carpeta-abierta-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-volver {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-volver:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.carpeta-titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.carpeta-titulo svg {
  color: #fdc300;
}

.carpeta-contenido {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

/* ── Responsive ── */
@media (max-width: 992px) {
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    padding-right: 2rem; /* vuelve al padding simétrico */
    padding-top: 4.25rem; /* la campana queda sola arriba, sin chocar con el título */
  }
  .header-meta {
    justify-content: center;
  }
  .header-actions {
    justify-content: center;
  }
  .btn-action {
    flex: 1;
    justify-content: center;
  }
  .filters-group {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box,
  .select-filter {
    width: 100%;
    min-width: 0;
  }
  .tablero {
    grid-template-columns: 1fr;
  }
  .creador-meses {
    grid-template-columns: repeat(4, 1fr);
  }
  .archivo-toolbar {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  .archivo-eyebrow {
    justify-content: center;
  }
  .btn-nueva-carpeta {
    justify-content: center;
  }
}
</style>
