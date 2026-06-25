<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>GESTIÓN DE FICHAS</h1>
          <p class="header-meta">
            Sede Principal Puerto Asís | 03:15:50 PM
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-action" @click="openNewFichaModal">
          <font-awesome-icon icon="fa-solid fa-plus" />
          <span>NUEVA FICHA</span>
        </button>
      </div>
    </header>

    <main class="dash-grid">
      <section class="dash-col">
        <div class="module-card table-card">
          <div class="table-toolbar">
            <h2 class="module-title">
              <font-awesome-icon icon="fa-solid fa-clipboard-list" /> DIRECTORIO DE FICHAS
            </h2>
            <div class="filters-group">
              <div class="search-box">
                <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
                <input type="text" class="form-input search-input" placeholder="Buscar por código o nombre..." />
              </div>
              <select class="form-input select-filter">
                <option value="">Todos los Estados</option>
                <option value="active">En Lectiva</option>
                <option value="inactive">Terminada</option>
              </select>
            </div>
          </div>

          <div class="table-responsive-wrapper">
            <table class="apprentices-table">
              <thead>
                <tr>
                  <th>CÓDIGO</th>
                  <th>PROGRAMA DE FORMACIÓN</th>
                  <th class="text-center">FECHA INICIO</th>
                  <th class="text-center">FECHA FINAL</th>
                  <th class="text-center">ESTADO</th>
                  <th class="text-center">ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ficha in fichas" :key="ficha.code + Math.random()">
                  <td>
                    <strong class="col-code">{{ ficha.code }}</strong>
                  </td>
                  <td>
                    <div class="program-info">
                      <span class="program-name">{{ ficha.name }}</span>
                      <span class="program-level">{{ ficha.level }}</span>
                      <div class="progress-container">
                        <div class="progress-bar">
                          <div 
                            class="progress-fill" 
                            :class="getProgressClass(ficha.status)"
                            :style="{ width: ficha.progress + '%' }"
                          ></div>
                        </div>
                        <span class="progress-text">{{ ficha.progress }}%</span>
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <span class="time-cell">{{ ficha.startDate }}</span>
                  </td>
                  <td class="text-center">
                    <span class="time-cell">{{ ficha.endDate }}</span>
                  </td>
                  <td class="text-center">
                    <span :class="['status-badge', getStatusClass(ficha.status)]">
                      <font-awesome-icon :icon="getStatusIcon(ficha.status)" class="mr-1" />
                      {{ ficha.status }}
                    </span>
                  </td>
                  <td>
                    <div class="actions-cell">
                      <button class="btn-table action-view" title="Vincular Aprendices" @click="openVincularModal(ficha)">
                        <font-awesome-icon icon="fa-solid fa-user-plus" />
                      </button>
                      <button class="btn-table action-chart" title="Editar" @click="openEditFichaModal(ficha)">
                        <font-awesome-icon icon="fa-solid fa-pen-to-square" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Form Ficha -->
    <ModalFormFicha 
      :show="showFichaModal" 
      :fichaData="selectedFicha"
      @update:show="showFichaModal = $event"
      @close="showFichaModal = false"
      @save="handleSaveFicha"
    />

    <!-- Modal Vincular Aprendices -->
    <ModalVincularAprendices
      :show="showVincularModal"
      :fichaData="selectedFichaParaVincular"
      @update:show="showVincularModal = $event"
      @close="showVincularModal = false"
      @save="handleSaveVincular"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import ModalFormFicha from '@/components/admin/modals/ModalFormFicha.vue';
import ModalVincularAprendices from '@/components/admin/modals/ModalVincularAprendices.vue';

const router = useRouter();

// Mock Data
const fichas = reactive([
  { code: '2693821', name: 'Análisis y Desarrollo de Software (ADSO)', level: 'Tecnólogo', progress: 60, startDate: '15/01/2024', endDate: '15/07/2025', status: 'Lectiva' },
  { code: '2693822', name: 'Producción Multimedia', level: 'Técnico', progress: 85, startDate: '01/02/2024', endDate: '01/08/2025', status: 'Practicas' },
  { code: '2589001', name: 'Gestión Admminstrativa', level: 'Complementario', progress: 100, startDate: '10/10/2022', endDate: '10/04/2024', status: 'Terminada' },
  { code: '2693821', name: 'Análisis y Desarrollo de Software (ADSO)', level: 'Tecnólogo', progress: 60, startDate: '15/01/2024', endDate: '15/07/2025', status: 'Lectiva' },
  { code: '2693822', name: 'Producción Multimedia', level: 'Técnico', progress: 85, startDate: '01/02/2024', endDate: '01/08/2025', status: 'Practicas' },
  { code: '2589001', name: 'Gestión Admminstrativa', level: 'Complementario', progress: 100, startDate: '10/10/2022', endDate: '10/04/2024', status: 'Terminada' }
]);

const getStatusClass = (status) => {
  if (status === 'Lectiva') return 'status-green';
  if (status === 'Practicas') return 'status-yellow';
  if (status === 'Terminada') return 'status-red';
  return 'status-gray';
};

const getStatusIcon = (status) => {
  if (status === 'Lectiva') return ['fas', 'check-circle'];
  if (status === 'Practicas') return ['fas', 'user-graduate'];
  if (status === 'Terminada') return ['fas', 'graduation-cap'];
  return ['fas', 'circle'];
};

