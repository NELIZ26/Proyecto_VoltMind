<template>
  <div class="admin-view-shell">
    <!-- Header principal -->
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>DIRECTORIO DE INSTRUCTORES</h1>
          <p class="header-meta">
            Gestión de personal y carga académica <span class="time-divider">|</span> <strong>03:15:50 PM</strong>
          </p>
        </div>
      </div>
      <div class="header-right">
        <div class="user-info">
          <div class="user-details">
            <h3 class="user-name">Nelson Contreras</h3>
            <span class="user-status">En línea</span>
          </div>
          <div class="user-avatar-container">
            <UserAvatar class="header-avatar" />
          </div>
        </div>
      </div>
    </header>

    <!-- Barra de búsqueda y filtros -->
    <div class="filters-bar">
      <div class="filters-right">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input type="text" class="form-input search-input" placeholder="Buscar por Competencias" />
        </div>
        <div class="select-box">
          <select class="form-select">
            <option>Todos los Roles</option>
            <option>Planta</option>
            <option>Contratista</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Grid de Instructores -->
    <main class="dash-grid instructors-grid">
      <div v-for="(instructor, i) in store.instructores" :key="instructor.id" class="module-card instructor-card" :style="{ animationDelay: `${i * 50}ms` }">
        <div class="card-header">
          <div class="instructor-header-left">
            <UserAvatar class="instructor-avatar-ring" :alt="instructor.name" />
            <div class="instructor-info">
              <h3 class="instructor-name">{{ instructor.name }}</h3>
              <p class="instructor-specialty">{{ instructor.specialty }}</p>
            </div>
          </div>
          <div class="instructor-badge">
             <span :class="['status-badge', instructor.type === 'Planta' ? 'badge-planta' : 'badge-contratista']">
               {{ instructor.type.toUpperCase() }}
             </span>
          </div>
        </div>
        
        <div class="card-body">
          <div class="stats-row">
            <div class="hours-col">
              <div class="hours-header">
                <span class="hours-label">Carga Mensual <span class="hours-status">({{ instructor.statusLabel }})</span></span>
                <span class="time-cell">{{ instructor.hours }}h / {{ instructor.maxHours }}h</span>
              </div>
              <div class="progress-track">
                <div 
                  class="progress-fill" 
                  :style="{ width: Math.min((instructor.hours / instructor.maxHours) * 100, 100) + '%', backgroundColor: instructor.progressColor }"
                ></div>
              </div>
            </div>
            <div class="mini-stat-card">
              <span class="mini-stat-title">Fichas</span>
              <span class="mini-stat-value">{{ instructor.fichas }}</span>
            </div>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="actions-row">
            <div class="info-box-green">
              <div class="info-icon">
                <font-awesome-icon icon="fa-solid fa-clock" />
              </div>
              <div class="info-texts">
                <span class="info-title">Horas Disponible</span>
                <span class="info-value">{{ instructor.available }}</span>
              </div>
            </div>
            <button class="btn-action-gray" @click="openViewModal(instructor)">
              <font-awesome-icon icon="fa-solid fa-calendar-days" />
              <span>Ver Horario</span>
            </button>
            <button class="btn-action-green" @click="openAssignModal(instructor)">
              <font-awesome-icon icon="fa-solid fa-user-plus" />
              <span>Asignar Horas</span>
            </button>
          </div>
          <div class="show-more">
            <a href="#" @click.prevent="openDetailModal(instructor)">Mostrar más</a>
          </div>
        </div>
      </div>
    </main>

    <!-- Paginación -->
    <div class="pagination-bar">
      <div class="pagination-info">
        Mostrando 1 a 6 de 150 Aprendices
      </div>
      <div class="pagination-controls">
        <button class="page-btn"><font-awesome-icon icon="fa-solid fa-chevron-left" /></button>
        <button class="page-btn active">1</button>
        <button class="page-btn">2</button>
        <button class="page-btn">3</button>
        <span class="page-dots">...</span>
        <button class="page-btn">27</button>
        <button class="page-btn"><font-awesome-icon icon="fa-solid fa-chevron-right" /></button>
      </div>
      <div class="pagination-select">
        <span>Mostrar</span>
        <select class="form-select-sm">
          <option>15</option>
          <option>30</option>
          <option>50</option>
        </select>
      </div>
    </div>

    <ModalFormInstructor 
      :show="showAssignModal"
      :instructorData="selectedInstructor"
      @update:show="showAssignModal = $event"
      @close="showAssignModal = false"
      @save="handleAssignSchedule"
    />

    <ModalViewInstructorSchedule 
      :show="showViewModal"
      :instructorData="selectedInstructor"
      @update:show="showViewModal = $event"
      @close="showViewModal = false"
    />

    <ModalInstructorDetail
      :show="showDetailModal"
      :instructorData="selectedDetailInstructor"
      @update:show="showDetailModal = $event"
      @close="showDetailModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ModalFormInstructor from '@/components/admin/modals/ModalFormInstructor.vue';
