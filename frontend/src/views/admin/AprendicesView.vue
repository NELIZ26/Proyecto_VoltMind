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
            <div class="stat-value">{{ totalItems }}</div>
            <div class="stat-meta green-text">Total en la búsqueda actual</div>
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
          <!-- Ficha Search Box (Movido a la izquierda) -->
          <div class="search-box autocomplete-box">
            <font-awesome-icon icon="fa-solid fa-layer-group" class="search-icon" />
            <input 
              type="text" 
              v-model="selectedFicha" 
              placeholder="N° de Ficha"
              @focus="showFichaDropdown = true"
              @blur="hideFichaDropdown"
            />
            <ul v-if="showFichaDropdown && filteredFichasList.length > 0" class="autocomplete-dropdown">
              <li v-for="ficha in filteredFichasList" :key="ficha.id" @mousedown.prevent="selectFicha(ficha.codigo)">
                <strong>{{ ficha.codigo }}</strong> - {{ ficha.programa }}
              </li>
            </ul>
          </div>
          <!-- Aprendiz Search Box (Movido a la derecha) -->
          <div class="search-box">
            <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
            <input type="text" v-model="searchQuery" placeholder="Documento o nombre del aprendiz" />
          </div>
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

        <div class="table-container">
          <!-- Estado en Blanco si no hay búsqueda activa -->
          <div v-if="!hasActiveSearch" class="empty-state-search">
            <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="empty-icon" />
            <h3>Comienza tu búsqueda</h3>
            <p>Ingresa un número de ficha o el documento/nombre de un aprendiz para ver los resultados.</p>
          </div>

          <table v-else class="data-table">
            <thead>
              <tr>
                <th>APRENDIZ</th>
                <th>FICHA</th>
                <th>PROGRAMA</th>
                <th>JORNADA</th>
                <th>NFC/IOT</th>
                <th>RIESGO ABANDONO</th>
                <th>ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-4" style="text-align: center; padding: 2rem;">Cargando aprendices...</td>
              </tr>
              <tr v-else-if="aprendices.length === 0">
                <td colspan="7" class="text-center py-4" style="text-align: center; padding: 2rem;">No se encontraron resultados</td>
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
                  <span class="programa-badge">{{ aprendiz.programa }}</span>
                  <div class="instructor-subtext">Inst: {{ aprendiz.instructor }}</div>
                </td>
                <td>
                  <span class="jornada-badge" :class="getJornadaClass(aprendiz.jornada)">
                    <font-awesome-icon :icon="getJornadaIcon(aprendiz.jornada)" />
                    {{ aprendiz.jornada }}
                  </span>
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
                  <span v-if="aprendiz.faltas_consecutivas >= 3" class="status-badge status-riesgo-alto">
                    <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> Alerta Deserción
                  </span>
                  <span v-else class="status-badge status-riesgo-normal">
                    <font-awesome-icon icon="fa-solid fa-check-circle" /> Normal
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
import { tituladasService } from '@/services/tituladasService';
import { aprendicesService } from '@/services/aprendicesService';

const toast = useToast();

// --- Estados Dinámicos ---
const aprendices = ref([]);
const fichasList = ref([]);
const loading = ref(false);

// Filtros
const searchQuery = ref('');
const selectedFicha = ref('');
const selectedDevice = ref('');
const selectedState = ref('');

// Paginación
const currentPage = ref(1);
const itemsPerPage = ref(15);
const showFichaDropdown = ref(false);

const hideFichaDropdown = () => {
  showFichaDropdown.value = false;
};

const selectFicha = (codigo) => {
  selectedFicha.value = codigo;
  showFichaDropdown.value = false;
};

const filteredFichasList = computed(() => {
  if (!selectedFicha.value) return fichasList.value.slice(0, 50);
  const q = selectedFicha.value.toLowerCase();
  return fichasList.value.filter(f => f.codigo.includes(q) || f.programa.toLowerCase().includes(q)).slice(0, 50);
});

// Búsqueda inteligente
const hasValidFicha = computed(() => selectedFicha.value && selectedFicha.value.length >= 5);
const hasValidSearch = computed(() => searchQuery.value && searchQuery.value.length >= 3);
const hasActiveSearch = computed(() => hasValidFicha.value || hasValidSearch.value);

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

