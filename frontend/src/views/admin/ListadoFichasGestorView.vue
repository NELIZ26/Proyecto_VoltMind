<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>FICHAS CREADAS</h1>
          <p class="header-meta">
            Visualice el listado general de fichas y edite las competencias.
          </p>
        </div>
      </div>
    </header>

    <!-- Filtros -->
    <div class="module-card filtros-card" style="margin-bottom: 24px;">
      <div class="filters-group">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por código o programa..."
          />
        </div>
        <select v-model="filtroJornada" class="form-input select-filter">
          <option value="">Todas las jornadas</option>
          <option v-for="j in JORNADAS_TITULADAS" :key="j.valor" :value="j.valor">
            {{ j.valor }} ({{ j.horario }})
          </option>
        </select>
        <select v-model="filtroMunicipio" class="form-input select-filter">
          <option value="">Todos los municipios</option>
          <option v-for="s in store.municipios" :key="s" :value="s">{{ s }}</option>
        </select>
        <button v-if="hayFiltros" class="btn-limpiar" @click="limpiarFiltros">
          <font-awesome-icon icon="fa-solid fa-xmark" /> Limpiar
        </button>
      </div>
    </div>

    <main class="module-card">
      <div class="table-toolbar">
        <h2 class="module-title">
          <font-awesome-icon icon="fa-solid fa-clipboard-list" /> DIRECTORIO DE FICHAS TITULADAS
        </h2>
        <span class="tabla-conteo" style="color: #8a8d93; font-size: 14px;">
          {{ fichasFiltradas.length }} de {{ (store.fichas || []).length }} fichas
        </span>
      </div>

      <div class="table-responsive-wrapper">
        <table class="apprentices-table">
          <thead>
            <tr>
              <th class="text-left">CÓDIGO (SOFÍA)</th>
              <th class="text-left">PROGRAMA DE FORMACIÓN</th>
              <th class="text-left">INSTRUCTOR TITULAR</th>
              <th class="text-center">JORNADA</th>
              <th class="text-center">MUNICIPIO</th>
              <th class="text-center">HORAS</th>
              <th class="text-center">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargando">
              <td colspan="7" class="text-center" style="padding: 32px; color: var(--texto-secundario);">
                <font-awesome-icon icon="fa-solid fa-circle-notch" spin /> Cargando fichas...
              </td>
            </tr>
            <tr v-else-if="fichasFiltradas.length === 0">
              <td colspan="7" class="text-center" style="padding: 32px; color: var(--texto-secundario);">
                No se encontraron fichas.
              </td>
            </tr>
            <tr v-for="ficha in fichasPaginadas" :key="ficha.id" class="fila-ficha">
              <td><strong>{{ ficha.codigo }}</strong></td>
              <td>
                <div class="programa-info">
                  <span class="programa-nombre">{{ ficha.programa }}</span>
                  <span class="programa-nivel">{{ ficha.nivel }}</span>
                </div>
              </td>
              <td>
                <div class="titular-container">
                  <span v-if="store.actualizandoTitularId === ficha.id" class="titular">
                    <font-awesome-icon :icon="['fas', 'circle-notch']" spin />
                    Guardando...
                  </span>
                  <span v-else-if="ficha.instructor_titular" class="titular">
                    <span class="punto-color" :style="{ background: ficha.instructor_titular.color }"></span>
                    {{ ficha.instructor_titular.nombre }}
                  </span>
                  <span v-else class="titular sin-titular">Pendiente por asignar</span>
                </div>
              </td>
              <td class="text-center">
                <span class="badge-jornada" :class="`jornada-${(ficha.jornada || '').toLowerCase()}`">
                  {{ ficha.jornada }}
                  <small>{{ horarioJornada(ficha.jornada) }}</small>
                </span>
              </td>
              <td class="text-center">{{ ficha.municipio }}</td>
              <td class="text-center">{{ ficha.horas_programa_formacion || 'N/A' }}</td>
              <td class="text-center">
                <div class="acciones-container">
                  <button
                    class="btn-mini-accion"
                    title="Gestionar Competencias de la Ficha"
                    @click="abrirCompetencias(ficha)"
                    :disabled="cargandoFichaId === ficha.id"
                  >
                    <font-awesome-icon v-if="cargandoFichaId === ficha.id" icon="fa-solid fa-circle-notch" spin />
                    <font-awesome-icon v-else icon="fa-solid fa-list-check" />
                  </button>
                  <button
                    class="btn-mini-accion"
                    title="Asignar Instructor Titular"
                    @click="abrirAsignarTitular(ficha)"
                  >
                    <font-awesome-icon icon="fa-solid fa-user-plus" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="totalPaginas > 1" class="paginacion-container">
        <button 
          class="btn-paginacion" 
          :disabled="paginaActual === 1" 
          @click="paginaActual--"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-left" />
        </button>
        <span class="paginacion-info">
          Página {{ paginaActual }} de {{ totalPaginas }}
        </span>
        <button 
          class="btn-paginacion" 
          :disabled="paginaActual === totalPaginas" 
          @click="paginaActual++"
        >
          <font-awesome-icon icon="fa-solid fa-chevron-right" />
        </button>
      </div>
    </main>

    <!-- Modal para editar las competencias de la ficha -->
    <ModalDiagnostico
      v-model:show="showModalDiagnostico"
      :ficha="fichaSeleccionada"
      @close="store.cargarDetalle(fichaSeleccionada.id)"
    />

    <!-- Modal para asignar titular -->
    <ModalAsignarTitular
      v-model:show="showModalTitular"
      :ficha="fichaAsignarTitular"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useTituladasStore, JORNADAS_TITULADAS, horarioJornada } from '@/stores/tituladas';
