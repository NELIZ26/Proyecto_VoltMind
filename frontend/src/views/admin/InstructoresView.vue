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
      <!-- Botón Crear Instructor -->
<button class="btn-crear-instructor" @click="showCreateModal = true">
  <font-awesome-icon icon="fa-solid fa-plus" />
  <span>Crear Instructor</span>
</button>

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

    <!-- Modales de Asignación y Detalle (Antiguos) -->
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
      @delete="handleDeleteInstructor"
    />

    <!-- Modal para CREAR PERFIL (Llama al archivo Modalcrearinstructor.vue) -->
    <Modalcrearinstructor 
      :isOpen="showCreateModal" 
      @close="showCreateModal = false" 
      @created="handleCreated" 
      
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ModalFormInstructor from '@/components/admin/modals/ModalFormInstructor.vue';
import Modalcrearinstructor from '@/components/admin/modals/Modalcrearinstructor.vue';
import ModalViewInstructorSchedule from '@/components/admin/modals/ModalViewInstructorSchedule.vue';
import ModalInstructorDetail from '@/components/admin/modals/ModalInstructorDetail.vue';
import UserAvatar from '@/components/UserAvatar.vue';
import { useProgramacionStore } from '@/stores/programacion';
import { apiService } from '@/services/apiService' 

import Swal from 'sweetalert2';

const router = useRouter();
const store = useProgramacionStore();

onMounted(() => {
  store.initStore();
});

const showAssignModal = ref(false);
const showViewModal = ref(false);
const showDetailModal = ref(false);
const showCreateModal = ref(false);

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