import ModalViewInstructorSchedule from '@/components/admin/modals/ModalViewInstructorSchedule.vue';
import ModalInstructorDetail from '@/components/admin/modals/ModalInstructorDetail.vue';
import UserAvatar from '@/components/UserAvatar.vue';
import { useProgramacionStore } from '@/stores/programacion';

import Swal from 'sweetalert2';

const router = useRouter();
const store = useProgramacionStore();

onMounted(() => {
  store.initStore();
});

const showAssignModal = ref(false);
const showViewModal = ref(false);
const showDetailModal = ref(false);
const selectedInstructor = ref(null);
const selectedDetailInstructor = ref(null);

const getInitials = (name) => {
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const openAssignModal = (instructor) => {
  selectedInstructor.value = instructor;
  showAssignModal.value = true;
};

const openViewModal = (instructor) => {
  selectedInstructor.value = instructor;
  showViewModal.value = true;
};

const openDetailModal = (instructor) => {
  selectedDetailInstructor.value = instructor;
  showDetailModal.value = true;
};

const handleAssignSchedule = (data) => {
  if (selectedInstructor.value) {
    const result = store.assignSchedule({
      instructorId: selectedInstructor.value.id,
      ambienteId: data.ambiente,
      bloque: data.bloque,
      ficha: data.ficha
    });

    if (result && !result.success) {
      Swal.fire({
        icon: 'error',
        title: 'Conflicto de Horario',
        text: result.error,
        confirmButtonColor: '#EF4444' // Match Sena red / boundary color
      });
    } else {
      Swal.fire({
        icon: 'success',
        title: 'Horario Asignado',
        text: 'La carga horaria ha sido asignada con éxito al instructor.',
        confirmButtonColor: '#39a900',
        timer: 2000,
        showConfirmButton: false
      });
    }
  }
};
</script>

<style scoped>
/* ==========================================================================
   ESTILOS BASADOS EN EL MOCKUP
   ========================================================================== */
.admin-view-shell {
  font-family: var(--fuente-principal, 'Inter', sans-serif);
  min-height: 100vh;
  color: var(--texto-principal);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: transparent;
}

.dash-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--sombra-suave, rgba(0,0,0,0.05));
}

.header-left {
  display: flex;
  flex-direction: column;
}

.environment-badge h1 {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0;
  letter-spacing: -0.5px;
}

.header-meta {
  margin-top: 6px;
  font-size: 0.9rem;
  color: var(--texto-secundario);
}

.time-divider {
  margin: 0 8px;
  color: var(--borde);
}

.header-meta strong {
  color: var(--texto-principal);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  text-align: right;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--texto-principal);
  margin: 0;
}

.user-status {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sena-verde);
}

.user-avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-avatar {
  transform: scale(0.85); /* Aumentado tamaño */
  transform-origin: right center;
  margin-right: -5px;
}

