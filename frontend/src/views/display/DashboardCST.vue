<script setup>
import { ref, shallowRef, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useRole } from "@/composables/useRole";
import DarkModeToggle from "@/components/DarkModeToggle.vue";

// Chart.js e integraciones de Vue
import { Line, Doughnut, Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, 
  LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler 
} from 'chart.js'

// Registro de componentes de Chart.js
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

const router = useRouter();
const { hasRole } = useRole();
const currentTime = ref(new Date().toLocaleTimeString());

// ==========================================
// 1. MOCKS DE DATOS (Dinamizador)
// ==========================================

const kpis = ref({
  consumoHoy: 124.5,
  genSolar: 45,
  ahorroVsMesAnt: -12,
  huellaEvitada: 25,
  picoConsumo: { hora: '11:30 am', lugar: 'Taller de soldadura' }
});

const alertas = ref([
  { id: 1, type: 'critical', text: 'Taller de soldadura consumió 30% más que ayer a la misma hora.', time: '11:45 am' },
  { id: 2, type: 'warning', text: 'Consumo nocturno (2am-5am): 8 kWh - Posible equipo encendido en Sistemas.', time: '05:00 am' },
  { id: 3, type: 'info', text: 'Panel solar 3 sin generación detectada.', time: '10:15 am' }
]);

const senaMetrics = ref({
  kwhAprendizDia: 0.8,
  kwhHora: 4.2,
  metaAhorroProgreso: 65
});

// ==========================================
// 2. CONFIGURACIÓN DE GRÁFICOS (shallowRef para evitar desbordamiento de memoria Proxy)
// ==========================================

const lineChartData = shallowRef({
  labels: ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],
  datasets: [{
    label: 'Consumo Global (kWh)',
    data: [12, 45, 80, 110, 95, 85, 40, 15],
    borderColor: '#39A900', // Verde SENA
    backgroundColor: 'rgba(57, 169, 0, 0.1)',
    fill: true,
    tension: 0.4
  }]
});

const doughnutChartData = shallowRef({
  labels: ['Taller Motos', 'Sistemas', 'Cocina', 'Admin', 'Exterior'],
  datasets: [{
    data: [40, 25, 15, 10, 10],
    backgroundColor: ['#39A900', '#00324D', '#F27B35', '#0072CE', '#6b7280'],
    borderWidth: 0
  }]
});

const barChartData = shallowRef({
  labels: ['Mes Actual', 'Mes Anterior', 'Año Pasado'],
  datasets: [{
    label: 'Consumo (kWh)',
    data: [1500, 1700, 1850],
    backgroundColor: ['#39A900', '#00324D', '#cccccc'],
    borderRadius: 4
  }]
});

const commonChartOptions = shallowRef({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12 } }
  }
});

// ==========================================
// 3. MAPA DE CALOR (Generación Manual CSS)
// ==========================================
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie'];
const horasHeatmap = ['06:00', '10:00', '14:00', '18:00'];
const heatmapData = ref([
  [2, 3, 2, 4, 2], // 06:00
  [8, 9, 7, 9, 8], // 10:00
  [9, 10, 9, 10, 7], // 14:00
  [4, 5, 4, 3, 2], // 18:00
]);

const getHeatColor = (val) => {
  if (val <= 3) return '#dcfce7'; // Verde claro (Bajo)
  if (val <= 6) return '#86efac'; // Verde medio
  if (val <= 8) return '#fde047'; // Amarillo (Medio/Alto)
  return '#ef4444'; // Rojo (Crítico)
};

// ==========================================
// 4. CICLO DE VIDA Y MÉTODOS
// ==========================================
onMounted(() => {
  if (!hasRole(["dinamizador", "instructor"])) {
    router.push("/login");
  }
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString();
  }, 1000);
});

const descargarExcel = () => {
  alert("Generando reporte Excel para análisis de eficiencia energética...");
};
</script>

