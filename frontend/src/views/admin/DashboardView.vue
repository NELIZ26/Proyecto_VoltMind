<template>
  <div class="admin-view-shell">
    <!-- Header Bar (Cabecera) -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="header-title">PANEL DE CONTROL GENERAL</h1>
        <p class="header-subtitle">Sede Principal Puerto Asís | {{ currentTime }}</p>
      </div>
      <div class="header-right" @click="showProfileModal = true">
        <div class="user-info">
          <span class="user-name">Nelson Contreras</span>
          <span class="user-status">En línea</span>
        </div>
        <div class="user-avatar-wrapper">
          <font-awesome-icon :icon="['fas', 'circle-user']" />
        </div>
      </div>
    </div>

    <!-- Main Grid Layout -->
    <div class="dashboard-grid">
      <!-- Columna Izquierda: Gráfica Interactiva (65%) -->
      <section class="left-column">
        <div class="card chart-card">
          <div class="card-header-simple">
            <h3 class="card-title">
              <font-awesome-icon :icon="['fas', 'bolt']" class="icon-margin" />
              CONSUMO GLOBAL
            </h3>
          </div>
          <div class="chart-container">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>
      </section>

      <!-- Columna Derecha: Métricas y Alertas (35%) -->
      <section class="right-column">
        <!-- Métricas Row (dos tarjetas) -->
        <div class="metrics-row">
          <div class="metric-card">
            <div class="icon-box">
              <font-awesome-icon :icon="['fas', 'plug']" />
            </div>
            <div class="metric-text-box">
              <span class="metric-label">Carga Total</span>
              <div class="metric-combined-value">
                <span class="value-number">1450,5</span>
                <span class="value-unit">kW</span>
              </div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="icon-box">
              <font-awesome-icon :icon="['fas', 'house-laptop']" />
            </div>
            <div class="metric-text-box">
              <span class="metric-label">Aulas Activas</span>
              <div class="metric-combined-value">
                <span class="value-number">3/5</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Alertas / Notificaciones Card -->
        <div class="card notifications-card">
          <div class="card-header-simple">
            <h3 class="card-title">
              <font-awesome-icon :icon="['fas', 'bell']" class="icon-margin" />
              NOTIFICACIONES
            </h3>
          </div>
          <div class="notifications-list">
            <div 
              v-for="notif in notifications.filter(n => !n.resolved)" 
              :key="notif.id" 
              class="notification-item"
              :class="{ 'resolving-out': notif.resolving }"
            >
              <div class="notification-left-group">
                <div class="notification-checkbox-wrapper">
                  <button 
                    class="notif-circle-check" 
                    @click="resolveNotification(notif)" 
                    title="Marcar como resuelta"
                  >
                    <font-awesome-icon :icon="['fas', 'check']" class="check-icon" />
                  </button>
                </div>
                <div class="notification-body">
                  <span class="notification-title">{{ notif.title }}</span>
                  <span class="notification-desc">{{ notif.desc }}</span>
                </div>
              </div>
              <span :class="['badge', notif.badgeClass]">{{ notif.badge }}</span>
            </div>
            <div v-if="notifications.filter(n => !n.resolved).length === 0" class="empty-notifications">
              No hay alertas pendientes 🎉
            </div>
          </div>
          <div class="notifications-footer">
            <button class="show-more-btn" @click="showNotificationsModal = true">
              Mostrar más
            </button>
          </div>
        </div>
      </section>

      <!-- Sección Inferior: Tabla de Actividad Reciente (100%) -->
      <section class="bottom-full-column">
        <div class="card table-card">
          <div class="table-header-row">
            <h3 class="card-title">
              <font-awesome-icon :icon="['fas', 'clock-rotate-left']" class="icon-margin" />
              Actividad Reciente en Sede
            </h3>
            <router-link to="/admin/fichas" class="action-link">Ver Fichas</router-link>
          </div>

          <div class="table-responsive">
            <table class="activity-table">
              <thead>
                <tr>
                  <th>FECHA / HORA</th>
                  <th>SEDE / AMBIENTE</th>
                  <th>INSTRUCTOR / EVENTO</th>
                  <th>ESTADO</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="activity in recentActivities.slice(0, 3)" :key="activity.id">
                  <td class="time-cell">{{ activity.timestamp }}</td>
                  <td>
                    <div class="cell-location">
                      <span class="location-main">{{ activity.campus }}</span>
                      <span class="location-sub">{{ activity.room }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="cell-event">
                      <span class="event-user">{{ activity.instructor }}</span>
                      <span class="event-desc">{{ activity.event }}</span>
                    </div>
                  </td>
                  <td>
                    <span :class="['status-badge', activity.statusClass]">
                      {{ activity.statusText }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <button class="show-more-btn" @click="showActivitiesModal = true">
              Mostrar más
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- Modal Components -->
    <ModalAdminProfile 
      :show="showProfileModal" 
      @close="showProfileModal = false" 
    />

    <ModalNotifications 
      :show="showNotificationsModal" 
      :notifications="notifications" 
      @close="showNotificationsModal = false" 
    />

    <ModalActivities 
      :show="showActivitiesModal" 
      :activities="recentActivities" 
      @close="showActivitiesModal = false" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { useToast } from 'vue-toastification';
import ModalAdminProfile from '@/components/admin/modals/ModalAdminProfile.vue';
import ModalNotifications from '@/components/admin/modals/ModalNotifications.vue';
import ModalActivities from '@/components/admin/modals/ModalActivities.vue';

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const toast = useToast();

// Time State
const currentTime = ref('');
let clockInterval;

const updateClock = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

// Theme State
const isDark = ref(false);
const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
    toast.success('Modo oscuro activado');
  } else {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
    toast.success('Modo claro activado');
  }
};

