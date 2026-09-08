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

    <main class="module-card">
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
      
      <div class="instructors-table-container">
        <table class="sena-table">
          <thead>
            <tr>
              <th>INSTRUCTOR</th>
              <th>PERFIL PROFESIONAL</th>
              <th>VINCULACIÓN</th>
              <th>CARGA MENSUAL</th>
              <th>DISPONIBLE</th>
              <th>ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="instructor in instructoresPaginados" :key="instructor.id">
              <td>
                <div class="table-instructor-info">
                  <UserAvatar class="instructor-avatar-ring small" :alt="instructor.name" />
                  <div class="texts">
                    <span class="instructor-name-table">{{ instructor.name }}</span>
                    <span class="instructor-doc-table">Doc: {{ instructor.document || 'No registrado' }}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="instructor-specialty-table">{{ instructor.specialty }}</span>
              </td>
              <td>
                <span :class="['status-badge', instructor.type === 'Planta' ? 'badge-planta' : 'badge-contratista']" style="display: inline-block; width: fit-content;">
                  {{ instructor.type ? instructor.type.toUpperCase() : '' }}
                </span>
              </td>
              <td>
                <div class="hours-header" style="justify-content: flex-start; gap: 10px;">
                  <span class="time-cell">{{ instructor.hours }}h / {{ instructor.maxHours }}h</span>
                  <span class="hours-status" :style="{ color: instructor.progressColor }">({{ instructor.statusLabel }})</span>
                </div>
                <div class="progress-track" style="margin-top: 5px; max-width: 200px;">
                  <div class="progress-fill" :style="{ width: Math.min(((instructor.hours || 0) / (instructor.maxHours || 1)) * 100, 100) + '%', backgroundColor: instructor.progressColor }"></div>
                </div>
              </td>
              <td>
                <span class="hours-badge">
                  <font-awesome-icon icon="fa-solid fa-clock" />
                  {{ instructor.available }}
                </span>
              </td>
              <td>
                <div class="table-actions-group">
                  <button class="btn-icon" title="Ver Horario" @click="verCalendario(instructor)">
                    <font-awesome-icon icon="fa-solid fa-calendar-days" />
                  </button>
                  <button class="btn-icon" title="Mostrar más" @click="openDetailModal(instructor)">
                    <font-awesome-icon icon="fa-solid fa-eye" />
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
      
      <ModalInstructorDetail
        :show="showDetailModal"
        :readonly="true"
        :instructorData="selectedDetailInstructor"
        @update:show="showDetailModal = $event"
        @close="showDetailModal = false"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useProgramacionStore } from '@/stores/programacion';
import UserAvatar from '@/components/UserAvatar.vue';
import ModalInstructorDetail from '@/components/admin/modals/ModalInstructorDetail.vue';

const router = useRouter();
const store = useProgramacionStore();

const busqueda = ref('');

// Paginación
const paginaActual = ref(1);
const elementosPorPagina = 10;

onMounted(() => {
  store.initStore();
});

const instructoresFiltrados = computed(() => {
  if (!busqueda.value) return store.instructores;
  const q = busqueda.value.toLowerCase();
  return store.instructores.filter(i => 
    (i.name || '').toLowerCase().includes(q) || 
    (i.type || '').toLowerCase().includes(q)
  );
});

// Reiniciar página al buscar
watch(busqueda, () => {
  paginaActual.value = 1;
});

const totalPaginas = computed(() => Math.ceil(instructoresFiltrados.value.length / elementosPorPagina) || 1);

const instructoresPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * elementosPorPagina;
  const fin = inicio + elementosPorPagina;
  return instructoresFiltrados.value.slice(inicio, fin);
});

const verCalendario = (instructor) => {
  router.push(`/programador-academico/instructores/${instructor.id}`);
};

const showDetailModal = ref(false);
const selectedDetailInstructor = ref(null);

const openDetailModal = (instructor) => {
  selectedDetailInstructor.value = instructor;
  showDetailModal.value = true;
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

/* Estilos de Tabla e Indicadores */
.instructors-table-container {
  margin-top: 1.5rem;
  overflow-x: auto;
}

.sena-table {
  width: 100%;
  border-collapse: collapse;
  background-color: transparent;
  font-size: 0.9rem;
}

.sena-table th {
  background-color: var(--fondo-app, #f8fafc);
  color: var(--texto-secundario, #64748b);
  font-weight: 700;
  text-transform: uppercase;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid var(--borde, #e2e8f0);
  font-size: 0.8rem;
}

.sena-table td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--borde, #e2e8f0);
  vertical-align: middle;
}

.table-instructor-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.instructor-avatar-ring.small {
  width: 40px;
  height: 40px;
  transform: scale(0.8);
}

.table-instructor-info .texts {
  display: flex;
  flex-direction: column;
}

.instructor-name-table {
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
}

.instructor-doc-table {
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
}

.instructor-specialty-table {
  font-weight: 600;
  color: var(--texto-principal, #0f172a);
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.badge-planta {
  background: var(--sena-verde);
  color: white;
}

.badge-contratista {
  background: var(--sena-verde-oscuro);
  color: white;
}

.hours-header {
  display: flex;
  align-items: baseline;
}

.time-cell {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.hours-status {
  font-size: 0.8rem;
  font-weight: 500;
}

.progress-track {
  height: 6px;
  background: var(--borde);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.hours-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
}

.table-actions-group {
  display: flex;
  gap: 0.5rem;
}

.table-actions-group .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid var(--borde, #e2e8f0);
  background: transparent;
  color: var(--texto-secundario, #64748b);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.table-actions-group .btn-icon:hover {
  border-color: var(--sena-verde, #39A900);
  color: var(--sena-verde, #39A900);
}

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
