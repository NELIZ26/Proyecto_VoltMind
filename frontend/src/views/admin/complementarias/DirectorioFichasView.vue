<template>
  <div class="admin-view-shell">
    
    <!-- Encabezado y Tarjetas de Resumen -->
    <header class="top-panel">
      <div class="welcome-section">
        <h1>{{ codigoFiltro ? `Resumen Ficha ${codigoFiltro}` : 'Resumen de Complementarias' }}</h1>
        <p>{{ codigoFiltro ? 'Vista general de las solicitudes bajo este código' : 'Vista general del estado de la formación complementaria' }}</p>
      </div>
      
      <div class="summary-cards">
        <article class="summary-card">
          <div class="card-icon">
            <font-awesome-icon icon="fa-solid fa-graduation-cap" />
          </div>
          <div class="card-data">
            <h3>Total Fichas</h3>
            <p class="card-value">{{ todasLasFichas.length }}</p>
          </div>
        </article>
        
        <article class="summary-card highlight">
          <div class="card-icon">
            <font-awesome-icon icon="fa-solid fa-check-circle" />
          </div>
          <div class="card-data">
            <h3>Meta de Programación</h3>
            <p class="card-value">85%</p>
          </div>
        </article>

        <article class="summary-card">
          <div class="card-icon">
            <font-awesome-icon icon="fa-solid fa-clock-rotate-left" />
          </div>
          <div class="card-data">
            <h3>En Ejecución</h3>
            <p class="card-value">{{ todasLasFichas.filter(f => f.estado === 'En Ejecución').length }}</p>
          </div>
        </article>
      </div>
    </header>

    <!-- Filtros de Búsqueda -->
    <div class="filtros-card">
      <div class="filters-group">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por código, programa o instructor..."
          />
        </div>
        <select v-model="filtroJornada" class="form-input select-filter">
          <option value="">Todas las jornadas</option>
          <option v-for="j in ['Mañana', 'Tarde', 'Noche', 'Mixta']" :key="j" :value="j">{{ j }}</option>
        </select>
        <select v-model="filtroEstado" class="form-input select-filter">
          <option value="">Todos los estados</option>
          <option v-for="e in ['Pendiente', 'Publicada', 'En Ejecución', 'Cancelada']" :key="e" :value="e">{{ e }}</option>
        </select>
        <button v-if="busqueda || filtroJornada || filtroEstado" class="btn-limpiar" @click="limpiarFiltros">
          <font-awesome-icon icon="fa-solid fa-xmark" /> Limpiar
        </button>
      </div>
    </div>

    <!-- Panel de Tabla -->
    <section class="table-container">
      <div class="table-header">
        <div class="table-title">
          <h2>{{ codigoFiltro ? 'SOLICITUDES EN ESTA FICHA' : 'Directorio de Fichas' }}</h2>
          <span class="tabla-conteo" v-if="fichasFiltradas">
            {{ fichasFiltradas.length }} de {{ todasLasFichas.length }}
          </span>
        </div>
        <div class="header-actions">
          <router-link v-if="codigoFiltro" to="/programador-complementarios/directorio" class="btn-secondary">
            <font-awesome-icon icon="fa-solid fa-layer-group" />
            <span>VER TODO EL DIRECTORIO</span>
          </router-link>
          <button class="btn-primary">
            <font-awesome-icon icon="fa-solid fa-plus" /> Nueva Ficha
          </button>
        </div>
      </div>

      <div v-if="cargando" class="estado-panel">
        <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
        <p>Cargando información desde el servidor...</p>
      </div>
      
      <p v-else-if="fichasFiltradas.length === 0" class="tabla-vacia">
        No hay solicitudes que coincidan con los filtros aplicados.
      </p>

      <div v-else class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>CÓDIGO</th>
              <th>PROGRAMA DE FORMACIÓN</th>
              <th>INSTRUCTOR TITULAR</th>
              <th class="text-center">JORNADA</th>
              <th>SEDE</th>
              <th>PROGRAMACIÓN</th>
              <th class="text-center">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ficha in fichasFiltradas" :key="ficha.id" class="table-row">
              <td class="col-codigo">{{ ficha.codigo_ficha || 'Sin asignar' }}</td>
              <td class="col-programa">
                <span class="programa-nombre">{{ ficha.nombre_programa }}</span>
              </td>
              <td class="col-instructor">
                <div class="instructor-info" v-if="ficha.nombre_instructor">
                  <span class="dot-indicator"></span>
                  {{ ficha.nombre_instructor }}
                </div>
                <div v-else class="instructor-info sin-instructor">Sin instructor</div>
              </td>
              <td class="text-center">
                <span class="badge" :class="`badge-${(ficha.jornada || '').toLowerCase()}`">
                  {{ ficha.jornada || 'N/A' }}
                </span>
              </td>
              <td class="col-sede">{{ ficha.lugar_ejecucion }}</td>
              <td class="col-progreso">
                <div class="progress-wrapper">
                  <div class="progress-track">
                    <div class="progress-fill" :style="{ width: `${ficha.progreso}%` }"></div>
                  </div>
                  <span class="progress-text">{{ ficha.progreso }}%</span>
                </div>
              </td>
              <td class="text-center">
                <button class="btn-icon" title="Ver detalles" @click="$router.push('/programador-complementarios/fichas/' + ficha.id)">
                  <font-awesome-icon icon="fa-solid fa-eye" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const codigoFiltro = ref(route.query.codigo || null);