// Chart Data (Mock Data matching design)
const chartData = ref({
  labels: ['Sede Principal', 'Santa Teresa', 'La Granja', 'Otras Sedes'],
  datasets: [
    {
      label: 'Consumo (kW)',
      backgroundColor: ['#4A90E2', '#B892FF', '#FFC074', '#FFD166'],
      borderRadius: 6,
      data: [8.5, 4.8, 3.2, 1.7]
    }
  ]
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: true
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
});

// Table Mock Data
const recentActivities = ref([
  { id: 1, timestamp: '23/06/2026 08:00 AM', campus: 'Sede Principal', room: 'Ambiente 101', instructor: 'Marlon Monsalve', event: 'Ingreso e inicio de sesión', statusClass: 'status-green', statusText: 'Normal' },
  { id: 2, timestamp: '23/06/2026 08:15 AM', campus: 'Sede Santa Teresa', room: 'Laboratorio Tics', instructor: 'Luisa Balial', event: 'Alerta consumo elevado', statusClass: 'status-orange', statusText: 'Revisión' },
  { id: 3, timestamp: '23/06/2026 09:30 AM', campus: 'La Granja', room: 'Sector Pecuario', instructor: 'Andrian Mauricio', event: 'ESP32 sin respuesta', statusClass: 'status-red', statusText: 'Fallo' },
  { id: 4, timestamp: '23/06/2026 09:45 AM', campus: 'Sede Principal', room: 'Biblioteca', instructor: 'Carlos Rojas', event: 'Apagado automático de luminarias', statusClass: 'status-green', statusText: 'Normal' },
  { id: 5, timestamp: '23/06/2026 10:00 AM', campus: 'Sede Santa Teresa', room: 'Auditorio', instructor: 'Diana Ortega', event: 'Encendido de aire acondicionado', statusClass: 'status-green', statusText: 'Normal' },
  { id: 6, timestamp: '23/06/2026 10:30 AM', campus: 'La Granja', room: 'Sector Agrícola', instructor: 'Jorge Gomez', event: 'Sensor de humedad desconectado', statusClass: 'status-orange', statusText: 'Revisión' },
  { id: 7, timestamp: '23/06/2026 11:15 AM', campus: 'Sede Principal', room: 'Sala de Juntas', instructor: 'Patricia Luna', event: 'Consumo inusual detectado', statusClass: 'status-orange', statusText: 'Revisión' },
  { id: 8, timestamp: '23/06/2026 11:30 AM', campus: 'La Granja', room: 'Sistemas de Riego', instructor: 'Andrian Mauricio', event: 'Cortocircuito de protección activado', statusClass: 'status-red', statusText: 'Fallo' }
]);