/* Filtros */
.filters-bar {
  background: var(--fondo-tarjetas);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--sombra-suave, rgba(0,0,0,0.05));
  display: flex;
  justify-content: flex-end;
}

.filters-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.6rem 1rem 0.6rem 2.2rem;
  width: 100%;
  font-size: 0.9rem;
  color: var(--texto-principal);
  outline: none;
}

.form-input:focus {
  border-color: var(--sena-verde);
}

.select-box {
  width: 180px;
}

.form-select {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.6rem 1rem;
  width: 100%;
  font-size: 0.9rem;
  color: var(--texto-principal);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem top 50%;
  background-size: 0.65rem auto;
}

/* Grid de cards */
.instructors-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.instructor-card {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px var(--sombra-suave, rgba(0,0,0,0.05));
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.instructor-header-left {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.instructor-avatar-ring {
  transform: scale(0.9); /* Aumentado el avatar */
  transform-origin: center left;
  margin-right: -5px;
}

.instructor-info {
  display: flex;
  flex-direction: column;
}

.instructor-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0 0 4px 0;
}

.instructor-specialty {
  font-size: 0.9rem;
  color: var(--texto-secundario);
  margin: 0;
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

.stats-row {
  display: flex;
  gap: 1rem;
  align-items: stretch;
  margin-bottom: 1.5rem;
}

.hours-col {
  flex: 1;
  background: var(--fondo-app);
  padding: 0.8rem 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hours-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  align-items: baseline;
}

.hours-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--texto-principal);
}

.hours-status {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--texto-secundario);
  margin-left: 4px;
}

.time-cell {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
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

.mini-stat-card {
  background-color: var(--sena-gris-claro);
  border-radius: 8px;
  overflow: hidden;
  border-top: 6px solid var(--sena-verde-oscuro);
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  padding: 0.6rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.1rem;
  min-width: 80px;
}

.mini-stat-title {
  color: var(--sena-azul-oscuro);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.mini-stat-value {
  color: var(--sena-azul-oscuro);
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
  margin-top: 2px;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.actions-row {
  display: flex;
  gap: 10px;
  height: 45%;
}

.info-box-green {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 1rem;
  border: 1.5px solid var(--sena-verde);
  border-radius: 6px;
  border-left-width: 4px;
  flex: 1;
}

.info-icon {
  color: var(--sena-verde);
  font-size: 1.1rem;
}

.info-texts {
  display: flex;
  flex-direction: column;
}

.info-title {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.info-value {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--sena-verde);
}

.btn-action-gray, .btn-action-green {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
  flex: 1;
}

.btn-action-gray {
  background: var(--fondo-app);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
}

.btn-action-gray:hover {
  background: var(--borde);
}

.btn-action-green {
  background: var(--sena-verde);
  color: white;
}

.btn-action-green:hover {
  background: var(--sena-verde-oscuro);
}

.show-more {
  text-align: center;
  margin-top: 4px;
}

.show-more a {
  color: var(--texto-principal);
  font-size: 0.9rem;
  font-weight: 700;
  text-decoration: none;
}

.show-more a:hover {
  text-decoration: underline;
}

/* Paginación */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--sombra-suave, rgba(0,0,0,0.05));
  margin-top: auto;
}

.pagination-info {
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-btn {
  background: var(--fondo-app);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: var(--texto-principal);
  cursor: pointer;
  font-weight: 600;
}

.page-btn.active {
  background: var(--sena-verde);
  color: white;
}

.page-btn:hover:not(.active) {
  background: var(--borde);
}

.page-dots {
  color: var(--texto-secundario);
  font-weight: 600;
}

.pagination-select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.form-select-sm {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 4px;
  padding: 0.4rem 1.5rem 0.4rem 0.8rem;
  font-size: 0.85rem;
  color: var(--texto-principal);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%236B7280%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem top 50%;
  background-size: 0.65rem auto;
}
</style>