const getProgressClass = (status) => {
  if (status === 'Lectiva') return 'progress-green';
  if (status === 'Practicas') return 'progress-yellow';
  if (status === 'Terminada') return 'progress-red';
  return '';
};

const showFichaModal = ref(false);
const selectedFicha = ref(null);

const showVincularModal = ref(false);
const selectedFichaParaVincular = ref(null);

const openNewFichaModal = () => {
  selectedFicha.value = null;
  showFichaModal.value = true;
};

const openEditFichaModal = (ficha) => {
  selectedFicha.value = { ...ficha };
  showFichaModal.value = true;
};

const openVincularModal = (ficha) => {
  selectedFichaParaVincular.value = { ...ficha };
  showVincularModal.value = true;
};

const handleSaveFicha = (data) => {
  if (selectedFicha.value) {
    // Editar
    const index = fichas.findIndex(f => f.code === selectedFicha.value.code);
    if (index !== -1) fichas[index] = data;
  } else {
    // Nueva
    fichas.push(data);
  }
};

const handleSaveVincular = (payload) => {
  console.log('Datos a vincular recibidos:', payload);
  // Aquí puedes enviar los datos al backend usando axios, fetch, etc.
  // Ejemplo: await vincularAprendices(payload);
  alert('Datos recibidos. Revisa la consola para ver el payload.');
};

const goToFichaDetails = (code) => {
  // Simulando redirección. En el futuro puede ser `/admin/fichas/${code}`
  router.push('/admin/dashboard');
};
</script>

<style scoped>
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL (SENA 2024)
   ========================================================================== */
.admin-view-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
  box-sizing: border-box;
}

.dash-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  border-left: 5px solid var(--sena-verde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
}

.header-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 2.5rem;
}

.environment-badge h1 {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.header-actions {
  display: flex;
  align-items: center;
}

.btn-action {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-action:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.3);
}

.dash-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dash-col {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-top: 4px solid var(--sena-verde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.module-title {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.filters-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
  font-size: 0.9rem;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.65rem 1rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input {
  width: 100%;
  padding-left: 2.2rem;
  box-sizing: border-box;
}

.select-filter {
  min-width: 160px;
  cursor: pointer;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

/* Tablas (Estilo DashboardInstru) */
.table-responsive-wrapper {
  overflow-x: auto;
}

.apprentices-table {
  width: 100%;
  border-collapse: collapse;
}

.apprentices-table th {
  text-align: left;
  padding: 1rem;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-secundario);
  border-bottom: 2px solid var(--fondo-app);
  letter-spacing: 0.5px;
}

.apprentices-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--fondo-app);
  vertical-align: middle;
}

.apprentices-table tr:hover td {
  background: rgba(0, 48, 64, 0.02);
}

.table-user-info {
  display: flex;
  flex-direction: column;
}

.table-user-info strong {
  font-size: 0.9rem;
  color: var(--texto-principal);
  font-weight: 700;
}

.col-code {
  font-family: monospace;
  font-size: 1rem;
  color: var(--sena-azul-oscuro);
}

.time-cell {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--texto-principal);
  background: var(--fondo-app);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--borde);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.status-green {
  background: rgba(57, 169, 0, 0.15);
  color: var(--sena-verde-oscuro, #2e8b57);
}

.status-yellow {
  background: rgba(255, 193, 7, 0.2);
  color: #b08d00;
}

.status-red {
  background: rgba(244, 67, 54, 0.15);
  color: #d32f2f;
}

.status-gray {
  background: rgba(113, 39, 122, 0.1); /* Violeta Sena */
  color: var(--sena-violeta);
}

[data-theme="dark"] .status-gray { color: #ce93d8; }

.program-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.program-name {
  font-weight: 800;
  color: var(--sena-azul-oscuro, #00324b);
  font-size: 0.9rem;
}
.program-level {
  font-size: 0.8rem;
  color: var(--texto-secundario, #666);
}
.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--borde, #e0e0e0);
  border-radius: 4px;
  overflow: hidden;
  max-width: 200px;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}
.progress-green {
  background-color: var(--sena-verde, #39A900);
}
.progress-yellow {
  background: linear-gradient(90deg, var(--sena-verde, #39A900) 50%, #ffc107 100%);
}
.progress-red {
  background-color: #f44336;
}
.progress-text {
  font-size: 0.75rem;
  color: var(--texto-secundario, #666);
  font-weight: 700;
}

.text-center {
  text-align: center !important;
}

.mr-1 {
  margin-right: 4px;
}

.actions-cell {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.btn-table {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--texto-secundario);
}

.btn-table:hover {
  transform: translateY(-2px);
}

.action-view:hover {
  border-color: var(--sena-azul-claro);
  color: var(--sena-azul-oscuro);
  background: rgba(80, 229, 249, 0.1);
}

.action-chart:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.1);
}

@media (max-width: 992px) {
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  .header-left {
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  .header-actions {
    justify-content: center;
  }
  .btn-action {
    width: 100%;
    justify-content: center;
  }
  .filters-group {
    flex-direction: column;
    width: 100%;
  }
  .search-box, .select-filter, .search-input {
    width: 100%;
  }
}
</style>