import ModalDiagnostico from '@/components/admin/modals/ModalDiagnostico.vue';
import ModalAsignarTitular from '@/components/admin/modals/ModalAsignarTitular.vue';

const store = useTituladasStore();
const busqueda = ref('');
const filtroJornada = ref('');
const filtroMunicipio = ref('');
const cargando = ref(true);

const showModalDiagnostico = ref(false);
const fichaSeleccionada = ref(null);

const showModalTitular = ref(false);
const fichaAsignarTitular = ref(null);

onMounted(async () => {
  await store.initStore();
  cargando.value = false;
});

const fichasFiltradas = computed(() => {
  // Revertimos el orden para que las últimas creadas salgan primero
  let resultado = [...(store.fichas || [])].reverse();

  if (filtroJornada.value) {
    resultado = resultado.filter((f) => f.jornada === filtroJornada.value);
  }

  if (filtroMunicipio.value) {
    const norm = (s) => (s || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, ' ').toLowerCase().trim();
    const filtroNorm = norm(filtroMunicipio.value);
    resultado = resultado.filter((f) => norm(f.municipio) === filtroNorm);
  }

  if (busqueda.value) {
    const t = busqueda.value.toLowerCase();
    resultado = resultado.filter(
      (f) =>
        (f.codigo && f.codigo.toLowerCase().includes(t)) ||
        (f.programa && f.programa.toLowerCase().includes(t))
    );
  }
  return resultado;
});

const paginaActual = ref(1);
const elementosPorPagina = 10;

const totalPaginas = computed(() => Math.ceil(fichasFiltradas.value.length / elementosPorPagina));

const fichasPaginadas = computed(() => {
  const inicio = (paginaActual.value - 1) * elementosPorPagina;
  const fin = inicio + elementosPorPagina;
  return fichasFiltradas.value.slice(inicio, fin);
});

// Reiniciar a la primera página si cambian los filtros
watch([busqueda, filtroJornada, filtroMunicipio], () => {
  paginaActual.value = 1;
});

const hayFiltros = computed(() => {
  return busqueda.value !== '' || filtroJornada.value !== '' || filtroMunicipio.value !== '';
});

