<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-top">
        <div class="title-section">
          <h1>GESTION DE APRENDICES</h1>
          <p class="subtitle">Listado, asignación IoT y novedades</p>
        </div>
        <div class="user-profile">
          <div class="user-info">
            <span class="user-name">Nelson Contreras</span>
            <span class="user-status">En línea</span>
          </div>
          <div class="user-avatar">
            <font-awesome-icon icon="fa-solid fa-circle-user" class="avatar-icon" />
          </div>
        </div>
      </div>
      <div class="header-bottom">
        <div class="action-buttons">
          <button class="btn-primary" @click="openNuevoAprendizModal">
            <span>+ Nuevo Aprendiz</span>
          </button>
          <button class="btn-outline" @click="showVincularModal = true">
            <font-awesome-icon icon="fa-solid fa-cloud-arrow-up" /> 
            <span>Importar Aprendices</span>
          </button>
          <button class="btn-outline" @click="exportarExcel">
            <font-awesome-icon icon="fa-solid fa-download" /> 
            <span>Exportar</span>
          </button>
        </div>
      </div>
    </header>

    <main class="dash-grid">
      <!-- Stats Cards -->
      <section class="stats-cards">
        <div class="stat-card green-card">
          <div class="stat-icon-wrapper">
            <font-awesome-icon icon="fa-solid fa-user-group" />
          </div>
          <div class="stat-content">
            <h3>Aprendices Matriculados</h3>
            <div class="stat-value">150</div>
            <div class="stat-meta green-text"><span>+20</span> este mes</div>
          </div>
        </div>
        <div class="stat-card blue-card">
          <div class="stat-icon-wrapper">
            <font-awesome-icon icon="fa-solid fa-microchip" />
          </div>
          <div class="stat-content">
            <h3>Dispositivo IoT</h3>
            <div class="stat-value">80</div>
            <div class="stat-meta">Conectados <span class="dot green-dot"></span></div>
          </div>
        </div>
        <div class="stat-card yellow-card">
          <div class="stat-icon-wrapper">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
          </div>
          <div class="stat-content">
            <h3>Pendientes De Asignar</h3>
            <div class="stat-value">22</div>
            <div class="stat-meta">Por Asignar <span class="dot yellow-dot"></span></div>
          </div>
        </div>
        <div class="stat-card purple-card">
          <div class="stat-icon-wrapper">
            <font-awesome-icon icon="fa-solid fa-chart-column" />
          </div>
          <div class="stat-content">
            <h3>Estado del Sitema</h3>
            <div class="stat-value">80%</div>
            <div class="stat-meta">Operatividad <span class="dot green-dot"></span></div>
          </div>
        </div>
      </section>

      <!-- Table Section -->
      <section class="module-card table-card">
        <div class="filters-row">
          <div class="search-box">
            <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
            <input type="text" v-model="searchQuery" placeholder="Buscar por Nombre, Documento..." />
          </div>
          <select class="form-select" v-model="selectedFicha">
            <option value="">Todos las Fichas</option>
            <option value="2693821">2693821</option>
            <option value="2693822">2693822</option>
          </select>
          <select class="form-select" v-model="selectedDevice">
            <option value="">Todos los Dispositivos</option>
            <option value="assigned">Asignados</option>
            <option value="unassigned">Sin Asignar</option>
          </select>
          <select class="form-select" v-model="selectedState">
            <option value="">Todos los Estados</option>
            <option value="vinculado">Vinculado</option>
            <option value="pendiente">Pendiente</option>
          </select>
        </div>

        <div class="table-responsive-wrapper">
          <table class="modern-table">
            <thead>
              <tr>
                <th>APRENDIZ</th>
                <th>FICHA</th>
                <th>IDENTIFICACIÓN DEL DISPOSITIVO (NFC/IOT)</th>
                <th>ESTADO</th>
                <th>ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="5" class="text-center py-4" style="text-align: center; padding: 2rem;">Cargando aprendices...</td>
              </tr>
              <tr v-else-if="aprendices.length === 0">
                <td colspan="5" class="text-center py-4" style="text-align: center; padding: 2rem;">No se encontraron resultados</td>
              </tr>
              <tr v-else v-for="aprendiz in aprendices" :key="aprendiz.documento">
                <td>
                  <div class="user-cell">
                    <img :src="aprendiz.avatar" alt="Avatar" class="user-avatar-img" />
                    <div class="user-details">
                      <strong>{{ aprendiz.nombre }}</strong>
                      <span>{{ aprendiz.documento }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="ficha-badge">{{ aprendiz.ficha }}</span>
                </td>
                <td>
                  <div v-if="aprendiz.deviceId" class="device-cell">
                    <strong>{{ aprendiz.deviceId }}</strong>
                    <span>Asignado el {{ aprendiz.assignDate }}</span>
                  </div>
                  <div v-else>
                    <span class="unassigned-badge">SIN ASIGNAR</span>
                  </div>
                </td>
                <td>
                  <span v-if="aprendiz.deviceId" class="status-badge status-vinculado">
                    <font-awesome-icon icon="fa-solid fa-check-circle" /> Vinculado
                  </span>
                  <span v-else class="status-badge status-pendiente">
                    <font-awesome-icon icon="fa-solid fa-clock" /> Pendiente
                  </span>
                </td>
                <td>
                  <div class="actions-cell">
                    <button class="btn-icon" title="Ver" @click="openPerfilModal(aprendiz)">
                      <font-awesome-icon icon="fa-solid fa-eye" />
                    </button>
                    <button class="btn-icon" title="Editar" @click="openAssignModal(aprendiz)">
                      <font-awesome-icon icon="fa-solid fa-pen-to-square" />
                    </button>
                    <button class="btn-icon" title="Eliminar" @click="openDeleteModal(aprendiz)">
                      <font-awesome-icon icon="fa-solid fa-trash-can" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-row">
          <div class="pagination-info">Mostrando {{ paginationStart }} a {{ paginationEnd }} de {{ totalItems }} Aprendices</div>
          <div class="pagination-controls">
            <button class="page-btn" @click="prevPage" :disabled="currentPage === 1"><font-awesome-icon icon="fa-solid fa-chevron-left" /></button>
            
            <button 
              v-for="page in visiblePages" 
              :key="page" 
              class="page-btn" 
              :class="{ active: currentPage === page }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
            
            <button class="page-btn" @click="nextPage" :disabled="currentPage === totalPages"><font-awesome-icon icon="fa-solid fa-chevron-right" /></button>
          </div>
          <div class="pagination-size">
            Mostrar 
            <select class="size-select" v-model="itemsPerPage">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="15">15</option>
              <option :value="30">30</option>
            </select>
          </div>
        </div>
      </section>
    </main>

    <!-- Modals -->
    <!-- Modal de Edición Completa -->
    <ModalEditarAprendiz
      :show="showAssignModal"
      :aprendizData="selectedAprendiz"
      @update:show="showAssignModal = $event"
      @close="showAssignModal = false"
      @save="handleEditAprendizSave"
    />

    <ModalConfirmAction 
      :show="showDeleteModal"
      :message="`¿Estás seguro de eliminar por completo al aprendiz ${selectedAprendiz?.nombre}? Esta acción no se puede deshacer.`"
      @update:show="showDeleteModal = $event"
      @close="showDeleteModal = false"
      @confirm="handleDeleteAprendiz"
    />

    <ModalVincularAprendices
      :show="showVincularModal"
      @update:show="showVincularModal = $event"
      @close="showVincularModal = false"
      @save="handleVincularSave"
    />

    <ModalFormAprendiz
      :show="showNuevoAprendizModal"
      @update:show="showNuevoAprendizModal = $event"
      @close="showNuevoAprendizModal = false"
      @save="handleNuevoAprendizSave"
    />

    <ModalPerfilAprendiz
      :show="showPerfilModal"
      :aprendiz="selectedAprendiz"
      @update:show="showPerfilModal = $event"
      @close="showPerfilModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import ModalConfirmAction from '@/components/admin/modals/ModalConfirmAction.vue';
import ModalVincularAprendices from '@/components/admin/modals/ModalVincularAprendices.vue';
import ModalFormAprendiz from '@/components/admin/modals/ModalFormAprendiz.vue';
import ModalPerfilAprendiz from '@/components/admin/modals/ModalPerfilAprendiz.vue';
import ModalEditarAprendiz from '@/components/admin/modals/ModalEditarAprendiz.vue';
import { useToast } from 'vue-toastification';

const toast = useToast();

// --- Estados Dinámicos ---
const aprendices = ref([]);
const loading = ref(false);

// Filtros
const searchQuery = ref('');
const selectedFicha = ref('');
const selectedDevice = ref('');
const selectedState = ref('');

// Paginación
const currentPage = ref(1);
const itemsPerPage = ref(15);
const totalItems = ref(0);

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / itemsPerPage.value)));