const handleCreated = async (nuevoInstructorData) => {
  try {
    // Petición directa al backend FastAPI
    const response = await fetch('http://127.0.0.1:8000/api/instructores', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(nuevoInstructorData),
    });

    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.statusText}`);
    }

    const respuesta = await response.json();
    const guidDataverse = respuesta?.id || respuesta?.data?.cr6a3_instructorid;
    const maxHoras = Number(nuevoInstructorData.max_horas_mensuales) || 160;

    const instructorParaInsertar = {
      cr6a3_instructorid: guidDataverse,
      id: guidDataverse || Date.now(),
      name: nuevoInstructorData.nombre,
      nombre: nuevoInstructorData.nombre,
      documento: nuevoInstructorData.documento,
      correo: nuevoInstructorData.correo,
      telefono: nuevoInstructorData.telefono,
      specialty: nuevoInstructorData.area_especialidad || 'General',
      type: nuevoInstructorData.tipo_vinculacion === 'PLANTA' ? 'Planta' : 'Contratista',
      maxHours: maxHoras,
      horasMaximas: maxHoras,
      assignedHours: 0,
      availableHours: maxHoras
    };

    if (store.instructores) {
      store.instructores = [instructorParaInsertar, ...store.instructores];
    }

    showCreateModal.value = false;

    Swal.fire({
      icon: 'success',
      title: 'Instructor Registrado',
      text: 'Guardado correctamente en Dataverse.',
      confirmButtonColor: '#39a900',
      timer: 2000,
      showConfirmButton: false
    });

  } catch (error) {
    console.error('Error al guardar en Dataverse:', error);
    Swal.fire({
      icon: 'error',
      title: 'Error al registrar',
      text: 'No se pudo guardar el instructor en la base de datos.',
      confirmButtonColor: '#EF4444'
    });
    if (store.instructores) {
  store.instructores = [instructorParaInsertar, ...store.instructores];
  // Guardar inmediatamente en localStorage para mantener coherencia local
  if (typeof store.saveToLocalStorage === 'function') {
    store.saveToLocalStorage();
  }
}
  }
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
        confirmButtonColor: '#EF4444'
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
  // En InstructoresView.vue

const handleDeleteInstructor = async (instructorOrId) => {
  // Extrae el GUID de Dataverse de las posibles propiedades del objeto
  const idParaBorrar = typeof instructorOrId === 'object' 
    ? (instructorOrId.cr6a3_instructorid || instructorOrId.id) 
    : instructorOrId;

  if (!idParaBorrar) {
    console.error('No se recibió ID válido del instructor');
    return;
  }

  try {
    // 1. Eliminamos el instructor en el backend enviando el GUID de Dataverse
    await apiService.deleteInstructor(idParaBorrar);

    // 2. Volvemos a inicializar/recargar la lista en la store de Pinia
    await store.initStore();

    // 3. Cerramos el modal
    showDetailModal.value = false;

    Swal.fire({
      icon: 'success',
      title: 'Instructor Eliminado',
      text: 'El registro se borró correctamente de Dataverse.',
      confirmButtonColor: '#39a900',
      timer: 2000,
      showConfirmButton: false
    });

  } catch (error) {
    console.error('Error al borrar instructor:', error.message);
  }
};
</script>

<style scoped>
/* Estilos sin modificaciones */
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
  transform: scale(0.85);
  transform-origin: right center;
  margin-right: -5px;
}

.filters-bar {
  background: var(--fondo-tarjetas);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--sombra-suave, rgba(0,0,0,0.05));
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}
/* Botón Crear Instructor */
.btn-crear-instructor {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--sena-verde, #39a900);
  color: var(--sena-blanco, #ffffff);
  font-family: var(--fuente-principal, sans-serif);
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(57, 169, 0, 0.2);
}

.btn-crear-instructor:hover {
  background-color: var(--sena-verde-oscuro, #007832);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 120, 50, 0.3);
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
  transform: scale(0.9);
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

/* ==========================================================================
   ESTILOS ADAPTABLES A TEMA (LIGHT / DARK) PARA EL FORMULARIO MODAL
   ========================================================================== */

/* Fondo oscuro / Overlay general */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

/* Contenedor del Modal (Cambia según el tema) */
.modal-container {
  background-color: var(--fondo-tarjetas);
  color: var(--texto-principal);
  border: 1px solid var(--borde);
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Cabecera y Pie */
.modal-header,
.modal-footer {
  padding: 16px 24px;
  border-color: var(--borde);
  display: flex;
  align-items: center;
}

.modal-header {
  justify-content: space-between;
  border-bottom: 1px solid var(--borde);
}

.modal-footer {
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid var(--borde);
}

.modal-header h3 {
  color: var(--texto-principal);
  font-weight: 700;
  font-size: 1.2rem;
}

/* Botón X de Cierre */
.btn-close-modal {
  background: transparent;
  border: none;
  color: var(--texto-secundario);
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.btn-close-modal:hover {
  color: var(--texto-principal);
}

/* Inputs, Selects y Labels */
.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--texto-principal);
  margin-bottom: 6px;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 14px;
  font-family: var(--fuente-principal);
  font-size: 0.95rem;
  color: var(--texto-principal);
  background-color: var(--fondo-app); /* En oscuro toma #121212 / #484949 */
  border: 1px solid var(--borde);
  border-radius: 6px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 3px rgba(57, 169, 0, 0.2);
}

/* Botones de Acción dentro del Modal */
.btn-cancelar {
  background-color: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 10px 18px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-cancelar:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.btn-guardar {
  background-color: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-guardar:hover {
  background-color: var(--sena-verde-oscuro);
}

/* ==========================================================================
   ESTILOS DINÁMICOS DEL MODAL (SIN AFECTAR LA VISTA PRINCIPAL)
   ========================================================================== */

/* 1. Fondo semitransparente del overlay */
:deep(.modal-overlay) {
  background-color: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(4px);
}

/* 2. Tarjeta del modal (cambia entre blanco y oscuro automáticamente) */
:deep(.modal-container),
:deep(.modal-content) {
  background-color: var(--fondo-tarjetas) !important;
  color: var(--texto-principal) !important;
  border: 1px solid var(--borde) !important;
}

/* 3. Títulos y etiquetas (Labels) dentro del modal */
:deep(.modal-container h3),
:deep(.modal-container label),
:deep(.modal-content h3),
:deep(.modal-content label) {
  color: var(--texto-principal) !important;
}

/* 4. CASILLAS DEL MODAL EN TEMA CLARO */
html:not([data-theme="dark"]) :deep(.modal-container input),
html:not([data-theme="dark"]) :deep(.modal-container select),
html:not([data-theme="dark"]) :deep(.modal-content input),
html:not([data-theme="dark"]) :deep(.modal-content select) {
  background-color: #ffffff !important;
  color: #003040 !important;
  border: 1px solid #d1d5db !important;
}

/* 5. CASILLAS DEL MODAL EN TEMA OSCURO */
html[data-theme="dark"] :deep(.modal-container input),
html[data-theme="dark"] :deep(.modal-container select),
html[data-theme="dark"] :deep(.modal-content input),
html[data-theme="dark"] :deep(.modal-content select) {
  background-color: #2b2b2b !important;
  color: #ffffff !important;
  border: 1px solid #444444 !important;
}

/* 6. Botones del modal */
:deep(.modal-container .btn-guardar),
:deep(.modal-content .btn-guardar),
:deep(.modal-container button[type="submit"]) {
  background-color: var(--sena-verde, #39a900) !important;
  color: #ffffff !important;
}

:deep(.modal-container .btn-cancelar),
:deep(.modal-content .btn-cancelar) {
  background-color: #e5e7eb !important;
  color: #1f2937 !important;
}

html[data-theme="dark"] :deep(.modal-container .btn-cancelar),
html[data-theme="dark"] :deep(.modal-content .btn-cancelar) {
  background-color: #374151 !important;
  color: #ffffff !important;
}
/* ==========================================================================
   RECONSTRUCCIÓN DE LA BARRA DE BÚSQUEDA (LUPA Y POSICIONAMIENTO)
   ========================================================================== */

.filters-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative !important;
  display: flex !important;
  align-items: center !important;
}

.search-box .search-icon {
  position: absolute !important;
  left: 12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  color: var(--texto-secundario, #9ca3af) !important;
  pointer-events: none !important;
  z-index: 5 !important;
}

.search-box .search-input {
  padding-left: 38px !important; /* Desplaza el texto para que la lupa no quede encima */
  height: 40px;
}
:deep(.stat-card),
:deep(.info-card),
:deep(.detail-card),
:deep(.stat-box) {
  background-color: var(--fondo-tarjetas) !important;
  color: var(--texto-principal) !important;
  border: 1px solid var(--borde) !important;
}

:deep(.modal-content),
:deep(.modal-container) {
  background-color: var(--fondo-tarjetas) !important;
  color: var(--texto-principal) !important;
}
/* Corrección de la barra de pestañas en tema oscuro */
:deep(.tabs-header),
:deep(.tab-nav),
:deep(.modal-tabs),
:deep(.tabs-container) {
  background-color: var(--fondo-tarjetas, #1e1e1e) !important;
  border-bottom: 1px solid var(--borde, #333333) !important;
}

/* Corrección de las tarjetas laterales de conexión en tema oscuro */
:deep(.connection-card),
:deep(.mini-card),
:deep(.info-tile),
:deep(.modal-body div[class*="-card"]) {
  background-color: var(--fondo-tarjetas, #1e1e1e) !important;
  color: var(--texto-principal, #ffffff) !important;
  border: 1px solid var(--borde, #333333) !important;
}

/* Textos dentro de esas minitarjetas */
:deep(.connection-card *),
:deep(.mini-card *) {
  color: var(--texto-principal, #ffffff) !important;
}
/* Corrección directa de la barra blanca de navegación/pestañas */
:deep(.modal-content nav),
:deep(.modal-content ul),
:deep(.modal-content [class*="tab"]),
:deep(.modal-content [class*="nav"]),
:deep(.modal-container nav),
:deep(.modal-container ul),
:deep(.modal-container [class*="tab"]),
:deep(.modal-container [class*="nav"]) {
  background-color: var(--fondo-tarjetas) !important;
  border-color: var(--borde) !important;
}

/* Color del texto e indicadores de la pestaña */
:deep([class*="tab"] button),
:deep([class*="tab"] a),
:deep([class*="nav"] button),
:deep([class*="nav"] a) {
  color: var(--texto-principal) !important;
}

</style>