const limpiarFiltros = () => {
  busqueda.value = '';
  filtroJornada.value = '';
  filtroMunicipio.value = '';
  paginaActual.value = 1;
};

const cargandoFichaId = ref(null);

const abrirCompetencias = async (ficha) => {
  cargandoFichaId.value = ficha.id;
  await store.cargarDetalle(ficha.id);
  fichaSeleccionada.value = store.fichaActual;
  showModalDiagnostico.value = true;
  cargandoFichaId.value = null;
};

const abrirAsignarTitular = (ficha) => {
  fichaAsignarTitular.value = ficha;
  showModalTitular.value = true;
};

</script>

<style scoped>
.admin-view-shell {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
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
.environment-badge h1 {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--texto-principal);
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
.module-card {
  background: var(--fondo-tarjetas, #1E232B);
  border: 1px solid var(--borde, #2D333B);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.module-title {
  color: var(--texto-principal, #ffffff);
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.search-box {
  position: relative;
  width: 300px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #8a8d93;
}
.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--borde, #2D333B);
  border-radius: 6px;
  color: white;
}
.table-responsive-wrapper {
  overflow-x: auto;
}
.apprentices-table {
  width: 100%;
  border-collapse: collapse;
}
.apprentices-table th {
  padding: 12px;
  font-size: 12px;
  color: #8a8d93;
  border-bottom: 1px solid var(--borde, #2D333B);
}
.text-left {
  text-align: left;
}
.text-center {
  text-align: center;
}
.apprentices-table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  vertical-align: middle;
}
.text-center {
  text-align: center;
}
.programa-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 200px;
}

.programa-nombre { font-weight: 700; color: var(--texto-principal); }
.programa-nivel { font-size: 0.7rem; color: var(--texto-secundario); }

.badge-jornada {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.2;
}

.badge-jornada small { font-size: 0.62rem; font-weight: 600; opacity: 0.8; }

.jornada-mañana { background: rgba(253, 195, 0, 0.15); color: #8a6d00; }
.jornada-tarde { background: rgba(230, 126, 34, 0.15); color: #b35c0e; }
.jornada-noche { background: rgba(41, 128, 185, 0.15); color: #1f618d; }

[data-theme="dark"] .jornada-mañana { color: #fdc300; }
[data-theme="dark"] .jornada-tarde { color: #e67e22; }
[data-theme="dark"] .jornada-noche { color: #5dade2; }
.btn-mini-accion {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--borde, #2D333B);
  color: var(--texto-secundario, #8a8d93);
  width: 34px;
  height: 34px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-mini-accion:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--texto-principal);
  color: var(--texto-principal);
}
.btn-mini-accion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fila-ficha {
  transition: background 0.2s;
}
.fila-ficha:hover {
  background: rgba(57, 169, 0, 0.05);
}

.filtros-card {
  margin-bottom: 24px;
}
.filters-group {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}
.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
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
.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}
.search-input {
  width: 100%;
  padding-left: 2.2rem;
  box-sizing: border-box;
}
.select-filter {
  min-width: 170px;
  cursor: pointer;
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
  background: rgba(220, 53, 69, 0.05);
  border-color: rgba(220, 53, 69, 0.3);
  color: #dc3545;
}

.acciones-container {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.titular-container {
  display: flex;
  align-items: center;
}

.titular {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  white-space: nowrap;
}

.sin-titular { color: var(--texto-secundario); font-style: italic; font-weight: 400; }

.punto-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.paginacion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--borde, #2D333B);
}

.btn-paginacion {
  background: var(--fondo-app, #161B22);
  border: 1px solid var(--borde, #2D333B);
  color: var(--texto-secundario, #8a8d93);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-paginacion:hover:not(:disabled) {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.btn-paginacion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paginacion-info {
  font-size: 0.85rem;
  color: var(--texto-secundario, #8a8d93);
  font-weight: 600;
}
</style>
