<template>
  <div class="admin-view-shell">
    <!-- Header principal -->
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>AMBIENTES Y HORARIOS</h1>
          <p class="header-meta">
            Programación académica por bloques | 03:15:50 PM
          </p>
        </div>
      </div>
      <div class="header-right user-profile">
        <div class="user-info">
          <span class="user-name">Nelson Contreras</span>
          <span class="user-status">En línea</span>
        </div>
        <div class="user-avatar">
          <font-awesome-icon :icon="['fas', 'circle-user']" />
        </div>
      </div>
    </header>

    <!-- Barra de herramientas (Filtros y botones) -->
    <div class="toolbar-section">
      <div class="toolbar-left">
        <button class="btn-info-sedes" @click="showModalSedes = true">
          <font-awesome-icon :icon="['fas', 'circle-info']" /> Información de Sedes
        </button>
      </div>
      <div class="toolbar-right">
        <div class="date-picker-wrapper">
          <input type="date" class="form-input date-filter" v-model="currentDate" />
          <font-awesome-icon :icon="['fas', 'calendar-days']" class="input-icon" />
        </div>
        <div class="search-wrapper">
          <font-awesome-icon :icon="['fas', 'magnifying-glass']" class="search-icon" />
          <input type="text" class="form-input search-instructor" v-model="searchQuery" placeholder="Buscar por Instructor o Ficha" />
        </div>
        <select class="form-input select-filter" v-model="selectedSede">
          <option value="caaa">Sede: CAAA</option>
          <option value="orito">Sede Orito</option>
          <option value="pto-leguizamo">Sede: Pto Leguizamo</option>
          <option value="maguere">Sede Magueré</option>
          <option value="machindinoy">Sede Machindinoy</option>
        </select>
      </div>
    </div>

    <!-- Contenido Principal -->
    <main class="dash-grid">
      <section class="dash-col">
        <div class="module-card">
          <h2 class="module-title mb-4">
            <font-awesome-icon :icon="['fas', 'calendar-days']" /> Programación de Ambientes (CAAA)
          </h2>
          
          <div class="matrix-wrapper">
            <div class="grid-matrix" :style="{ gridTemplateColumns: `220px repeat(${bloques.length}, minmax(200px, 1fr))` }">
              <!-- Header Row (Jornadas/Bloques) -->
              <div class="matrix-cell header-cell corner-cell">AMBIENTES</div>
              <div v-for="bloque in bloques" :key="bloque" class="matrix-cell header-cell time-cell">
                <font-awesome-icon :icon="['fas', 'clock']" class="time-icon" />
                {{ bloque }}
              </div>

              <!-- Matrix Rows -->
              <template v-for="ambiente in ambientes" :key="ambiente.id">
                <!-- Room Label -->
                <div class="matrix-cell room-cell">
                  <strong class="room-name">{{ ambiente.name }}</strong>
                  <span class="room-capacity">
                    <font-awesome-icon :icon="['fas', 'users']" />
                    Limite: {{ ambiente.capacity }}
                  </span>
                </div>
                
                <!-- Schedule Cells -->
                <div v-for="bloque in bloques" :key="`${ambiente.id}-${bloque}`" class="matrix-cell data-cell">
                  <template v-if="getSessions(ambiente.id, bloque).length > 0">
                    <div 
                      v-for="(session, index) in getSessions(ambiente.id, bloque)" 
                      :key="index"
                      class="session-card compact-session"
                      :class="getDisciplineClass(session.discipline)"
                    >
                      <div v-if="session.timeSpan" class="session-time">
                        <font-awesome-icon :icon="['fas', 'clock']" /> {{ session.timeSpan }}
                      </div>
                      <div class="session-ficha" :title="session.ficha">
                        {{ session.ficha }}
                      </div>
                      <div class="session-instructor" :title="session.instructor">
                        <font-awesome-icon :icon="['fas', 'chalkboard-user']" />
                        Inst. {{ session.instructor }}
                      </div>
                    </div>
                  </template>
                  <div v-else class="empty-cell">
                    Libre
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal de Sedes -->
    <div class="modal-overlay" v-if="showModalSedes" @click.self="showModalSedes = false">
      <div class="modal-content">
        <button class="modal-close" @click="showModalSedes = false">
          <font-awesome-icon :icon="['fas', 'xmark']" />
        </button>
        <div class="sedes-grid">
          <!-- Card 1 -->
          <div class="sede-card">
            <div class="sede-img-placeholder">
              <img src="@/image/SedePrincipal.png" alt="Sede Principal">
            </div>
            <div class="sede-info">
              <span class="sede-type">SEDE PRINCIPAL</span>
              <h3 class="sede-title">Centro Agroforestal y Acuicola Arapaima</h3>
              <p class="sede-location">Puerto Asis</p>
              <span class="sede-branches">3 Sucursales</span>
            </div>
          </div>
          <!-- Card 2 -->
          <div class="sede-card">
            <div class="sede-img-placeholder">
              <img src="@/image/SedeOrito.png" alt="Sede Orito">
            </div>
            <div class="sede-info">
              <span class="sede-type">SUBSEDE</span>
              <h3 class="sede-title">Sede Orito</h3>
              <p class="sede-location">Orito</p>
              <span class="sede-branches">1 Sucursales</span>
            </div>
          </div>
          <!-- Card 3 -->
          <div class="sede-card">
            <div class="sede-img-placeholder">
              <img src="@/image/SedeLeguizamo.png" alt="Sede Puerto Leguizamo">
            </div>
            <div class="sede-info">
              <span class="sede-type">SUBSEDE</span>
              <h3 class="sede-title">Sede Puerto Leguizamo</h3>
              <p class="sede-location">Pto. Leguizamo</p>
              <span class="sede-branches">2 Sucursales</span>
            </div>
          </div>
          <!-- Card 4 -->
          <div class="sede-card">
            <div class="sede-img-placeholder">
              <img src="@/image/SedeMocoa.png" alt="Sede Maguaré">
            </div>
            <div class="sede-info">
              <span class="sede-type">SUBSEDE</span>
              <h3 class="sede-title">Sede Maguaré<br>(Edificio Maguaré)</h3>
              <p class="sede-location">Mocoa</p>
              <span class="sede-branches">1 Sucursales</span>
            </div>
          </div>
          <!-- Card 5 (Centered) -->
          <div class="sede-card centered-card">
            <div class="sede-img-placeholder">
              <img src="@/image/SedeSibundoy.png" alt="Sede Machindinoy">
            </div>
            <div class="sede-info">
              <span class="sede-type">SUBSEDE</span>
              <h3 class="sede-title">Sede Machindinoy</h3>
              <p class="sede-location">Sibundoy</p>
              <span class="sede-branches">2 Sucursales</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useProgramacionStore } from '@/stores/programacion';
