<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1><font-awesome-icon :icon="['fas', 'chalkboard-user']" /> INSTRUCTORES</h1>
          <p class="header-meta">
            Seleccione un instructor para ver su calendario de programación
          </p>
        </div>
      </div>
    </header>

    <div v-if="cargando" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando instructores...</p>
    </div>
    
    <div v-else-if="error" class="module-card estado-panel estado-error">
      <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="estado-icono" />
      <p>{{ error }}</p>
    </div>

    <main v-else class="module-card">
      <div class="filtros-bar">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por nombre o vinculación..."
          />
        </div>
      </div>
      
      <div class="tabla-scroll mt-3">
        <table class="tabla-fichas">
          <thead>
            <tr>
              <th>INSTRUCTOR</th>
              <th class="text-center">VINCULACIÓN</th>
              <th class="text-center">CORREO</th>
              <th class="text-center">ACCIÓN</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in instructoresPaginados" :key="i.id" class="fila-ficha" @click="verCalendario(i)">
              <td>
                <div class="instructor-cell">
                  <span class="punto-color" :style="{ background: i.color }"></span>
                  <strong>{{ i.nombre }}</strong>
                </div>
              </td>
              <td class="text-center">
                <span class="badge-vinculacion" :class="`badge-${(i.tipo_vinculacion || '').toLowerCase()}`">
                  {{ i.tipo_vinculacion }}
                </span>
              </td>
              <td class="text-center">{{ i.correo }}</td>
              <td class="text-center">
                <button class="btn-tabla" title="Ver Calendario" @click.stop="verCalendario(i)">
                  <font-awesome-icon icon="fa-solid fa-calendar-days" />
                </button>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { tituladasService } from '@/services/tituladasService';

const router = useRouter();
const instructores = ref([]);
const cargando = ref(true);
const error = ref('');
const busqueda = ref('');

// Paginación
const paginaActual = ref(1);
const elementosPorPagina = 10;

onMounted(async () => {
  try {
    const data = await tituladasService.getInstructores();
    instructores.value = data.sort((a, b) => a.nombre.localeCompare(b.nombre));
  } catch (e) {
    error.value = 'No se pudieron cargar los instructores: ' + e.message;
  } finally {
    cargando.value = false;
  }
});

const instructoresFiltrados = computed(() => {
  if (!busqueda.value) return instructores.value;
  const q = busqueda.value.toLowerCase();
  return instructores.value.filter(i => 
    i.nombre.toLowerCase().includes(q) || 
    (i.tipo_vinculacion || '').toLowerCase().includes(q)
  );
});

// Reiniciar página al buscar
watch(busqueda, () => {
  paginaActual.value = 1;
});

const totalPaginas = computed(() => Math.ceil(instructoresFiltrados.value.length / elementosPorPagina));

const instructoresPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * elementosPorPagina;
  const fin = inicio + elementosPorPagina;
  return instructoresFiltrados.value.slice(inicio, fin);
});

const verCalendario = (instructor) => {
  router.push(`/programador-academico/instructores/${instructor.id}`);
};
</script>

<style scoped>
.admin-view-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
}

.dash-header {
  display: flex;
  margin-bottom: 20px;
}

.environment-badge h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.environment-badge h1 svg { color: var(--sena-verde); }
.header-meta { margin: 0; color: var(--texto-secundario); font-size: 0.9rem; }

.module-card {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--borde);
}

.estado-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: var(--texto-secundario);
}
.estado-icono { font-size: 2rem; color: var(--sena-verde); }
.estado-error .estado-icono { color: #e67e22; }

.filtros-bar {
  display: flex;
  margin-bottom: 1rem;
}
.search-box {
  position: relative;
  width: 100%;
  max-width: 400px;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
}
.search-input {
  width: 100%;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.6rem 1rem 0.6rem 2.2rem;
  color: var(--texto-principal);
}

.mt-3 { margin-top: 1.5rem; }

.tabla-scroll { overflow-x: auto; }
.tabla-fichas {
  width: 100%;
  border-collapse: collapse;
}
.tabla-fichas th {
  text-align: left;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-secundario);
  padding: 0.8rem;
  border-bottom: 2px solid var(--borde);
}
.tabla-fichas td {
  padding: 0.8rem;
  border-bottom: 1px solid var(--fondo-app);
  font-size: 0.85rem;
}
.text-center { text-align: center; }

.fila-ficha { cursor: pointer; transition: background 0.15s; }
.fila-ficha:hover { background: rgba(57, 169, 0, 0.05); }

.instructor-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.punto-color {
  width: 12px; height: 12px; border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.2);
}

.badge-vinculacion {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 800;
}
.badge-planta { background: var(--sena-verde); color: white; }
.badge-contratista { background: var(--sena-verde-oscuro); color: white; }

.btn-tabla {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  width: 32px; height: 32px;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.btn-tabla:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

/* Paginación */
.paginacion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--borde);
}
.btn-paginacion {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
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
  color: var(--texto-secundario);
}
</style>