// Modal States
const showProfileModal = ref(false);
const showNotificationsModal = ref(false);
const showActivitiesModal = ref(false);

const notifications = ref([
  { id: 1, title: 'Alerta Consumo Extra', desc: 'Consumo elevado detectado en Sede Principal', badge: 'Revisión', badgeClass: 'badge-warning', resolved: false, resolving: false },
  { id: 2, title: 'Fallo de Conexión', desc: 'ESP32 Sede Granja desconectado', badge: 'Fallo', badgeClass: 'badge-danger', resolved: false, resolving: false }
]);

const resolveNotification = (notif) => {
  notif.resolving = true;
  setTimeout(() => {
    notif.resolved = true;
    toast.success(`Notificación "${notif.title}" resuelta`);
  }, 400);
};

onMounted(() => {
  isDark.value = document.documentElement.getAttribute('data-theme') === 'dark' || localStorage.getItem('theme') === 'dark';
  updateClock(); // Renderizado inmediato
  clockInterval = setInterval(updateClock, 1000);
});

onUnmounted(() => {
  clearInterval(clockInterval); // Limpieza obligatoria al destruir el componente
});
</script>

<style scoped>
/* Main shell layout configuration */
.admin-view-shell {
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeIn 300ms ease-in-out;
  
  /* Local spacing & styling definitions */
  --local-shadow-suave: rgba(0, 48, 64, 0.08);
  --local-shadow-media: rgba(0, 48, 64, 0.15);
}

/* Header Bar Styling */
.dashboard-header {
  background-color: var(--fondo-tarjetas);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--local-shadow-suave);
  margin-bottom: 1.5rem;
  border: 1px solid var(--borde);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  text-transform: uppercase;
  line-height: 1;
  margin: 0;
}

.header-subtitle {
  font-size: 0.9rem;
  color: var(--texto-secundario);
  font-weight: 500;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.user-info {
  display: flex;
  flex-direction: column;
  text-align: right;
  line-height: 1.2;
}

.user-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
}

.user-status {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sena-verde);
}

.user-avatar-wrapper {
  font-size: 3rem;
  color: var(--sena-negro);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 2 Column Layout - Grid Configuration */
.dashboard-grid {
  display: grid;
  grid-template-columns: 58% 42%;
  gap: 1.5rem;
}

/* Card Styling */
.card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: var(--local-shadow-suave);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  display: flex;
  align-items: center;
}

/* Left Column Styling */
.left-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex-grow: 1;
  min-height: 250px;
  position: relative;
  width: 100%;
}

/* Right Column Styling */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Metrics row styling */
.metrics-row {
  display: flex;
  gap: 1rem;
}

.metric-card {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 1rem;
  background-color: var(--fondo-tarjetas);
  border-left: 10px solid var(--sena-verde);
  border-radius: 16px;
  box-shadow: 0 2px 6px rgba(0, 48, 64, 0.04);
  transition: transform 150ms ease-in-out, box-shadow 150ms ease-in-out;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--local-shadow-suave);
}

.icon-box {
  background-color: #FFFFFF;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--sena-verde);
  font-size: 1.5rem;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.metric-text-box {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-secundario);
}

.metric-combined-value {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.value-number {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  line-height: 1.2;
}

.value-unit {
  font-size: 1rem;
  font-weight: 700;
  color: var(--sena-verde);
}

/* Notifications Card styling */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--fondo-app);
  border-radius: 12px;
  border: 1px solid var(--borde);
}

.notification-left-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-grow: 1;
}

.notification-body {
  display: flex;
  flex-direction: column;
}

.notification-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
}

.notification-desc {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}

.badge {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 6px;
  text-transform: uppercase;
}

.badge-warning {
  background-color: rgba(253, 195, 0, 0.15);
  color: #B7791F;
}

.badge-danger {
  background-color: rgba(229, 62, 62, 0.15);
  color: #C53030;
}