import { useConfigStore } from '@/stores/config';

const route = useRoute();
const store = useProgramacionStore();

const currentDate = ref(new Date().toISOString().split('T')[0]);
const searchQuery = ref('');
const selectedSede = ref('caaa');
const isLoading = ref(true);
const error = ref(null);
const showModalSedes = ref(false);

const configStore = useConfigStore();

// Los bloques horarios se calculan dinámicamente desde la configuración global
const bloques = computed(() => configStore.bloquesHorarios);

// Estado para almacenar los datos que vendrán de la API
const ambientes = computed(() => store.ambientes);
const schedule = computed(() => store.schedule);

// Función para obtener la lista de ambientes desde el backend
const fetchAmbientes = async () => {
  // Ahora manejado por el store
};

// Función para obtener la programación desde el backend
const fetchSchedule = async () => {
  isLoading.value = false;
};

onMounted(async () => {
  store.initStore();
  
  if (route.query.q) {
    searchQuery.value = route.query.q;
  }
  
  await fetchAmbientes();
  await fetchSchedule();
});

watch(currentDate, () => {
  fetchSchedule();
});

watch(selectedSede, () => {
  fetchAmbientes(); // Asumiendo que los ambientes cambian por sede
  fetchSchedule();
});

const filteredSchedule = computed(() => {
  if (!searchQuery.value) return schedule.value;
  const q = searchQuery.value.toLowerCase();
  return schedule.value.filter(s => 
    (s.instructor && s.instructor.toLowerCase().includes(q)) || 
    (s.ficha && s.ficha.toLowerCase().includes(q))
  );
});

