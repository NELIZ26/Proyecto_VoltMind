<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content detail-modal">
      
      <!-- HEADER -->
      <header class="modal-header">
        <div class="header-left">
          <UserAvatar :alt="instructorData?.name" />
          <div class="info-texts">
            <h3>{{ instructorData?.name }}</h3>
            <p>{{ instructorData?.specialty }} | {{ instructorData?.type }}</p>
          </div>
        </div>
        <div class="header-right">
          <p class="desc-text">
            Consulte y genere informes del aula por día, semana o mes, así como reportes semanales de aprendices con ausencias, registros y horas de ingreso.
          </p>
        </div>
        <button class="btn-close" @click="closeModal">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </header>

      <!-- STAT CARDS -->
      <div class="stats-cards-container">
        <div class="stat-card">
          <span class="stat-label">Horas Asignadas</span>
          <span class="stat-value">{{ instructorData?.hours }} h</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Máximo Horas</span>
          <span class="stat-value">{{ instructorData?.maxHours }} h</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Horas Disponibles</span>
          <span class="stat-value">{{ getAvailableHours }} h</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Fichas Asg.</span>
          <span class="stat-value">{{ instructorData?.fichas }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Estado</span>
          <span class="stat-value status-text" :style="{ color: instructorData?.progressColor || '#10B981' }">
            {{ instructorData?.statusLabel }}
          </span>
        </div>
      </div>

      <!-- TABS SELECTOR -->
      <div class="tabs-nav">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- TAB CONTENT -->
      <div class="tab-content-container">
        
        <!-- RESUMEN TAB -->
        <div v-if="activeTab === 'resumen'" class="tab-pane resumen-grid">
          <div class="info-card">
            <h4>INFORMACIÓN GENERAL</h4>
            <div class="info-row">
              <span class="info-label">Documento</span>
              <span class="info-value">{{ getInstructorDoc }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Correo</span>
              <span class="info-value">{{ getInstructorEmail }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Teléfono</span>
              <span class="info-value">{{ getInstructorPhone }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Jornada</span>
              <span class="info-value">Mañana</span>
            </div>
            <div class="info-row">
              <span class="info-label">Competencia</span>
              <span class="info-value">Técnica</span>
            </div>
          </div>

          <div class="connections-row">
            <div class="connection-card">
              <div class="conn-icon-label">
                <font-awesome-icon icon="fa-solid fa-clock" class="icon-green" />
                <div class="conn-texts">
                  <span class="conn-title">Ultima conexión</span>
                  <span class="conn-value-main">Hoy, 10:45 a.m.</span>
                </div>
              </div>
              <span class="conn-date">17/06/2026</span>
            </div>

            <div class="connection-card">
              <div class="conn-icon-label">
                <font-awesome-icon icon="fa-solid fa-clock" class="icon-green" />
                <div class="conn-texts">
                  <span class="conn-title">Tiempo Conn.</span>
                  <span class="conn-value-main">28h 45 min</span>
                </div>
              </div>
              <span class="conn-date">En los últimos días</span>
            </div>
          </div>
        </div>

        <!-- HORARIOS TAB -->
        <div v-if="activeTab === 'horarios'" class="tab-pane">
          <div class="schedule-grid" v-if="instructorSchedule.length > 0">
            <div class="schedule-card" v-for="item in instructorSchedule" :key="item.id">
              <div class="card-top-banner">
                <span class="env-name">AMBIENTE {{ getAmbienteName(item.ambienteId).toUpperCase() }}</span>
                <span class="time-range">{{ formatTimeRange(item.bloque) }}</span>
              </div>
              <div class="card-main-content">
                <h5>{{ getProgramName(item.ficha) }} ({{ item.ficha }})</h5>
                <p>{{ instructorData?.specialty }} | Transversal</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <font-awesome-icon icon="fa-regular fa-calendar" class="empty-icon" />
            <p>No hay bloques horarios asignados para este instructor.</p>
          </div>
        </div>

        <!-- ASIGNACIONES TAB -->
        <div v-if="activeTab === 'asignaciones'" class="tab-pane">
          <div class="assignments-grid" v-if="instructorSchedule.length > 0">
            <div class="assignment-card" v-for="item in instructorSchedule" :key="item.id">
              <h5>{{ getProgramName(item.ficha) }} | Mañana</h5>
              <p class="subtitle">{{ instructorData?.specialty }} | Transversal</p>
              <div class="detail-line">
                <span class="label">Competencia:</span>
                <span class="val">240201530</span>
              </div>
              <div class="detail-line font-bold">
                <span class="label">Horas:</span>
                <span class="val text-green">40h</span>
              </div>
              <div class="detail-line">
                <span class="label">Fecha Inicio:</span>
                <span class="val">08/05/2026</span>
              </div>
              <div class="detail-line">
                <span class="label">Fecha Fin:</span>
                <span class="val">08/08/2026</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <font-awesome-icon icon="fa-solid fa-list-check" class="empty-icon" />
            <p>No hay asignaciones registradas para este instructor.</p>
          </div>
        </div>

        <!-- NOVEDADES TAB -->
        <div v-if="activeTab === 'novedades'" class="tab-pane">
          <div class="empty-state">
            <font-awesome-icon icon="fa-solid fa-bell-slash" class="empty-icon" />
            <p>No se registran novedades para este instructor.</p>
          </div>
        </div>

      </div>

      <!-- FOOTER -->
      <footer class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cerrar</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue';
import { useProgramacionStore } from '@/stores/programacion';
import UserAvatar from '@/components/UserAvatar.vue';

const props = defineProps({
  show: Boolean,
  instructorData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close']);

const store = useProgramacionStore();

const activeTab = ref('resumen');

const tabs = [
  { id: 'resumen', label: 'Resumen' },
  { id: 'horarios', label: 'Horarios' },
  { id: 'asignaciones', label: 'Asignaciones' },
  { id: 'novedades', label: 'Novedades' }
];

watch(() => props.show, (newVal) => {
  if (newVal) {
    activeTab.value = 'resumen';
  }
});

const getInitials = (name) => {
  if (!name) return '';
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const getAvailableHours = computed(() => {
  if (!props.instructorData) return 0;
  return props.instructorData.maxHours - props.instructorData.hours;
});

// Dynamic values helper to look realistic
const getInstructorDoc = computed(() => {
  if (!props.instructorData) return '';
  // Deterministic mock document based on ID
  return (1002345000 + props.instructorData.id * 8329).toString();
});

const getInstructorEmail = computed(() => {
  if (!props.instructorData) return '';
  const first = props.instructorData.name.split(' ')[0].toLowerCase();
  return `${first}@sena.edu.co`;
});

const getInstructorPhone = computed(() => {
  if (!props.instructorData) return '';
  return `312 345 67 ${80 + props.instructorData.id}`;
});

const instructorSchedule = computed(() => {
  if (!props.instructorData) return [];
  return store.schedule.filter(s => s.instructorId === props.instructorData.id);
});

const getAmbienteName = (ambienteId) => {
  const amb = store.ambientes.find(a => a.id === ambienteId);
  return amb ? amb.name : 'Ambiente 102';
};

const getProgramName = (ficha) => {
  if (ficha === '2693821') return 'Técnico Sistemas';
  if (ficha === '2693822') return 'Multimedia';
  if (ficha === '2710100') return 'Cocina';
  return 'Análisis y Desarrollo';
};

const formatTimeRange = (bloque) => {
  if (!bloque) return '9:00AM / 11:00AM';
  // Bloque: "06:00 am - 09:00 am" -> convert to "6:00AM / 9:00AM" style
  const clean = bloque.toUpperCase().replace(/\s+/g, '');
  const parts = clean.split('-');
  if (parts.length === 2) {
    return `${parts[0]} / ${parts[1]}`;
  }
  return bloque;
};

const closeModal = () => {
  emit('close');
  emit('update:show', false);
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 48, 64, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  padding: 1rem;
}

.detail-modal {
  background: var(--fondo-tarjetas, #ffffff);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--borde, #cbd5e1);
}

/* HEADER */
.modal-header {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1.5rem;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-bottom: 1px solid var(--borde, #cbd5e1);
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--sena-verde, #39a900);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
}

.info-texts h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
}

.info-texts p {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: var(--texto-secundario, #64748b);
}

.header-right {
  display: flex;
  align-items: center;
}

.desc-text {
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--texto-secundario, #64748b);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--texto-secundario, #64748b);
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #EF4444;
}

/* STAT CARDS */
.stats-cards-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: var(--fondo-app, #f8fafc);
  border-bottom: 1px solid var(--borde, #cbd5e1);
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  border: 1px solid var(--borde, #cbd5e1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario, #64748b);
  text-align: center;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
}

.status-text {
  font-weight: 800;
}

/* TABS NAV */
.tabs-nav {
  display: flex;
  gap: 1.5rem;
  padding: 0 2rem;
  background: white;
  border-bottom: 1px solid var(--borde, #cbd5e1);
}

.tab-btn {
  background: none;
  border: none;
  padding: 1rem 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--texto-secundario, #64748b);
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.tab-btn:hover {
  color: var(--texto-principal, #0f172a);
}

.tab-btn.active {
  color: var(--sena-verde, #39a900);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--sena-verde, #39a900);
  border-radius: 3px 3px 0 0;
}

/* TAB CONTENT */
.tab-content-container {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
  background: var(--fondo-app, #f8fafc);
  min-height: 250px;
}

.tab-pane {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* RESUMEN TAB */
.resumen-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--borde, #cbd5e1);
}

.info-card h4 {
  margin: 0 0 1.25rem 0;
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--texto-secundario, #64748b);
  letter-spacing: 0.5px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--fondo-app, #f8fafc);
  font-size: 0.9rem;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: var(--texto-secundario, #64748b);
}

.info-value {
  font-weight: 700;
  color: var(--texto-principal, #0f172a);
}

.connections-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.connection-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--borde, #cbd5e1);
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conn-icon-label {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-green {
  font-size: 1.5rem;
  color: var(--sena-verde, #39a900);
}

.conn-texts {
  display: flex;
  flex-direction: column;
}

.conn-title {
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
  font-weight: 600;
}

.conn-value-main {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
  margin-top: 2px;
}

.conn-date {
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
}

/* HORARIOS TAB - GRID */
.schedule-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  max-height: 320px;
  overflow-y: auto;
}

.schedule-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--borde, #cbd5e1);
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.card-top-banner {
  background-color: var(--sena-verde, #39a900);
  color: white;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 800;
}

.card-main-content {
  padding: 1rem;
}

.card-main-content h5 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
}

.card-main-content p {
  margin: 6px 0 0 0;
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
}

/* ASIGNACIONES TAB */
.assignments-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.assignment-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--borde, #cbd5e1);
  padding: 1.25rem;
  border-left: 5px solid var(--sena-verde, #39a900);
}

.assignment-card h5 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--texto-principal, #0f172a);
}

.assignment-card .subtitle {
  margin: 4px 0 10px 0;
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
}

.detail-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  margin-bottom: 4px;
}

.detail-line:last-child {
  margin-bottom: 0;
}

.detail-line .label {
  color: var(--texto-secundario, #64748b);
  font-weight: 600;
}

.detail-line .val {
  color: var(--texto-principal, #0f172a);
  font-weight: 700;
}

.text-green {
  color: var(--sena-verde, #39a900) !important;
}

.font-bold {
  font-weight: 800;
}

/* EMPTY STATE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: var(--texto-secundario, #64748b);
  text-align: center;
}

.empty-icon {
  font-size: 2.5rem;
  color: var(--borde, #cbd5e1);
  margin-bottom: 1rem;
}

/* FOOTER */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1.25rem 2rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-top: 1px solid var(--borde, #cbd5e1);
}

.btn-cancel {
  background: var(--fondo-app, #f8fafc);
  border: 1px solid var(--borde, #cbd5e1);
  color: var(--texto-principal, #0f172a);
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: var(--borde, #cbd5e1);
}
</style>
