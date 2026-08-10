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
          </p>
        </div>
      </div>
      <div class="header-actions">
        <!-- Navegación por pestañas reales -->
        <div class="tabs-navegacion" role="tablist">
          <router-link 
            to="/programador-complementarios/fichas/tablero" 
            class="tab-link"
            active-class="activo"
            role="tab"
          >
            <font-awesome-icon icon="fa-solid fa-table-columns" /> Tablero
          </router-link>
          <router-link 
            to="/programador-complementarios/fichas/archivo" 
            class="tab-link"
            active-class="activo"
            role="tab"
          >
            <font-awesome-icon icon="fa-solid fa-folder-open" /> Histórico
          </router-link>
        </div>
        <button class="btn-action" @click="abrirNueva">
          <font-awesome-icon icon="fa-solid fa-plus" />
          <span>NUEVA SOLICITUD</span>
        </button>
      </div>
      <!-- Campana de notificaciones -->
      <NotificacionesBell class="campana-header" />
    </header>

    <!-- Filtros Globales (Afectan tanto al Tablero como al Archivo) -->
    <div class="module-card filtros-card">
      <div class="filters-group">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="store.busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por programa o código de ficha..."
          />
        </div>
        <select v-model="store.filtroEstado" class="form-input select-filter">
          <option value="">Todos los estados</option>
          <option v-for="e in ESTADOS_TABLERO" :key="e" :value="e">{{ e }}</option>
        </select>
        <select v-model="store.filtroMunicipio" class="form-input select-filter">
          <option value="">Todos los municipios</option>
          <option v-for="m in store.municipios" :key="m" :value="m">{{ m }}</option>
        </select>
        <select v-model="store.filtroJornada" class="form-input select-filter">
          <option value="">Todas las jornadas</option>
          <option v-for="j in JORNADAS" :key="j" :value="j">{{ j }}</option>
        </select>
        <select v-model="store.filtroInstructor" class="form-input select-filter">
          <option value="">Todos los instructores</option>
          <option v-for="i in store.instructores" :key="i" :value="i">{{ i }}</option>
        </select>
        <button v-if="hayFiltros" class="btn-limpiar" @click="limpiarFiltros">
          <font-awesome-icon icon="fa-solid fa-xmark" /> Limpiar
        </button>
      </div>
    </div>

    <!-- Estados de carga o error -->
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

    <div v-else-if="store.cargando && store.solicitudes.length === 0" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando solicitudes de formación complementaria...</p>
    </div>

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

    <!-- Vistas Hijas (Tablero o Archivo) -->
    <router-view v-else @abrir-detalle="abrirDetalle"></router-view>

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
    await store.cargarTodo();
    solicitud = store.solicitudes.find((s) => s.id === id);
  }
  if (solicitud) {
    abrirDetalle(solicitud);
  } else {
    toast.warning('La solicitud de la notificación ya no existe.');
  }
  router.replace({ query: {} });
};

watch(() => route.query.solicitud, (id) => {
  if (id) abrirDesdeQuery();
});

const hayFiltros = computed(
  () =>
    store.busqueda ||
    store.filtroEstado ||
    store.filtroMunicipio ||
    store.filtroJornada ||
    store.filtroInstructor
);

const limpiarFiltros = () => {
  store.busqueda = '';
  store.filtroEstado = '';
  store.filtroMunicipio = '';
  store.filtroJornada = '';
  store.filtroInstructor = '';
};

// ── Modales ──
const showDetalle = ref(false);
const showForm = ref(false);
const solicitudSeleccionadaId = ref(null);
const solicitudEnEdicion = ref(null);

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
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  padding-right: 5.5rem;
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

.dash-header .campana-header {
  position: absolute;
  top: 1.1rem;
  right: 1.25rem;
  bottom: auto;
}

.dash-header .campana-header :deep(.panel) {
  top: 56px;
  bottom: auto;
  right: 0;
}

.tabs-navegacion {
  display: flex;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  overflow: hidden;
}

.tab-link {
  text-decoration: none;
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

.tab-link.activo {
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

/* ── Responsive ── */
@media (max-width: 992px) {
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    padding-right: 2rem;
    padding-top: 4.25rem;
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
}
</style>