const getSessions = (ambId, bloque) => {
  return filteredSchedule.value.filter(s => s.ambienteId === ambId && s.bloque === bloque);
};

const getDisciplineClass = (discipline) => {
  const map = {
    'software': 'card-software',
    'design': 'card-design',
    'hardware': 'card-hardware',
    'language': 'card-language',
  };
  return map[discipline] || 'card-default';
};
</script>

<style scoped>
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL
   ========================================================================== */
.admin-view-shell {
  font-family: var(--fuente-principal, 'Inter', sans-serif);
  min-height: 100vh;
  color: var(--texto-principal, #333);
  box-sizing: border-box;
  padding: 1.5rem;
  background-color: var(--fondo-app, #f1f3f5);
  max-width: 100%;
  overflow-x: hidden;
}

.dash-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas, #ffffff);
  padding: 1.5rem 2rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  border: 1px solid var(--borde, #dee2e6);
  border-left: 5px solid var(--sena-verde, #39A900);
}

.header-left {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.environment-badge h1 {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: -0.5px;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.95rem;
  color: var(--texto-secundario);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  text-align: right;
}

.user-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--sena-azul-oscuro);
}

.user-status {
  font-size: 0.85rem;
  color: var(--sena-verde);
  font-weight: 700;
}

.user-avatar {
  font-size: 2.8rem;
  color: #000;
}

/* Barra de herramientas */
.toolbar-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-info-sedes {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-info-sedes:hover {
  background-color: #c3e6cb;
}

.date-picker-wrapper, .search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.date-picker-wrapper .input-icon, .search-wrapper .search-icon {
  position: absolute;
  color: #6c757d;
  pointer-events: none;
}

.date-picker-wrapper .input-icon {
  right: 12px;
}

.date-picker-wrapper input[type="date"]::-webkit-calendar-picker-indicator {
  opacity: 0;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  cursor: pointer;
}

.search-wrapper .search-icon {
  left: 12px;
}

.search-wrapper input {
  padding-left: 36px !important;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 0.6rem 1rem;
  color: var(--texto-secundario);
  font-family: inherit;
  font-size: 0.95rem;
  outline: none;
  min-height: 40px;
  font-weight: 500;
}

.select-filter {
  min-width: 160px;
  cursor: pointer;
}

.date-filter {
  width: 140px;
}

.dash-grid {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
}

.module-card {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--borde);
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.module-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

/* Matrix Estilos Específicos */
.matrix-wrapper {
  width: 100%;
  max-height: 550px;
  overflow-x: auto;
  overflow-y: auto;
  border: 1px solid var(--borde);
  border-radius: 12px;
}

.grid-matrix {
  display: grid;
  /* El grid-template-columns se maneja de forma dinámica en el HTML */
  min-width: fit-content;
}

.matrix-cell {
  background-color: var(--fondo-tarjetas);
  border-right: 1px solid var(--borde);
  border-bottom: 1px solid var(--borde);
}

.header-cell {
  background-color: var(--fondo-tarjetas);
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 55px;
  position: sticky;
  top: 0;
  z-index: 2;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

.corner-cell {
  font-size: 1.05rem;
  color: var(--texto-secundario);
  text-transform: uppercase;
  position: sticky;
  left: 0;
  top: 0;
  z-index: 3;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.03);
}

.time-cell {
  font-size: 0.85rem;
  color: var(--sena-verde, #1e7e34);
}

.time-icon {
  margin-right: 8px;
}

.room-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background-color: var(--fondo-app);
  position: sticky;
  left: 0;
  z-index: 1;
  box-shadow: 2px 0 5px rgba(0,0,0,0.03);
}

.room-name {
  color: var(--sena-azul-oscuro);
  font-size: 1.1rem;
  text-align: center;
  font-weight: 800;
}

.room-capacity {
  font-size: 0.9rem;
  color: var(--texto-secundario);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.data-cell {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* Allow vertical scroll if many sessions overlap in one cell */
  overflow-y: auto;
}

.session-card {
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.compact-session {
  height: auto;
  min-height: min-content;
}

.session-time {
  font-size: 0.75rem;
  font-weight: 800;
  margin-bottom: 4px;
  opacity: 0.85;
}

.session-ficha {
  font-weight: 800;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.session-instructor {
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-cell {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #adb5bd;
  font-style: italic;
  font-size: 0.95rem;
  font-weight: 500;
}

/* Discipline Colors */
/* Green */
.card-software {
  background-color: #e8f5e9;
  border: 1px solid #c8e6c9;
  border-left: 5px solid #4caf50;
  color: #2e7d32;
}
/* Purple */
.card-design {
  background-color: #f3e5f5;
  border: 1px solid #e1bee7;
  border-left: 5px solid #ab47bc;
  color: #6a1b9a;
}
/* Blue */
.card-hardware {
  background-color: #e1f5fe;
  border: 1px solid #b3e5fc;
  border-left: 5px solid #29b6f6;
  color: #0277bd;
}
/* Yellow */
.card-language {
  background-color: #fff8e1;
  border: 1px solid #ffecb3;
  border-left: 5px solid #ffca28;
  color: #f57f17;
}

/* ==========================================================================
   MODAL DE SEDES
   ========================================================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: transparent;
  padding: 2rem;
  width: 90%;
  max-width: 900px;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 0;
  right: 0;
  background: white;
  border: 1px solid var(--borde, #dee2e6);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  color: #333;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sedes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  justify-content: center;
}

.sede-card {
  display: flex;
  background: #ffffff;
  border-radius: 12px;
  border: 2px solid var(--sena-verde, #39A900);
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(57, 169, 0, 0.15);
  height: 160px;
}

.centered-card {
  grid-column: 1 / -1;
  width: 50%;
  margin: 0 auto;
}

.sede-img-placeholder {
  width: 40%;
  background-color: #e9ecef;
  border-right: 2px solid var(--sena-verde, #39A900);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.placeholder-text {
  color: #adb5bd;
  font-size: 0.85rem;
  font-style: italic;
}

.sede-img-placeholder img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sede-info {
  width: 60%;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  background: linear-gradient(to right, #ffffff, #fdfdfd);
}

.sede-type {
  color: var(--sena-verde, #39A900);
  font-weight: 900;
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.sede-title {
  color: var(--sena-azul-oscuro);
  font-weight: 800;
  font-size: 1.05rem;
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.sede-location {
  color: var(--texto-secundario);
  font-weight: 700;
  font-size: 0.9rem;
  margin: 0 0 12px 0;
}

.sede-branches {
  color: var(--texto-secundario);
  font-size: 0.8rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .sedes-grid {
    grid-template-columns: 1fr;
  }
  .centered-card {
    width: 100%;
  }
}

@media (max-width: 992px) {
  .dash-header, .toolbar-section {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  .header-left, .header-right {
    justify-content: center;
    margin-bottom: 1rem;
  }
  .toolbar-left, .toolbar-right {
    flex-direction: column;
    width: 100%;
  }
  .btn-info-sedes, .select-filter, .form-input, .date-picker-wrapper, .search-wrapper {
    width: 100%;
  }
}
</style>