// --- Funciones del Backend ---
const fetchAprendices = async () => {
  if (!hasActiveSearch.value) {
    aprendices.value = [];
    totalItems.value = 0;
    return;
  }
  
  loading.value = true;
  
  try {
    let data = [];
    if (hasValidFicha.value) {
      data = await aprendicesService.obtenerAprendicesPorFicha(selectedFicha.value);
    } else if (hasValidSearch.value) {
      // Búsqueda global (requiere al menos 3 caracteres para no sobrecargar la BD)
      data = await aprendicesService.buscarAprendicesGlobal(searchQuery.value);
    }

    const allData = data.map(ap => ({
      documento: ap.documento,
      nombre: ap.nombre,
      ficha: ap.ficha,
      programa: ap.programa,
      jornada: ap.jornada || 'Sin Jornada',
      instructor: ap.instructor || 'No asignado',
      etapa: ap.etapa,
      correo: ap.correo,
      telefono: ap.telefono || 'N/A',
      faltas_totales: ap.faltas_totales || 0,
      faltas_consecutivas: ap.faltas_consecutivas || 0,
      deviceId: null,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${ap.nombre}`
    }));

    let filteredData = [...allData];
    
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      filteredData = filteredData.filter(a => (a.nombre && a.nombre.toLowerCase().includes(q)) || (a.documento && a.documento.includes(q)));
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
    toast.error("Error al cargar los aprendices de la ficha seleccionada.");
    aprendices.value = [];
    totalItems.value = 0;
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
onMounted(async () => {
  try {
    fichasList.value = await aprendicesService.obtenerFichasRapido();
  } catch (error) {
    console.error("Error al obtener fichas:", error);
    toast.error("Error al cargar la lista de fichas disponibles.");
  }
  fetchAprendices();
});

// --- Métodos UI de Acciones Principales ---
const openNuevoAprendizModal = () => {
  showNuevoAprendizModal.value = true;
};

const handleNuevoAprendizSave = async (payload) => {
  try {
    const apiPayload = {
      cr6a3_nombre_completo: `${payload.nombres} ${payload.apellidos}`,
      cr6a3_documento_de_identidad: payload.documento,
      cr6a3_correo_electronico: payload.correo,
      cr6a3_numero_celular: payload.celular || null,
      cr6a3_numero_ficha: payload.ficha,
    };
    
    await aprendicesService.crearAprendiz(apiPayload);

    showNuevoAprendizModal.value = false;
    toast.success("Aprendiz registrado exitosamente.");
    fetchAprendices();
  } catch (error) {
    console.error(error);
    toast.error(error.message || "Error al crear el aprendiz en el servidor");
  }
};

const exportarExcel = () => {
  toast.info("Iniciando exportación de aprendices...");
};

const getJornadaClass = (jornada) => {
  if (!jornada) return 'jornada-default';
  const j = jornada.toLowerCase();
  if (j.includes('mañana')) return 'jornada-manana';
  if (j.includes('tarde')) return 'jornada-tarde';
  if (j.includes('noche')) return 'jornada-noche';
  if (j.includes('madrugada')) return 'jornada-madrugada';
  return 'jornada-default';
};

const getJornadaIcon = (jornada) => {
  if (!jornada) return 'fa-solid fa-clock';
  const j = jornada.toLowerCase();
  if (j.includes('mañana')) return 'fa-solid fa-sun';
  if (j.includes('tarde')) return 'fa-solid fa-cloud-sun';
  if (j.includes('noche')) return 'fa-solid fa-moon';
  if (j.includes('madrugada')) return 'fa-solid fa-cloud-moon';
  return 'fa-solid fa-clock';
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

.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--borde);
  background: white;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.data-table th {
  text-align: left;
  padding: 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  border-bottom: 2px solid var(--fondo-app);
  text-transform: uppercase;
}

.data-table td {
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

/* --- Autocomplete Styles --- */
.autocomplete-box {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--borde);
  border-radius: 8px;
  max-height: 250px;
  overflow-y: auto;
  z-index: 1000;
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.autocomplete-dropdown li {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid var(--borde);
  font-size: 0.9rem;
  color: var(--texto-principal);
}

.autocomplete-dropdown li:last-child {
  border-bottom: none;
}

.autocomplete-dropdown li:hover, .autocomplete-dropdown li:active {
  background-color: var(--fondo-app);
  color: var(--sena-verde);
}

/* --- Empty State Styles --- */
.empty-state-search {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  background-color: var(--blanco);
  border-radius: 12px;
  border: 1px dashed var(--borde);
  margin-top: 1rem;
}

.empty-state-search .empty-icon {
  font-size: 3rem;
  color: var(--texto-secundario);
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state-search h3 {
  color: var(--texto-principal);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.empty-state-search p {
  color: var(--texto-secundario);
  font-size: 0.95rem;
  max-width: 400px;
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

.programa-badge {
  color: var(--sena-azul-oscuro);
  font-weight: 600;
  font-size: 0.85rem;
}

.instructor-subtext {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin-top: 4px;
}

.jornada-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}
.jornada-manana { background-color: #fff3e0; color: #e65100; }
.jornada-tarde { background-color: #e3f2fd; color: #1565c0; }
.jornada-noche { background-color: #ede7f6; color: #4527a0; }
.jornada-madrugada { background-color: #eceff1; color: #37474f; }
.jornada-default { background-color: #f5f5f5; color: #616161; }

.status-riesgo-alto {
  background-color: #fce4e4;
  color: #c62828;
}

.status-riesgo-normal {
  background-color: #e8f5e9;
  color: #2e7d32;
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

.status-lectiva {
  background-color: #E3F2FD;
  color: #1976D2;
}

.status-practica {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.status-finalizada {
  background-color: #F5F5F5;
  color: #757575;
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