const busqueda = ref('');
const filtroJornada = ref('');
const filtroEstado = ref('');

const limpiarFiltros = () => {
  busqueda.value = '';
  filtroJornada.value = '';
  filtroEstado.value = '';
};

watch(() => route.query.codigo, (newCodigo) => {
  codigoFiltro.value = newCodigo || null;
});

const cargando = ref(false);
const todasLasFichas = ref([]);

const fichasFiltradas = computed(() => {
  let lista = todasLasFichas.value;
  
  if (codigoFiltro.value) {
    lista = lista.filter(f => f.codigo_ficha === codigoFiltro.value);
  }
  if (filtroEstado.value) {
    lista = lista.filter(f => f.estado === filtroEstado.value);
  }
  if (filtroJornada.value) {
    lista = lista.filter(f => f.jornada === filtroJornada.value);
  }
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase();
    lista = lista.filter(f => 
      (f.codigo_ficha || '').toLowerCase().includes(q) ||
      (f.nombre_programa || '').toLowerCase().includes(q) ||
      (f.nombre_instructor || '').toLowerCase().includes(q)
    );
  }
  
  return lista;
});

onMounted(() => {
  // Datos mock que cumplen los requisitos exactos solicitados
  todasLasFichas.value = [
    {
      id: 1,
      codigo_ficha: '2997671',
      nombre_programa: 'Análisis y Desarrollo de Software',
      nombre_instructor: 'Ferley Tobon',
      lugar_ejecucion: 'Principal Puerto Asís',
      jornada: 'Mañana',
      estado: 'En Ejecución',
      progreso: 65
    },
    {
      id: 2,
      codigo_ficha: '3012458',
      nombre_programa: 'Gestión Contable y de Información Financiera',
      nombre_instructor: 'Martha Lucía Ramírez',
      lugar_ejecucion: 'Sede Centro',
      jornada: 'Tarde',
      estado: 'Pendiente',
      progreso: 42
    },
    {
      id: 3,
      codigo_ficha: '2895641',
      nombre_programa: 'Asistencia Administrativa',
      nombre_instructor: 'Carlos Alberto Ruiz',
      lugar_ejecucion: 'Principal Puerto Asís',
      jornada: 'Noche',
      estado: 'En Ejecución',
      progreso: 88
    },
    {
      id: 4,
      codigo_ficha: '3104592',
      nombre_programa: 'Cocina',
      nombre_instructor: 'Diana Carolina Méndez',
      lugar_ejecucion: 'Sede Gastronomía',
      jornada: 'Mañana',
      estado: 'Cancelada',
      progreso: 15
    }
  ];
});
</script>

<style scoped>
/* ─── ÁREA PRINCIPAL ─── */
.admin-view-shell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.top-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.welcome-section h1 {
  margin: 0 0 0.25rem 0;
  color: var(--sena-azul-oscuro);
  font-size: 1.5rem;
  font-weight: 800;
}
.welcome-section p {
  margin: 0;
  color: var(--texto-principal);
  opacity: 0.7;
  font-size: 0.9rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.summary-card {
  background-color: var(--fondo-tarjetas);
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 15px -5px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.08);
}