<template>
  <div class="dashboard-shell">
    
    <!-- ENCABEZADO -->
    <header class="dash-header">
      <div class="header-left">
        <div class="logo-duo">
          <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
          <div class="logo-divider" />
          <img src="@/assets/VoltMindAccess1.svg" alt="VoltMind" class="logo-volt" />
        </div>
        <div class="environment-badge">
          <h1>TABLERO DE EFICIENCIA ENERGÉTICA</h1>
          <p class="header-meta">
            Vista: Dinamizador | <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>
      <div class="header-right-actions">
        <button class="btn-primary" @click="router.push('/admin/monitor-aulas')">
          <font-awesome-icon icon="fa-solid fa-layer-group" /> Supervisión por Aulas
        </button>
        <button class="btn-dev-back" @click="router.push('/login')">
          <font-awesome-icon icon="fa-solid fa-right-from-bracket" /> Salir
        </button>
      </div>
    </header>

    <!-- 1. KPIs GLOBALES -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <span class="kpi-label">Consumo Hoy</span>
        <div class="kpi-val">{{ kpis.consumoHoy }} <small>kWh</small></div>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Generación Solar Hoy</span>
        <div class="kpi-val highlight-green">{{ kpis.genSolar }} <small>kWh</small></div>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">% Ahorro (vs Mes Ant)</span>
        <div class="kpi-val" :class="kpis.ahorroVsMesAnt < 0 ? 'highlight-green' : 'highlight-red'">
          {{ kpis.ahorroVsMesAnt }}%
        </div>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Huella CO₂ Evitada</span>
        <div class="kpi-val">{{ kpis.huellaEvitada }} <small>Kg</small></div>
      </div>
      <div class="kpi-card pico-card">
        <span class="kpi-label">Pico de Consumo</span>
        <div class="kpi-val small-val">{{ kpis.picoConsumo.hora }}</div>
        <div class="kpi-sub">{{ kpis.picoConsumo.lugar }}</div>
      </div>
    </section>

    <!-- 2. GRID CENTRAL DE MÓDULOS -->
    <main class="main-dashboard-grid">
      
      <!-- Fila 1: Line Chart (2/3) y Doughnut (1/3) -->
      <div class="module-card col-span-2">
        <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-bolt" /> Consumo en Tiempo Real (15 min)</h2>
        <div class="chart-container">
          <Line :data="lineChartData" :options="commonChartOptions" />
        </div>
      </div>
      
      <div class="module-card">
        <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-chart-pie" /> Por Centro de Costo (Ambientes)</h2>
        <div class="chart-container">
          <Doughnut :data="doughnutChartData" :options="commonChartOptions" />
        </div>
      </div>

      <!-- Fila 2: Bar Chart (2/3) y Heatmap (1/3) -->
      <div class="module-card col-span-2">
        <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-chart-column" /> Comparativo Histórico</h2>
        <div class="chart-container">
          <Bar :data="barChartData" :options="commonChartOptions" />
        </div>
      </div>
      
      <div class="module-card">
        <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-fire" /> Mapa de Calor (Horas vs Días)</h2>
        <div class="heatmap-container">
          <table class="heatmap-table">
            <thead>
              <tr>
                <th></th>
                <th v-for="d in diasSemana" :key="d">{{ d }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(fila, i) in heatmapData" :key="i">
                <td class="hm-hora">{{ horasHeatmap[i] }}</td>
                <td v-for="(val, j) in fila" :key="j" :style="{ backgroundColor: getHeatColor(val) }" class="hm-cell" :title="val + ' kWh'"></td>
              </tr>
            </tbody>
          </table>
          <div class="hm-legend">
            <span class="legend-box" style="background:#dcfce7"></span> <small>Bajo</small>
            <span class="legend-box" style="background:#fde047"></span> <small>Medio</small>
            <span class="legend-box" style="background:#ef4444"></span> <small>Alto</small>
          </div>
        </div>
      </div>

      <!-- Fila 3: Alertas (2/3) y Módulo SENA (1/3) -->
      <div class="module-card col-span-2">
        <h2 class="module-title"><font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> Alertas y Anomalías Detectadas</h2>
        <div class="alerts-table-wrapper">
          <table class="alerts-table">
            <tbody>
              <tr v-for="alerta in alertas" :key="alerta.id">
                <td class="alert-icon" :class="'icon-' + alerta.type">
                  <font-awesome-icon v-if="alerta.type==='critical'" icon="fa-solid fa-triangle-exclamation" />
                  <font-awesome-icon v-else-if="alerta.type==='warning'" icon="fa-solid fa-circle-exclamation" />
                  <font-awesome-icon v-else icon="fa-solid fa-info-circle" />
                </td>
                <td class="alert-text">{{ alerta.text }}</td>
                <td class="alert-time">{{ alerta.time }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="module-card sena-module">
        <h2 class="module-title sena-title">
          <img src="@/assets/LogoSena.png" class="sena-icon-mini"/> Módulo Formación SENA
        </h2>
        <div class="sena-metrics">
          <div class="sena-row">
            <span>Ind. por Aprendiz</span>
            <strong>{{ senaMetrics.kwhAprendizDia }} <small>kWh/día</small></strong>
          </div>
          <div class="sena-row">
            <span>Ind. por Hora Form.</span>
            <strong>{{ senaMetrics.kwhHora }} <small>kWh/hora</small></strong>
          </div>
          
          <div class="sena-goal">
            <span>Meta de Ahorro Mensual</span>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" :style="{ width: senaMetrics.metaAhorroProgreso + '%' }"></div>
            </div>
            <div class="progress-text">{{ senaMetrics.metaAhorroProgreso }}% alcanzado</div>
          </div>

          <button class="btn-excel" @click="descargarExcel">
            <font-awesome-icon icon="fa-solid fa-file-excel" /> Descargar Datos (Clase)
          </button>
        </div>
      </div>

    </main>
    <DarkModeToggle />
  </div>
</template>

<style scoped>
.dashboard-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  background-color: var(--fondo-app);
  padding: 1.5rem;
  box-sizing: border-box;
}

/* ENCABEZADO */
.dash-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
@media (min-width: 992px) {
  .dash-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  .header-left {
    flex-direction: row;
    gap: 2.5rem;
  }
}
.logo-duo { display: flex; align-items: center; gap: 16px; }
.logo-sena { height: 38px; }
.logo-volt { height: 34px; }
.logo-divider { width: 1px; height: 26px; background: var(--borde); }
.environment-badge h1 {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
}
.header-meta span {
  color: var(--sena-azul-oscuro);
  font-family: monospace;
  font-weight: 600;
}
.header-right-actions { display: flex; gap: 1rem; align-items: center; }
.btn-primary {
  background: var(--sena-verde);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-primary:hover { background: var(--sena-verde-oscuro); }
.btn-dev-back {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-dev-back:hover { background: var(--sena-verde-oscuro); }

/* KPIS GLOBALES */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.kpi-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.kpi-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.kpi-val {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--sena-azul-oscuro);
}
.kpi-val small { font-size: 0.9rem; color: var(--texto-secundario); font-weight: 600; }
.highlight-green { color: var(--sena-verde); }
.highlight-red { color: #ef4444; }
.pico-card { border-left: 4px solid var(--sena-naranja); }
.small-val { font-size: 1.2rem; }
.kpi-sub { font-size: 0.8rem; color: var(--texto-secundario); margin-top: 4px; }

/* GRID PRINCIPAL */
.main-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.col-span-2 {
  grid-column: span 2;
}
@media (max-width: 1024px) {
  .main-dashboard-grid { grid-template-columns: 1fr; }
  .col-span-2 { grid-column: span 1; }
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
}
.module-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.chart-container {
  position: relative;
  height: 250px;
  width: 100%;
  flex-grow: 1;
}

/* MAPA DE CALOR */
.heatmap-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex-grow: 1;
}
.heatmap-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 4px;
}
.heatmap-table th {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  font-weight: 600;
  text-align: center;
  padding-bottom: 4px;
}
.hm-hora {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  font-weight: 600;
  text-align: right;
  padding-right: 8px;
  width: 40px;
}
.hm-cell {
  border-radius: 4px;
  height: 35px;
  transition: transform 0.2s;
  cursor: pointer;
}
.hm-cell:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.hm-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: auto;
}
.legend-box {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 4px;
}