const paginationStart = computed(() => (totalItems.value === 0) ? 0 : (currentPage.value - 1) * itemsPerPage.value + 1);
const paginationEnd = computed(() => {
  const end = currentPage.value * itemsPerPage.value;
  return end > totalItems.value ? totalItems.value : end;
});

// Calculo de paginación visible (simple)
const visiblePages = computed(() => {
  const pages = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
});

// Modales
const showAssignModal = ref(false);
const showConfirmModal = ref(false);
const showDeleteModal = ref(false);
const showVincularModal = ref(false);
const showNuevoAprendizModal = ref(false);
const showPerfilModal = ref(false);
const selectedAprendiz = ref(null);

// --- Inicializar LocalStorage ---
const initLocalStorage = () => {
  if (!localStorage.getItem('mock_aprendices')) {
    const mockDatabase = [
      { documento: '1001234567', nombre: 'Andres Felipe Gomez', ficha: '2693821', deviceId: 'A1:B2:C3:D4:E5', assignDate: '17/06/2026', telefono: '3158709236', correo: 'andres.gomez@misena.edu.co', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Andres' },
      { documento: '1007654321', nombre: 'María Paula Ramírez', ficha: '2693821', deviceId: 'F6:G7:H8:I9:J0', assignDate: '17/06/2026', telefono: '3124567890', correo: 'maria.ramirez@misena.edu.co', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Maria' },
      { documento: '1023456789', nombre: 'Carlos Eduardo López', ficha: '2693821', deviceId: null, telefono: '3109876543', correo: 'carlos.lopez@misena.edu.co', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos' },
      { documento: '1054321987', nombre: 'Laura Valentina Sánchez', ficha: '2693821', deviceId: 'K1:L2:M3:N4:O5', assignDate: '17/06/2026', telefono: '3201234567', correo: 'laura.sanchez@misena.edu.co', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Laura' },
      { documento: '1098765432', nombre: 'Julián David Castro', ficha: '2693821', deviceId: null, telefono: '3145678901', correo: 'julian.castro@misena.edu.co', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Julian' }
    ];
    localStorage.setItem('mock_aprendices', JSON.stringify(mockDatabase));
  }
};

// --- Funciones del Backend (Mocks con LocalStorage) ---
const fetchAprendices = async () => {
  loading.value = true;
  
  try {
    // Simulamos un delay de red
    await new Promise(resolve => setTimeout(resolve, 300));

    const allData = JSON.parse(localStorage.getItem('mock_aprendices') || '[]');
    let filteredData = [...allData];
    
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      filteredData = filteredData.filter(a => a.nombre.toLowerCase().includes(q) || a.documento.includes(q) || a.ficha.includes(q));
    }
    if (selectedFicha.value) {
      filteredData = filteredData.filter(a => a.ficha === selectedFicha.value);
    }
    if (selectedDevice.value) {
      filteredData = filteredData.filter(a => selectedDevice.value === 'assigned' ? a.deviceId !== null : a.deviceId === null);
    }
    
    totalItems.value = filteredData.length;
    
    // Paginación Manual
    const startIdx = (currentPage.value - 1) * itemsPerPage.value;
    const endIdx = startIdx + itemsPerPage.value;
    aprendices.value = filteredData.slice(startIdx, endIdx);

  } catch (error) {
    console.error("Error cargando aprendices:", error);
    toast.error("Ocurrió un error obteniendo los datos");
  } finally {
    loading.value = false;
  }
};

// --- Watchers ---
watch([searchQuery, selectedFicha, selectedDevice, selectedState, itemsPerPage], () => {
  currentPage.value = 1;
  fetchAprendices();
});

watch(currentPage, () => {
  fetchAprendices();
});

// --- Ciclo de Vida ---
onMounted(() => {
  initLocalStorage();
  fetchAprendices();
});

// --- Métodos UI de Acciones Principales ---
const openNuevoAprendizModal = () => {
  showNuevoAprendizModal.value = true;
};

const handleNuevoAprendizSave = (payload) => {
  const newAprendiz = {
    documento: payload.documento,
    nombre: `${payload.nombres} ${payload.apellidos}`,
    ficha: payload.ficha,
    correo: payload.correo,
    telefono: '3000000000', // Mock fallback
    deviceId: null,
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${payload.nombres}`
  };

  const allData = JSON.parse(localStorage.getItem('mock_aprendices') || '[]');
  allData.unshift(newAprendiz); // Agregamos al inicio
  localStorage.setItem('mock_aprendices', JSON.stringify(allData));

  showNuevoAprendizModal.value = false;
  toast.success("Aprendiz registrado exitosamente.");
  fetchAprendices(); // Refrescar lista
};

const exportarExcel = () => {
  toast.info("Iniciando exportación de aprendices...");
};

const handleVincularSave = (payload) => {
  showVincularModal.value = false;
  toast.success("Proceso de importación exitoso.");
  fetchAprendices(); // Refrescar lista
};

// --- Métodos de la Tabla ---
const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const openPerfilModal = (aprendiz) => {
  selectedAprendiz.value = aprendiz;
  showPerfilModal.value = true;
};

const openAssignModal = (aprendiz) => {
  selectedAprendiz.value = aprendiz;
  showAssignModal.value = true;
};

const openDeleteModal = (aprendiz) => {
  selectedAprendiz.value = aprendiz;
  showDeleteModal.value = true;
};

const handleDeleteAprendiz = () => {
  if (selectedAprendiz.value) {
    let allData = JSON.parse(localStorage.getItem('mock_aprendices') || '[]');
    allData = allData.filter(a => a.documento !== selectedAprendiz.value.documento);
    localStorage.setItem('mock_aprendices', JSON.stringify(allData));

    toast.success(`El aprendiz ha sido eliminado.`);
    showDeleteModal.value = false;
    fetchAprendices();
  }
};

const handleEditAprendizSave = (payload) => {
  let allData = JSON.parse(localStorage.getItem('mock_aprendices') || '[]');
  const index = allData.findIndex(a => a.documento === payload.documento);
  
  if (index !== -1) {
    allData[index] = {
      ...allData[index],
      nombre: payload.nombre,
      correo: payload.correo,
      telefono: payload.telefono,
      instructor: payload.instructor,
      ambiente: payload.ambiente,
      deviceId: payload.deviceId,
      assignDate: payload.assignDate
    };
    
    localStorage.setItem('mock_aprendices', JSON.stringify(allData));
    toast.success("Información del aprendiz actualizada exitosamente.");
    showAssignModal.value = false;
    fetchAprendices();
  }
};
</script>

<style scoped>
.admin-view-shell {
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
  box-sizing: border-box;
  padding: 0 1rem 2rem 1rem;
}

.dash-header {
  background: var(--fondo-tarjetas);
  padding: 1.5rem 2rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px var(--sombra-suave, rgba(0,0,0,0.03));
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.title-section h1 {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  text-transform: uppercase;
}

.subtitle {
  color: var(--texto-secundario);
  font-size: 0.95rem;
  margin: 4px 0 0 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
  text-align: right;
}

.user-name {
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  font-size: 1.1rem;
}

.user-status {
  font-size: 0.8rem;
  color: var(--sena-verde);
  font-weight: 600;
}

.avatar-icon {
  font-size: 2.8rem;
  color: var(--sena-azul-oscuro);
}

.header-bottom {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  margin-top: -10px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--sena-verde);
  color: var(--sena-blanco, white);
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--sena-verde-oscuro);
}

.btn-outline {
  background: var(--fondo-tarjetas);
  color: var(--texto-secundario);
  border: 1px solid var(--borde);
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: var(--fondo-app);
  color: var(--texto-principal);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--fondo-tarjetas);
  border-radius: 16px;
  padding: 1rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  box-shadow: 0 2px 10px var(--sombra-suave, rgba(0,0,0,0.03));
  border: 1px solid var(--borde);
}

.green-card .stat-icon-wrapper {
  background: var(--fondo-app);
  color: var(--sena-verde);
  border: 1px solid var(--borde);
}

.blue-card .stat-icon-wrapper {
  background: var(--fondo-app);
  color: var(--sena-azul-oscuro);
  border: 1px solid var(--borde);
}

.yellow-card .stat-icon-wrapper {
  background: var(--fondo-app);
  color: var(--sena-amarillo);
  border: 1px solid var(--borde);
}

.purple-card .stat-icon-wrapper {
  background: var(--fondo-app);
  color: var(--sena-violeta);
  border: 1px solid var(--borde);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-content h3 {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-principal);
  margin: 0 0 2px 0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-meta {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
}

.green-text {
  color: var(--texto-secundario);
}

.green-text span {
  color: var(--sena-verde);
  font-weight: 700;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.green-dot { background: var(--sena-verde); }
.yellow-dot { background: var(--sena-amarillo, #fdc300); }

.table-card {
  background: var(--fondo-tarjetas);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px var(--sombra-suave, rgba(0,0,0,0.03));
}

.filters-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
}

.search-box input {
  width: 100%;
  padding: 0.7rem 1rem 0.7rem 2.8rem;
  border: 1px solid var(--borde);
  border-radius: 8px;
  font-size: 0.9rem;
  background: var(--fondo-app);
  box-sizing: border-box;
  color: var(--texto-principal);
}

.search-box input:focus {
  outline: none;
  border-color: var(--sena-verde);
}

.form-select {
  padding: 0.7rem 2.5rem 0.7rem 1.2rem;
  border: 1px solid var(--borde);
  border-radius: 8px;
  font-size: 0.9rem;
  background-color: var(--fondo-app);
  color: var(--texto-principal);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
  min-width: 180px;
}

.form-select:focus {
  outline: none;
  border-color: var(--sena-verde);
}

.table-responsive-wrapper {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}

.modern-table th {
  text-align: left;
  padding: 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  border-bottom: 2px solid var(--fondo-app);
  text-transform: uppercase;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--fondo-app);
  vertical-align: middle;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--borde);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-details strong {
  font-size: 0.95rem;
  color: var(--texto-principal);
}

.user-details span {
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.ficha-badge {
  background: var(--fondo-app);
  color: var(--texto-secundario);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
  border: 1px solid var(--borde);
}

.device-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.device-cell strong {
  font-size: 0.95rem;
  color: var(--texto-principal);
}

.device-cell span {
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

.unassigned-badge {
  background: var(--fondo-app);
  color: var(--texto-secundario);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.8rem;
  border: 1px solid var(--borde);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}

.status-vinculado {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
}

.status-pendiente {
  background: rgba(253, 195, 0, 0.1);
  color: var(--sena-amarillo);
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--borde);
  color: var(--sena-azul-oscuro);
}

.pagination-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  font-size: 0.85rem;
  color: var(--texto-secundario);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--fondo-app);
  border-radius: 6px;
  color: var(--texto-principal);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.page-btn:hover:not(.active) {
  background: var(--borde);
}

.page-btn.active {
  background: var(--sena-verde);
  color: var(--sena-blanco, white);
}

.page-dots {
  padding: 0 4px;
}

.pagination-size {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-select {
  padding: 0.4rem 2rem 0.4rem 0.8rem;
  border: 1px solid var(--borde);
  border-radius: 6px;
  background-color: var(--fondo-app);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
  color: var(--texto-principal);
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-top, .header-bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .user-profile {
    width: 100%;
    justify-content: space-between;
  }
  
  .action-buttons {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .btn-primary, .btn-outline {
    flex: 1;
    justify-content: center;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .filters-row {
    flex-direction: column;
  }
  
  .pagination-row {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