/* Bottom Full Width Column */
.bottom-full-column {
  grid-column: 1 / -1;
}

.table-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--borde);
  padding-bottom: 0.5rem;
}

.action-link {
  color: var(--sena-verde-oscuro);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 700;
}

.action-link:hover {
  text-decoration: underline;
  color: var(--sena-verde);
}

/* Table styling */
.table-responsive {
  overflow-x: auto;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.activity-table th {
  padding: 1rem;
  background-color: var(--fondo-app);
  color: var(--texto-secundario);
  font-weight: 700;
  font-size: 0.75rem;
  border-bottom: 2px solid var(--borde);
}

.activity-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--borde);
  font-size: 0.875rem;
  color: var(--texto-principal);
  vertical-align: middle;
}

.activity-table tr:hover td {
  background-color: rgba(57, 169, 0, 0.02);
}

.time-cell {
  font-family: monospace;
  font-size: 0.75rem;
}

.cell-location, .cell-event {
  display: flex;
  flex-direction: column;
}

.location-main, .event-user {
  font-weight: 700;
}

.location-sub, .event-desc {
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
}

.status-green {
  background-color: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
}

.status-orange {
  background-color: rgba(253, 195, 0, 0.1);
  color: var(--sena-naranja);
}

.status-red {
  background-color: rgba(229, 62, 62, 0.1);
  color: #E53E3E;
}

/* Simulated Modals Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 150ms ease-in-out;
}

.modal-card {
  background: var(--fondo-tarjetas);
  border-radius: 16px;
  border: 1px solid var(--borde);
  width: 90%;
  max-width: 450px;
  box-shadow: var(--local-shadow-media);
  animation: slideUp 300ms ease-in-out;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 1.125rem;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 9999px;
  background-color: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.875rem;
  margin-bottom: 1rem;
}

.profile-name {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
}

.profile-email {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin: 4px 0 0 0;
}

.divider {
  width: 100%;
  border: none;
  border-top: 1px solid var(--borde);
  margin: 1rem 0;
}

.profile-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.profile-details p {
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background-color: var(--fondo-app);
  border-top: 1px solid var(--borde);
}

.btn-secondary {
  background-color: transparent;
  color: var(--texto-secundario);
  border: 1px solid var(--borde);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: var(--borde);
  color: var(--texto-principal);
}

.notification-checkbox-wrapper {
  margin-right: 8px;
  display: flex;
  align-items: center;
}

.notif-circle-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(0, 48, 64, 0.15);
  background-color: rgba(0, 48, 64, 0.04);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 150ms ease-in-out;
  padding: 0;
}

.notif-circle-check:hover {
  border-color: var(--sena-verde);
  background-color: rgba(57, 169, 0, 0.1);
  transform: scale(1.1);
}

.check-icon {
  font-size: 0.75rem;
  color: var(--sena-verde);
  opacity: 0;
  transition: opacity 150ms ease-in-out;
}

.notif-circle-check:hover .check-icon {
  opacity: 1;
}

.empty-notifications {
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.85rem;
  padding: 1.5rem 0;
  font-weight: 500;
}

/* Slide out animation for resolved notifications */
.resolving-out {
  animation: slideOutRight 400ms forwards;
}

@keyframes slideOutRight {
  0% {
    transform: translateX(0);
    opacity: 1;
  }
  100% {
    transform: translateX(30px);
    opacity: 0;
    max-height: 0;
    padding: 0;
    margin: 0;
    border: none;
  }
}

.notifications-footer {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
  border-top: 1px solid var(--borde);
  padding-top: 0.5rem;
}

.table-footer {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  border-top: 1px solid var(--borde);
  padding-top: 1rem;
}

.show-more-btn {
  background: transparent;
  border: none;
  color: var(--sena-verde-oscuro);
  font-weight: 700;
  font-size: 0.8rem;
  cursor: pointer;
  transition: color 150ms ease-in-out;
}

.show-more-btn:hover {
  color: var(--sena-verde);
  text-decoration: underline;
}

/* Responsiveness settings */
@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    text-align: center;
  }
  .header-right {
    justify-content: center;
  }
}
</style>