<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content profile-modal">
      <header class="modal-header">
        <h2>Perfil Del Aprendiz</h2>
        <button class="btn-close" @click="closeModal">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </header>

      <div class="modal-body profile-grid">
        <!-- COLUMNA IZQUIERDA -->
        <div class="left-col">
          <div class="profile-header">
            <div class="avatar-container">
              <img :src="aprendiz?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + aprendiz?.nombre" alt="Avatar" class="profile-avatar" />
              <div class="status-indicator" :class="aprendiz?.deviceId ? 'online' : 'offline'"></div>
            </div>
            <div class="profile-title">
              <h3>{{ aprendiz?.nombre }}</h3>
              <span class="status-badge" :class="aprendiz?.deviceId ? 'status-vinculado' : 'status-pendiente'">
                <font-awesome-icon icon="fa-solid fa-check-circle" /> 
                {{ aprendiz?.deviceId ? 'Vinculado' : 'Sin Dispositivo' }}
              </span>
              <p class="role-text">Aprendiz Activo</p>
            </div>
          </div>

          <div class="info-list">
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-id-card" class="info-icon"/> Documento</span>
              <span class="info-value">{{ aprendiz?.documento }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-hashtag" class="info-icon"/> Ficha</span>
              <span class="info-value">{{ aprendiz?.ficha }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-laptop-code" class="info-icon"/> Programa</span>
              <span class="info-value">Análisis Y Desarrollo de Software</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-envelope" class="info-icon"/> Correo</span>
              <span class="info-value">{{ aprendiz?.correo || 'correo@misena.edu.co' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-phone" class="info-icon"/> Telefono</span>
              <span class="info-value">{{ aprendiz?.telefono || '3158709236' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-building" class="info-icon"/> Ambiente Asignado</span>
              <span class="info-value">{{ aprendiz?.ambiente || 'Sala 105 - sistema' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-calendar-days" class="info-icon"/> Fecha De Asignación</span>
              <span class="info-value">{{ aprendiz?.assignDate || '17/06/2026' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label"><font-awesome-icon icon="fa-solid fa-user-tie" class="info-icon"/> Instructor Asignado</span>
              <span class="info-value">{{ aprendiz?.instructor || 'Inst. Marlon Monsalve' }}</span>
            </div>
          </div>

          <div class="device-card" v-if="aprendiz?.deviceId">
            <div class="device-header">
              <h4>Dispositivo IoT Asignado</h4>
            </div>
            <div class="mac-badge">
              <span>{{ aprendiz?.deviceId }}</span>
              <font-awesome-icon icon="fa-solid fa-signal" class="signal-icon good" />
            </div>
            <div class="device-details">
              <div class="detail-row">
                <span class="detail-label">Tipo:</span>
                <span class="detail-value">NFC/IoT</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Estado:</span>
                <span class="detail-value">Conectado <span class="dot green-dot"></span></span>
              </div>
            </div>
          </div>
          <div class="device-card empty" v-else>
            <p>El aprendiz no tiene ningún dispositivo vinculado actualmente.</p>
          </div>
        </div>

        <!-- COLUMNA DERECHA -->
        <div class="right-col">
          <div class="section-header">
            <h3>Actividad del Dispositivo</h3>
            <select class="time-select">
              <option>últimos 7 días</option>
              <option>último mes</option>
            </select>
          </div>

          <div class="stats-row">
            <div class="mini-stat">
              <div class="stat-head">
                <font-awesome-icon icon="fa-solid fa-clock-rotate-left" class="icon-blue" />
                <span>Ultima conexión</span>
              </div>
              <div class="stat-body">
                <strong>Hoy, 10:45 a.m.</strong>
                <small>17/06/2026</small>
              </div>
            </div>
            <div class="mini-stat">
              <div class="stat-head">
                <font-awesome-icon icon="fa-solid fa-wifi" class="icon-green" />
                <span>Tiempo Conectado</span>
              </div>
              <div class="stat-body">
                <strong>{{ statsData.tiempoConectado }}</strong>
                <small>En los últimos 7 días</small>
              </div>
            </div>
            <div class="mini-stat">
              <div class="stat-head">
                <font-awesome-icon icon="fa-solid fa-chart-line" class="icon-gray" />
                <span>Conexiones</span>
              </div>
              <div class="stat-body">
                <strong>{{ statsData.totalConexiones }}</strong>
                <small>En los últimos 7 días</small>
              </div>
            </div>
            <div class="mini-stat">
              <div class="stat-head">
                <font-awesome-icon icon="fa-solid fa-signal" class="icon-blue" />
                <span>Señal promedio</span>
              </div>
              <div class="stat-body">
                <strong>{{ statsData.senalPromedio }}%</strong>
                <small :class="statsData.senalPromedio >= 80 ? 'text-green' : 'text-yellow'">
                  {{ statsData.senalPromedio >= 80 ? 'Buena' : 'Regular' }}
                </small>
              </div>
            </div>
          </div>

          <div class="charts-row">
            <div class="chart-box">
              <h4>Conexiones por día</h4>
              <p class="chart-subtitle">Conexiones</p>
              <div class="bar-chart-container" style="height: 150px; position: relative; margin-bottom: 1rem;">
                <Bar v-if="barChartData" :data="barChartData" :options="barChartOptions" />
              </div>
              <div class="chart-footer">
                <button class="btn-text">Mostrar Anterior mes <font-awesome-icon icon="fa-solid fa-chevron-down" /></button>
              </div>
            </div>
            
            <div class="chart-box doughnut-box">
              <div class="circular-progress" style="position: relative; width: 130px; height: 130px; margin-bottom: 1rem;">
                <Doughnut v-if="doughnutChartData" :data="doughnutChartData" :options="doughnutChartOptions" />
                <div class="doughnut-center-text">
                  <span class="percentage">{{ statsData.porcentajeOperativo }}%</span>
                  <span class="label">Operativo</span>
                </div>
              </div>
              <div class="legend">
                <div class="legend-item"><span class="dot green-dot"></span> Operativo <span class="val">{{ statsData.porcentajeOperativo }}%</span></div>
                <div class="legend-item"><span class="dot yellow-dot"></span> Intermitente <span class="val">{{ statsData.porcentajeIntermitente }}%</span></div>
                <div class="legend-item"><span class="dot red-dot"></span> Sin conexión <span class="val">{{ statsData.porcentajeDesconectado }}%</span></div>
              </div>
            </div>
          </div>

          <div class="recent-connections">
            <h4>Conexiones Recientes</h4>
            <div class="table-container">
              <table class="recent-table">
                <thead>
                  <tr>
                    <th>FECHA Y HORA</th>
                    <th>DURACIÓN</th>
                    <th>ESTADO</th>
                    <th>SEÑAL</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(conn, idx) in statsData.conexionesRecientes" :key="idx">
                    <td>{{ conn.fechaHora }}</td>
                    <td>{{ conn.duracion }}</td>
                    <td>
                      <span class="status-badge xs" :class="conn.estado === 'Conectado' ? 'status-vinculado' : 'status-rojo'">
                        {{ conn.estado }}
                      </span>
                    </td>
                    <td>
                      <template v-if="conn.senal">
                        <font-awesome-icon icon="fa-solid fa-signal" :class="conn.senal.valor >= 80 ? 'text-green' : 'text-yellow'"/> 
                        {{ conn.senal.texto }} ({{ conn.senal.valor }}%)
                      </template>
                      <template v-else>-</template>
                    </td>
                  </tr>
                  <tr v-if="statsData.conexionesRecientes?.length === 0">
                    <td colspan="4" style="text-align: center;">No hay conexiones registradas.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>

      <footer class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cerrar</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

const props = defineProps({
  show: Boolean,
  aprendiz: Object
});

const emit = defineEmits(['update:show', 'close']);

// --- Chart Data & Options ---
const barChartData = ref(null);
const doughnutChartData = ref(null);
const statsData = ref({
  tiempoConectado: '0h 0min',
  totalConexiones: 0,
  senalPromedio: 0,
  porcentajeOperativo: 0,
  porcentajeIntermitente: 0,
  porcentajeDesconectado: 0,
  conexionesRecientes: []
});

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#00324b',
      padding: 10,
      cornerRadius: 8,
      displayColors: false,
    }
  },
  scales: {
    y: { 
      beginAtZero: true, 
      ticks: { stepSize: 1, color: '#6c757d' }, 
      grid: { color: 'rgba(0,0,0,0.05)' },
      border: { display: false }
    },
    x: { 
      ticks: { color: '#6c757d' }, 
      grid: { display: false },
      border: { display: false }
    }
  }
};

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '80%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#00324b',
      padding: 10,
      cornerRadius: 8,
      displayColors: false,
    }
  }
};

// --- Mock Stats Generator with LocalStorage ---
const loadStats = (deviceId) => {
  if (!deviceId) {
    resetStats();
    return;
  }

  const storageKey = `mock_stats_${deviceId}`;
  let data = localStorage.getItem(storageKey);

  if (!data) {
    // Generate realistic random mock stats for this device
    const conexiones = Math.floor(Math.random() * 20) + 5;
    const senal = Math.floor(Math.random() * 30) + 70; // 70 to 100
    const operativo = Math.floor(Math.random() * 20) + 75; // 75 to 95
    const intermitente = Math.floor(Math.random() * 15);
    const desconectado = 100 - operativo - intermitente;

    const mockObj = {
      tiempoConectado: `${Math.floor(Math.random() * 40) + 10}h ${Math.floor(Math.random() * 59)} min`,
      totalConexiones: conexiones,
      senalPromedio: senal,
      porcentajeOperativo: operativo,
      porcentajeIntermitente: intermitente,
      porcentajeDesconectado: desconectado,
      barLabels: ['13/06', '14/06', '15/06', '16/06'],
      barData: [
        Math.floor(Math.random() * 5) + 1,
        Math.floor(Math.random() * 5) + 1,
        Math.floor(Math.random() * 5) + 1,
        conexiones - 10
      ],
      conexionesRecientes: [
        { fechaHora: 'Hoy 09:15 a.m.', duracion: '1 h 15 min', estado: 'Conectado', senal: { texto: 'Excelente', valor: senal + 2 } },
        { fechaHora: 'Ayer 10:22 a.m.', duracion: '2 h 22 min', estado: 'Conectado', senal: { texto: 'Buena', valor: senal - 5 } },
        { fechaHora: 'Ayer 08:15 a.m.', duracion: '1 h 15 min', estado: 'Conectado', senal: { texto: 'Regular', valor: senal - 25 } },
        { fechaHora: 'Hace 2 días 12:10 p.m.', duracion: '4 h 10 min', estado: 'Sin Conexión', senal: null }
      ]
    };
    
    localStorage.setItem(storageKey, JSON.stringify(mockObj));
    data = JSON.stringify(mockObj);
  }

  const parsed = JSON.parse(data);
  statsData.value = parsed;

  barChartData.value = {
    labels: parsed.barLabels,
    datasets: [{
      label: 'Conexiones',
      data: parsed.barData,
      backgroundColor: '#39a900',
      borderRadius: 4,
      barThickness: 20
    }]
  };

  doughnutChartData.value = {
    labels: ['Operativo', 'Intermitente', 'Sin conexión'],
    datasets: [{
      data: [parsed.porcentajeOperativo, parsed.porcentajeIntermitente, parsed.porcentajeDesconectado],
      backgroundColor: ['#39a900', '#fdc300', '#d32f2f'],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };
};

const resetStats = () => {
  statsData.value = {
    tiempoConectado: '0h 0min',
    totalConexiones: 0,
    senalPromedio: 0,
    porcentajeOperativo: 0,
    porcentajeIntermitente: 0,
    porcentajeDesconectado: 0,
    conexionesRecientes: []
  };
  barChartData.value = { labels: [], datasets: [] };
  doughnutChartData.value = { labels: [], datasets: [] };
};

// React to modal opening
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadStats(props.aprendiz?.deviceId);
  }
});

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

.profile-modal {
  background: var(--fondo-app);
  width: 100%;
  max-width: 1100px;
  max-height: 90vh;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 2rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-bottom: 1px solid var(--borde, #e0e0e0);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--sena-azul-oscuro, #00324b);
  font-weight: 800;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--texto-secundario, #666);
  cursor: pointer;
  transition: color 0.2s;
}
.btn-close:hover { color: var(--sena-rojo, #d32f2f); }

.modal-body {
  flex: 1;
  overflow-y: auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  background: var(--fondo-tarjetas);
}

/* LEFT COLUMN */
.left-col {
  padding: 2rem;
  border-right: 1px solid var(--borde);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: 2rem;
}

.avatar-container {
  position: relative;
  width: 80px;
  height: 80px;
}

.profile-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: var(--fondo-app);
  border: 3px solid var(--sena-verde);
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 3px solid var(--fondo-tarjetas);
}
.status-indicator.online { background: var(--sena-verde); }
.status-indicator.offline { background: var(--texto-secundario); }

.profile-title h3 {
  margin: 0 0 6px 0;
  color: var(--sena-azul-oscuro);
  font-size: 1.2rem;
  font-weight: 800;
}

.role-text {
  margin: 6px 0 0 0;
  color: var(--texto-secundario);
  font-size: 0.85rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 700;
}
.status-vinculado { background: rgba(57, 169, 0, 0.1); color: var(--sena-verde); }
.status-pendiente { background: rgba(253, 195, 0, 0.1); color: var(--sena-amarillo); }
.status-rojo { background: rgba(211, 47, 47, 0.1); color: #d32f2f; }

.info-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--borde);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 0.9rem;
}

.info-label {
  color: var(--sena-azul-oscuro);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  color: var(--texto-secundario);
  width: 16px;
}

.info-value {
  color: var(--texto-secundario);
  text-align: right;
  max-width: 50%;
  word-break: break-word;
}

.device-card {
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.2rem;
  background: var(--fondo-app);
}

.device-card.empty {
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.9rem;
  padding: 2rem 1rem;
}

.device-header h4 {
  margin: 0 0 1rem 0;
  color: var(--sena-azul-oscuro);
  font-size: 0.95rem;
  text-align: center;
}

.mac-badge {
  background: var(--fondo-tarjetas);
  border: 1px solid rgba(80, 229, 249, 0.3);
  color: var(--sena-azul-oscuro);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 800;
  font-size: 1.1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.signal-icon.good { color: #4285f4; }

.device-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.85rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
}

.detail-label { color: var(--texto-secundario); }
.detail-value { color: var(--texto-principal); font-weight: 600; display: flex; align-items: center; gap: 6px; }

.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.green-dot { background: var(--sena-verde); }
.yellow-dot { background: var(--sena-amarillo); }
.red-dot { background: #d32f2f; }

/* RIGHT COLUMN */
.right-col {
  padding: 2rem;
  background: var(--fondo-app);
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  color: var(--sena-azul-oscuro);
  font-size: 1.1rem;
}

.time-select {
  padding: 0.4rem 2rem 0.4rem 1rem;
  border: 1px solid var(--borde);
  border-radius: 6px;
  background-color: var(--fondo-tarjetas);
  color: var(--texto-principal);
  font-size: 0.85rem;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.mini-stat {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 1rem;
}

.stat-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin-bottom: 8px;
}
.icon-blue { color: #4285f4; }
.icon-green { color: var(--sena-verde); }
.icon-gray { color: var(--texto-secundario); }

.stat-body {
  display: flex;
  flex-direction: column;
}
.stat-body strong {
  font-size: 0.9rem;
  color: var(--texto-principal);
  margin-bottom: 4px;
}
.stat-body small {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}
.text-green { color: var(--sena-verde); font-weight: 700; }
.text-yellow { color: var(--sena-amarillo); font-weight: 700; }

.charts-row {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-box {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.5rem;
}

.chart-box h4 {
  margin: 0 0 4px 0;
  color: var(--sena-azul-oscuro);
  font-size: 1rem;
}

.chart-subtitle {
  margin: 0 0 1rem 0;
  color: var(--texto-secundario);
  font-size: 0.75rem;
}

/* CIRCULAR CHART TEXT OVERLAY */
.doughnut-center-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
}
.doughnut-center-text .percentage {
  color: var(--sena-azul-oscuro);
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
}
.doughnut-center-text .label {
  color: var(--texto-secundario);
  font-size: 0.75rem;
  margin-top: 4px;
}

.chart-footer {
  text-align: center;
}
.btn-text {
  background: none;
  border: none;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 0.5rem;
}
.btn-text:hover {
  color: var(--sena-azul-oscuro);
}

.doughnut-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  font-size: 0.8rem;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--texto-secundario);
}
.legend-item .val {
  margin-left: auto;
  font-weight: 700;
  color: var(--texto-principal);
}

/* RECENT CONNECTIONS */
.recent-connections h4 {
  margin: 0 0 1rem 0;
  color: var(--sena-azul-oscuro);
  font-size: 1rem;
}

.table-container {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  overflow: hidden;
}

.recent-table {
  width: 100%;
  border-collapse: collapse;
}

.recent-table th {
  background: rgba(0,0,0,0.02);
  text-align: left;
  padding: 0.8rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
  border-bottom: 1px solid var(--borde);
}

.recent-table td {
  padding: 0.8rem 1rem;
  font-size: 0.85rem;
  color: var(--texto-secundario);
  border-bottom: 1px solid var(--borde);
}

.recent-table tr:last-child td {
  border-bottom: none;
}

.status-badge.xs {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1.25rem 2rem;
  background: var(--fondo-tarjetas, #ffffff);
  border-top: 1px solid var(--borde, #e0e0e0);
}

.btn-cancel {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 0.65rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-cancel:hover { background: var(--borde); }

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .left-col {
    border-right: none;
    border-bottom: 1px solid var(--borde);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
  .stats-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