.summary-card.highlight {
  background-color: var(--sena-azul-oscuro);
  color: white;
}
.summary-card.highlight .card-data h3 {
  color: rgba(255, 255, 255, 0.8);
}
.summary-card.highlight .card-value {
  color: white;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: var(--fondo-app);
  color: var(--sena-verde);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}
.summary-card.highlight .card-icon {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.card-data {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.card-data h3 {
  margin: 0;
  font-size: 0.75rem;
  color: var(--texto-principal);
  opacity: 0.7;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.card-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

/* ─── FILTROS ─── */
.filtros-card {
  background-color: var(--fondo-tarjetas);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}

.filters-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 220px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-principal);
  opacity: 0.5;
  font-size: 0.85rem;
}

.search-input {
  width: 100%;
  padding-left: 2.25rem;
  box-sizing: border-box;
}

.form-input {
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 3px rgba(57, 169, 0, 0.1);
}

.select-filter {
  min-width: 160px;
  cursor: pointer;
}

.btn-limpiar {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-limpiar:hover {
  background-color: #fef2f2;
}


/* ─── TABLA DE DATOS ─── */
.table-container {
  background-color: var(--fondo-tarjetas);
  border-radius: 18px;
  box-shadow: 0 8px 25px -8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--borde);
  flex-wrap: wrap;
  gap: 1rem;
}
.table-title {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.table-header h2 {
  margin: 0;
  color: var(--sena-azul-oscuro);
  font-size: 1.25rem;
  font-weight: 700;
}
.tabla-conteo {
  background: var(--fondo-app);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  background-color: var(--sena-verde);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: opacity 0.2s;
}
.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background-color: var(--fondo-app);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  transition: all 0.2s ease;
}
.btn-secondary:hover {
  background-color: rgba(0,0,0,0.03);
}


.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  padding: 1rem 1.25rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--texto-principal);
  opacity: 0.6;
  font-weight: 700;
  border-bottom: 1px solid var(--borde);
}

.data-table td {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--borde);
  color: var(--texto-principal);
  font-size: 0.85rem;
  font-weight: 500;
}

.table-row {
  transition: background-color 0.2s ease;
}
.table-row:hover {
  background-color: var(--fondo-app);
}
.table-row:last-child td {
  border-bottom: none;
}

.col-codigo {
  font-weight: 700 !important;
  color: var(--sena-azul-oscuro) !important;
}

.programa-nombre {
  font-weight: 600;
}

.instructor-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.sin-instructor {
  opacity: 0.5;
  font-style: italic;
}
.dot-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--sena-verde);
}

.col-sede {
  color: var(--texto-principal);
  opacity: 0.8;
}

/* Badges Dinámicos */
.badge {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
/* Usamos opacidades simuladas con colores base si es necesario */
.badge-mañana, .badge-manana {
  background-color: rgba(254, 243, 199, 0.6); /* Tono amarillo suave */
  color: #b45309;
}
.badge-tarde {
  background-color: rgba(255, 237, 213, 0.6); /* Tono naranja suave */
  color: #c2410c;
}
.badge-noche {
  background-color: rgba(224, 231, 255, 0.6); /* Tono azul/morado suave */
  color: #4338ca;
}
.badge-mixta {
  background-color: rgba(243, 244, 246, 0.6); 
  color: #374151;
}

/* Barras de progreso */
.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.progress-track {
  flex: 1;
  height: 6px;
  background-color: var(--borde);
  border-radius: 99px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background-color: var(--sena-verde);
  border-radius: 99px;
  transition: width 0.5s ease;
}
.progress-text {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  width: 35px;
}

/* Botones de acción */
.btn-icon {
  background: transparent;
  border: none;
  color: var(--texto-principal);
  opacity: 0.5;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}
.btn-icon:hover {
  background-color: var(--fondo-app);
  color: var(--sena-verde);
  opacity: 1;
}

.text-center {
  text-align: center !important;
}

.estado-panel, .tabla-vacia {
  padding: 4rem 2rem;
  text-align: center;
  color: var(--texto-secundario);
}
.estado-icono {
  font-size: 2rem;
  color: var(--sena-verde);
  margin-bottom: 1rem;
}
</style>