/* TABLA ALERTAS */
.alerts-table-wrapper {
  overflow-x: auto;
}
.alerts-table {
  width: 100%;
  border-collapse: collapse;
}
.alerts-table td {
  padding: 12px;
  border-bottom: 1px solid var(--borde);
  font-size: 0.85rem;
}
.alerts-table tr:last-child td { border-bottom: none; }
.alert-icon { width: 30px; text-align: center; font-size: 1.1rem; }
.icon-critical { color: #ef4444; }
.icon-warning { color: var(--sena-amarillo); }
.icon-info { color: var(--sena-azul); }
.alert-text { color: var(--texto-principal); font-weight: 600; }
.alert-time { color: var(--texto-secundario); text-align: right; font-variant-numeric: tabular-nums; }

/* MÓDULO SENA */
.sena-module {
  border: 2px solid rgba(57, 169, 0, 0.2);
  background: linear-gradient(to bottom, #ffffff, #f0fdf4);
}
.sena-title { color: var(--sena-verde-oscuro); }
.sena-icon-mini { height: 20px; }
.sena-metrics { display: flex; flex-direction: column; gap: 1.25rem; flex-grow: 1; }
.sena-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--borde);
}
.sena-row span { font-size: 0.8rem; color: var(--texto-secundario); font-weight: 600; }
.sena-row strong { font-size: 1rem; color: var(--sena-azul-oscuro); }

.sena-goal span { font-size: 0.8rem; color: var(--texto-secundario); font-weight: 600; display: block; margin-bottom: 8px;}
.progress-bar-bg { width: 100%; height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: var(--sena-verde); transition: width 1s ease-out; }
.progress-text { font-size: 0.75rem; text-align: right; margin-top: 4px; color: var(--sena-verde-oscuro); font-weight: 700; }

.btn-excel {
  margin-top: auto;
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s;
}
.btn-excel:hover { background: #1d4ed8; }
</style>
