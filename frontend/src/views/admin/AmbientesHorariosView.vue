<template>
  <div class="admin-view-shell">
    <!-- Header principal -->
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>AMBIENTES Y HORARIOS</h1>
          <p class="header-meta">
            Gestión de ambientes de formación | 03:15:50 PM
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

    <!-- Barra de herramientas -->
      <div class="filters-bar">
        <!-- Botón Crear Ambiente -->
        <div style="display: flex; gap: 10px;" v-if="currentView === 'table'">
          <button class="btn-crear-instructor" @click="openModal()">
            <font-awesome-icon icon="fa-solid fa-plus" />
            <span>Crear Ambiente</span>
          </button>
          <button class="btn-crear-instructor" style="background-color: #2980b9;" @click="showModalSedes = true">
            <font-awesome-icon icon="fa-solid fa-building" />
            <span>Gestionar Sedes</span>
          </button>
        </div>
      <button v-if="currentView === 'calendar'" class="btn-crear-instructor" @click="currentView = 'table'; selectedAmbienteForCalendar = null">
        <font-awesome-icon icon="fa-solid fa-arrow-left" />
        <span>Volver a la Lista</span>
      </button>

      <div class="filters-right">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input type="text" class="form-input search-input" v-model="searchQuery" placeholder="Buscar Ambiente" />
        </div>
      </div>
    </div>

    <!-- Contenido Principal -->
    <main class="dash-grid">
      
      <!-- VISTA DE TABLA (CRUD) -->
      <section v-if="currentView === 'table'" class="instructors-table-container full-width">
        <div class="module-card">
          <table class="sena-table">
            <thead>
              <tr>
                <th>AMBIENTE</th>
                <th>SEDE</th>
                <th>IP MAESTRA</th>
                <th>CAPACIDAD</th>
                <th>NODOS</th>
                <th>DISPONIBILIDAD</th>
                <th>ESTADO</th>
                <th>ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="amb in filteredAmbientesList" :key="amb.cr6a3_ambiente_formacionid">
                <td>
                  <div class="table-instructor-info">
                    <div class="texts">
                      <span class="instructor-name-table">{{ amb.cr6a3_nombre_ambiente }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div style="display: flex; flex-direction: column;">
                    <span class="instructor-specialty-table">{{ amb.sede_nombre || 'Sin Sede' }}</span>
                    <span style="font-size: 0.75rem; color: #6c757d; font-weight: 500;" v-if="amb.sede_municipio">
                      <font-awesome-icon icon="fa-solid fa-location-dot" style="margin-right: 4px;" />{{ amb.sede_municipio }}
                    </span>
                  </div>
                </td>
                <td>
                  <span class="instructor-specialty-table">{{ amb.cr6a3_direccion_ip_maestra || 'N/A' }}</span>
                </td>
                <td>
                  <span class="instructor-specialty-table">{{ amb.cr6a3_capacidad_aprendices || 0 }} A.</span>
                </td>
                <td>
                  <span class="instructor-specialty-table">{{ amb.cr6a3_cantidad_nodos_electricos || 0 }} N.</span>
                </td>
                <td>
                  <div class="jornadas-ocupacion" translate="no">
                    <div class="jornada-badge" :class="amb.ocupacion?.manana ? 'ocupado' : 'libre'" :title="amb.ocupacion?.manana ? 'Ocupado hasta: ' + amb.ocupacion.manana.split('T')[0] : 'Disponible en la mañana'">
                      M
                    </div>
                    <div class="jornada-badge" :class="amb.ocupacion?.tarde ? 'ocupado' : 'libre'" :title="amb.ocupacion?.tarde ? 'Ocupado hasta: ' + amb.ocupacion.tarde.split('T')[0] : 'Disponible en la tarde'">
                      T
                    </div>
                    <div class="jornada-badge" :class="amb.ocupacion?.noche ? 'ocupado' : 'libre'" :title="amb.ocupacion?.noche ? 'Ocupado hasta: ' + amb.ocupacion.noche.split('T')[0] : 'Disponible en la noche'">
                      N
                    </div>
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', getStatusClass(amb.cr6a3_Estado_Ambiente)]" style="display: inline-block; width: fit-content;">
                    {{ getStatusText(amb.cr6a3_Estado_Ambiente).toUpperCase() }}
                  </span>
                </td>
                <td>
                  <div class="table-actions-group">
                    <button class="btn-icon action-view" title="Ver Horario" @click="viewCalendar(amb)">
                      <font-awesome-icon icon="fa-solid fa-calendar-days" />
                    </button>
                    <button class="btn-icon" title="Editar" @click="openModal(amb)">
                      <font-awesome-icon icon="fa-solid fa-pen-to-square" />
                    </button>
                    <button class="btn-icon action-delete" title="Eliminar" @click="deleteAmbiente(amb.cr6a3_ambiente_formacionid)">
                      <font-awesome-icon icon="fa-solid fa-trash" />
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredAmbientesList.length === 0">
                <td colspan="8" class="text-center empty-cell" style="padding: 20px;">No se encontraron ambientes.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- VISTA DE CALENDARIO ESPECÍFICO -->
      <section v-else-if="currentView === 'calendar' && selectedAmbienteForCalendar" class="dash-col">
        
        <!-- Calendario mensual -->
        <div class="module-card calendario-card">
          <div class="calendario-toolbar">
            <h2 class="module-title">
              <font-awesome-icon icon="fa-solid fa-calendar-days" /> CALENDARIO: {{ selectedAmbienteForCalendar.cr6a3_nombre_ambiente.toUpperCase() }}
            </h2>
            <div class="mes-nav">
              <button class="mes-flecha" aria-label="Mes anterior" @click="cambiarMes(-1)">
                <font-awesome-icon icon="fa-solid fa-chevron-left" />
              </button>
              <span class="mes-actual">{{ etiquetaMes }}</span>
              <button class="mes-flecha" aria-label="Mes siguiente" @click="cambiarMes(1)">
                <font-awesome-icon icon="fa-solid fa-chevron-right" />
              </button>
              <button class="btn-hoy" @click="irAHoy">Hoy</button>
            </div>
          </div>

          <div v-if="cargandoCalendario" class="estado-panel">
            <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
            <p>Cargando programación del ambiente...</p>
          </div>

          <div v-else class="calendario-scroll">
            <div class="calendario-grid">
              <div v-for="dia in DIAS_SEMANA" :key="dia" class="cal-encabezado">{{ dia }}</div>
              <div
                v-for="celda in celdasMes"
                :key="celda.iso"
                class="cal-dia"
                :class="{
                  'fuera-mes': !celda.esDelMes,
                  'fin-semana': celda.finDeSemana,
                  hoy: celda.iso === hoyIso,
                }"
              >
                <span class="cal-numero">{{ celda.dia }}</span>
                <div
                  v-for="a in celda.asignaciones"
                  :key="a.id"
                  class="cal-chip"
                  :style="estiloChip(a)"
                  :title="`Ficha ${a.ficha_codigo || 'N/A'} · ${a.ficha_programa || 'N/A'}\n` +
                    `${a.competencia?.nombre || 'Sin competencia'} (${a.competencia?.tipo || 'N/A'}) · Jornada ${a.jornada}\n` +
                    `${a.fecha_inicio} → ${a.fecha_fin} · ${a.horas} h · ` +
                    `Instructor: ${a.instructor?.nombre || '—'}`"
                >
                  <strong>{{ a.ficha_codigo || 'Ficha N/A' }}</strong>
                  <span class="cal-chip-texto">{{ a.competencia?.nombre || 'Sin competencia' }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!cargandoCalendario && leyendaMes.length" class="leyenda leyenda-calendario" style="margin-top: 15px;">
            <span class="leyenda-etiqueta">Convenciones del mes:</span>
            <span v-for="f in leyendaMes" :key="f.codigo" class="leyenda-item">
              <span class="punto-color" :style="{ background: f.color }"></span>
              <strong>{{ f.codigo }}</strong> = {{ f.programa }} ({{ f.jornada }})
            </span>
          </div>
          <p v-else-if="!cargandoCalendario" class="calendario-vacio" style="padding: 20px;">
            No hay asignaciones programadas en este mes.
          </p>
        </div>
        
        <!-- Detalle del mes (solo lectura) -->
        <div v-if="!cargandoCalendario && asignacionesMes.length" class="module-card" style="margin-top: 1.5rem;">
          <h2 class="module-title titulo-lista">
            <font-awesome-icon icon="fa-solid fa-table-list" /> DETALLE DE {{ etiquetaMes.toUpperCase() }}
          </h2>
          <ul class="lista-asignaciones">
            <li v-for="a in asignacionesMes" :key="a.id" class="asig-fila">
              <span class="asig-franja" :style="{ background: colorFicha(a.ficha_codigo) }"></span>
              <div class="asig-info">
                <span class="asig-principal">
                  <strong>Ficha {{ a.ficha_codigo || 'N/A' }}</strong> · {{ a.competencia?.nombre || 'Sin competencia' }}
                  <small>({{ a.competencia?.tipo || 'N/A' }})</small>
                </span>
                <span class="asig-secundario">
                  {{ formatearFecha(a.fecha_inicio) }} → {{ formatearFecha(a.fecha_fin) }}
                  · Jornada {{ a.jornada }} ({{ horarioJornada(a.jornada) }})
                  · {{ a.horas }} h · Instructor: {{ a.instructor?.nombre || '—' }}
                </span>
              </div>
            </li>
          </ul>
        </div>
      </section>
    </main>

    <!-- Modal para CREAR/EDITAR Ambiente -->
    <BaseModal
      :show="showModal"
      :title="formId ? 'Editar Ambiente' : 'Nuevo Ambiente'"
      @close="closeModal"
    >
      <form @submit.prevent="saveAmbiente" class="crud-form" style="display: flex; flex-direction: column; gap: 15px;">
        <div class="form-group">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Nombre del Ambiente <span class="text-danger" style="color: red;">*</span></label>
          <input type="text" class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model="formData.cr6a3_nombre_ambiente" required />
        </div>
        <div class="form-group">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Sede Asignada <span class="text-danger" style="color: red;">*</span></label>
          <select class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model="formData.sede_id" required>
            <option value="" disabled>Seleccione una sede...</option>
            <option v-for="s in sedesList" :key="s.cr6a3_sedeid" :value="s.cr6a3_sedeid">
              {{ s.cr6a3_nombre }} ({{ s.cr6a3_municipio || 'Sin municipio' }})
            </option>
          </select>
        </div>
        <div class="form-row" style="display: flex; gap: 15px;">
          <div class="form-group half" style="flex: 1;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Capacidad</label>
            <input type="number" class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model.number="formData.cr6a3_capacidad_aprendices" />
          </div>
          <div class="form-group half" style="flex: 1;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Nodos Eléctricos</label>
            <input type="number" class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model.number="formData.cr6a3_cantidad_nodos_electricos" />
          </div>
        </div>
        <div class="form-row" style="display: flex; gap: 15px;">
          <div class="form-group half" style="flex: 1;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Dirección IP Maestra</label>
            <input type="text" class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model="formData.cr6a3_direccion_ip_maestra" />
          </div>
          <div class="form-group half" style="flex: 1;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Estado</label>
            <select class="form-input" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" v-model.number="formData.cr6a3_Estado_Ambiente">
              <option :value="430120000">Activo</option>
              <option :value="430120001">En Mantenimiento</option>
              <option :value="430120002">Inactivo</option>
            </select>
          </div>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn-cancel" style="padding: 8px 16px; border: 1px solid #ccc; background: #fff; border-radius: 4px; cursor: pointer; font-weight: 600;" @click="closeModal">Cancelar</button>
        <button type="button" class="btn-action-green" style="padding: 8px 16px; border: none; border-radius: 4px; background: var(--sena-verde); color: white; cursor: pointer; font-weight: 600;" @click="saveAmbiente">Guardar</button>
      </template>
    </BaseModal>

    <!-- Modal para GESTIONAR Sedes -->
    <BaseModal
      :show="showModalSedes"
      title="Gestionar Sedes"
      @close="showModalSedes = false"
    >
      <div style="margin-bottom: 20px;">
        <h4 style="margin-bottom: 10px; color: var(--sena-azul-oscuro); margin-top: 0;">Crear Nueva Sede</h4>
        <form @submit.prevent="saveSede" style="display: flex; gap: 10px; flex-wrap: wrap;">
          <input type="text" v-model="formSede.cr6a3_nombre" placeholder="Nombre (Ej: Sede Principal)" class="form-input" style="flex:1; min-width: 150px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" required />
          <select v-model="formSede.cr6a3_municipio" class="form-input" style="flex:1; min-width: 100px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;" required>
            <option value="" disabled>Seleccione municipio...</option>
            <option value="Mocoa">Mocoa</option>
            <option value="Colón">Colón</option>
            <option value="Orito">Orito</option>
            <option value="Puerto Asís">Puerto Asís</option>
            <option value="Puerto Caicedo">Puerto Caicedo</option>
            <option value="Puerto Guzmán">Puerto Guzmán</option>
            <option value="Puerto Leguízamo">Puerto Leguízamo</option>
            <option value="San Francisco">San Francisco</option>
            <option value="San Miguel">San Miguel</option>
            <option value="Santiago">Santiago</option>
            <option value="Sibundoy">Sibundoy</option>
            <option value="Valle del Guamuez">Valle del Guamuez</option>
            <option value="Villagarzón">Villagarzón</option>
          </select>
          <button type="submit" class="btn-action-green" style="padding: 8px 15px; border-radius: 4px; border:none; color:white; background:var(--sena-verde); cursor: pointer; font-weight: bold;">Crear</button>
        </form>
      </div>

      <h4 style="margin-bottom: 10px; color: var(--sena-azul-oscuro);">Sedes Registradas</h4>
      <ul style="list-style:none; padding:0; margin:0; max-height: 250px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc;">
        <li v-for="s in sedesList" :key="s.cr6a3_sedeid" style="padding: 12px; border-bottom: 1px solid #e2e8f0; display: flex; flex-direction: column;">
          <strong style="color: var(--sena-azul-oscuro);">{{ s.cr6a3_nombre }}</strong>
          <span style="font-size: 0.85rem; color: var(--texto-secundario);"><font-awesome-icon icon="fa-solid fa-location-dot" style="margin-right:4px;" />{{ s.cr6a3_municipio || 'N/A' }}</span>
        </li>
      </ul>
      <p v-if="sedesList.length === 0" style="text-align:center; padding: 20px; color:#666;">No hay sedes registradas.</p>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ambientesService } from '@/services/ambientesService';
import { horarioJornada, formatearFecha } from '@/stores/tituladas';
import BaseModal from '@/components/admin/modals/BaseModal.vue';

const route = useRoute();

const currentView = ref('table'); 
const ambientesList = ref([]);
const sedesList = ref([]);
const selectedAmbienteForCalendar = ref(null);

const searchQuery = ref('');
const showModalSedes = ref(false);

const showModal = ref(false);
const formId = ref(null);
const formData = ref({
  cr6a3_nombre_ambiente: '',
  sede_id: '',
  cr6a3_direccion_ip_maestra: '',
  cr6a3_capacidad_aprendices: 0,
  cr6a3_cantidad_nodos_electricos: 0,
  cr6a3_Estado_Ambiente: 430120000
});

const formSede = ref({
  cr6a3_nombre: '',
  cr6a3_municipio: ''
});

const saveSede = async () => {
  try {
    await ambientesService.createSede(formSede.value);
    formSede.value = { cr6a3_nombre: '', cr6a3_municipio: '' };
    await loadSedes();
    alert("Sede creada exitosamente.");
  } catch (error) {
    console.error('Error creando sede:', error);
    alert("Error al crear la sede.");
  }
};

// CALENDARIO LOGIC
const asignacionesData = ref([]);
const cargandoCalendario = ref(false);
const NOMBRES_MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const PALETA_FICHAS = ['#39A900', '#2980B9', '#E67E22', '#8E44AD', '#C0392B', '#16A085', '#B7950B', '#1F618D'];

const hoy = new Date();
const hoyIso = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`;
const periodo = ref({ anio: hoy.getFullYear(), mes: hoy.getMonth() });

const etiquetaMes = computed(() => `${NOMBRES_MESES[periodo.value.mes]} ${periodo.value.anio}`);

const cambiarMes = (delta) => {
  const fecha = new Date(periodo.value.anio, periodo.value.mes + delta, 1);
  periodo.value = { anio: fecha.getFullYear(), mes: fecha.getMonth() };
};

const irAHoy = () => {
  periodo.value = { anio: hoy.getFullYear(), mes: hoy.getMonth() };
};

const colorFicha = (codigoFicha) => {
  if (!codigoFicha) return '#7f8c8d';
  let hash = 0;
  for (let i = 0; i < codigoFicha.length; i++) {
    hash = codigoFicha.charCodeAt(i) + ((hash << 5) - hash);
  }
  return PALETA_FICHAS[Math.abs(hash) % PALETA_FICHAS.length];
};

const estiloChip = (asig) => {
  const baseColor = colorFicha(asig.ficha_codigo);
  return {
    borderLeft: `4px solid ${baseColor}`,
    background: `${baseColor}15`, 
    color: 'var(--texto-principal)'
  };
};

const cargarCalendario = async (ambId) => {
  cargandoCalendario.value = true;
  try {
    const data = await ambientesService.getCalendario(ambId);
    if (data && data.asignaciones) {
      asignacionesData.value = data.asignaciones.map(a => ({
        ...a,
        fecha_inicio: a.fecha_inicio ? a.fecha_inicio.split('T')[0] : a.fecha_inicio,
        fecha_fin: a.fecha_fin ? a.fecha_fin.split('T')[0] : a.fecha_fin
      }));
    } else {
      asignacionesData.value = [];
    }
  } catch (error) {
    console.error("Error cargando calendario:", error);
    asignacionesData.value = [];
  } finally {
    cargandoCalendario.value = false;
  }
};

const asignacionesMes = computed(() => {
  if (!asignacionesData.value.length) return [];
  const p = periodo.value;
  const mesAnioPrefix = `${p.anio}-${String(p.mes + 1).padStart(2, '0')}`;
  
  return asignacionesData.value.filter(a => {
    if (!a.fecha_inicio || !a.fecha_fin) return false;
    return a.fecha_inicio.startsWith(mesAnioPrefix) || 
           a.fecha_fin.startsWith(mesAnioPrefix) ||
           (a.fecha_inicio < `${mesAnioPrefix}-01` && a.fecha_fin >= `${mesAnioPrefix}-31`);
  });
});

const celdasMes = computed(() => {
  const p = periodo.value;
  const primerDiaMes = new Date(p.anio, p.mes, 1);
  const ultimoDiaMes = new Date(p.anio, p.mes + 1, 0);
  
  let diaSemanaInicio = primerDiaMes.getDay() || 7; 
  diaSemanaInicio--; 
  
  const diasAnterior = new Date(p.anio, p.mes, 0).getDate();
  const celdas = [];
  
  for (let i = diaSemanaInicio - 1; i >= 0; i--) {
    const d = diasAnterior - i;
    const iso = `${p.mes === 0 ? p.anio - 1 : p.anio}-${String(p.mes === 0 ? 12 : p.mes).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    celdas.push({ dia: d, esDelMes: false, iso, finDeSemana: i === 0 || i === 1 });
  }
  
  for (let d = 1; d <= ultimoDiaMes.getDate(); d++) {
    const iso = `${p.anio}-${String(p.mes + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const diaSemana = new Date(p.anio, p.mes, d).getDay();
    celdas.push({ dia: d, esDelMes: true, iso, finDeSemana: diaSemana === 0 || diaSemana === 6 });
  }
  
  const extras = celdas.length % 7 === 0 ? 0 : 7 - (celdas.length % 7);
  for (let d = 1; d <= extras; d++) {
    const iso = `${p.mes === 11 ? p.anio + 1 : p.anio}-${String(p.mes === 11 ? 1 : p.mes + 2).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    celdas.push({ dia: d, esDelMes: false, iso, finDeSemana: false });
  }
  
  const asignacionesPorFecha = {};
  asignacionesMes.value.forEach(asig => {
    const inicio = new Date(asig.fecha_inicio + 'T12:00:00');
    const fin = new Date(asig.fecha_fin + 'T12:00:00');
    for (let dt = new Date(inicio); dt <= fin; dt.setDate(dt.getDate() + 1)) {
      const iterIso = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
      if (!asignacionesPorFecha[iterIso]) asignacionesPorFecha[iterIso] = [];
      asignacionesPorFecha[iterIso].push(asig);
    }
  });
  
  return celdas.map(celda => {
    let diaAsigs = asignacionesPorFecha[celda.iso] || [];
    if (celda.finDeSemana) {
      diaAsigs = diaAsigs.filter(a => a.jornada !== 'Mañana' && a.jornada !== 'Tarde'); // Logica basica para finde
    }
    return { ...celda, asignaciones: diaAsigs };
  });
});

const leyendaMes = computed(() => {
  const map = new Map();
  asignacionesMes.value.forEach(a => {
    if (!map.has(a.ficha_codigo)) {
      map.set(a.ficha_codigo, {
        codigo: a.ficha_codigo,
        programa: a.ficha_programa,
        jornada: a.jornada,
        color: colorFicha(a.ficha_codigo)
      });
    }
  });
  return Array.from(map.values());
});


const loadAmbientes = async () => {
  try {
    const data = await ambientesService.getAll();
    ambientesList.value = data;
  } catch (error) {
    console.error('Error loading ambientes:', error);
  }
};

const loadSedes = async () => {
  try {
    const data = await ambientesService.getSedes();
    sedesList.value = data;
  } catch (error) {
    console.error('Error loading sedes:', error);
  }
};

onMounted(async () => {
  await loadAmbientes();
  await loadSedes();
  if (route.query.q) {
    searchQuery.value = route.query.q;
  }
});

const filteredAmbientesList = computed(() => {
  if (!searchQuery.value) return ambientesList.value;
  const q = searchQuery.value.toLowerCase();
  return ambientesList.value.filter(amb => 
    amb.cr6a3_nombre_ambiente?.toLowerCase().includes(q) ||
    amb.sede_nombre?.toLowerCase().includes(q)
  );
});

// CRUD Logic
const openModal = (amb = null) => {
  if (amb) {
    formId.value = amb.cr6a3_ambiente_formacionid;
    formData.value = {
      cr6a3_nombre_ambiente: amb.cr6a3_nombre_ambiente || '',
      sede_id: amb.sede_id || '',
      cr6a3_direccion_ip_maestra: amb.cr6a3_direccion_ip_maestra || '',
      cr6a3_capacidad_aprendices: amb.cr6a3_capacidad_aprendices || 0,
      cr6a3_cantidad_nodos_electricos: amb.cr6a3_cantidad_nodos_electricos || 0,
      cr6a3_Estado_Ambiente: amb.cr6a3_Estado_Ambiente || 430120000
    };
  } else {
    formId.value = null;
    formData.value = {
      cr6a3_nombre_ambiente: '',
      sede_id: '',
      cr6a3_direccion_ip_maestra: '',
      cr6a3_capacidad_aprendices: 0,
      cr6a3_cantidad_nodos_electricos: 0,
      cr6a3_Estado_Ambiente: 430120000
    };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  formId.value = null;
};

const saveAmbiente = async () => {
  try {
    if (formId.value) {
      await ambientesService.update(formId.value, formData.value);
    } else {
      await ambientesService.create(formData.value);
    }
    closeModal();
    await loadAmbientes();
  } catch (error) {
    console.error("Error guardando ambiente:", error);
    alert("Hubo un error al guardar el ambiente");
  }
};

const deleteAmbiente = async (id) => {
  if (confirm("¿Estás seguro de eliminar este ambiente?")) {
    try {
      await ambientesService.delete(id);
      await loadAmbientes();
    } catch (error) {
      console.error("Error eliminando ambiente:", error);
      alert("Hubo un error al eliminar el ambiente");
    }
  }
};

// Calendar Actions
const viewCalendar = async (amb) => {
  selectedAmbienteForCalendar.value = amb;
  currentView.value = 'calendar';
  await cargarCalendario(amb.cr6a3_ambiente_formacionid);
};

// Utils
const getStatusText = (status) => {
  const map = {
    430120000: 'Activo',
    430120001: 'Mantenimiento',
    430120002: 'Inactivo'
  };
  return map[status] || 'Desconocido';
};

const getStatusClass = (status) => {
  const map = {
    430120000: 'badge-planta',
    430120001: 'badge-contratista',
    430120002: 'badge-contratista' // using existing sena-table classes for now
  };
  return map[status] || 'badge-contratista';
};
</script>

<style scoped>
@import './cal.css';

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

.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-crear-instructor {
  background: var(--sena-verde, #39A900);
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(57, 169, 0, 0.2);
}

.btn-crear-instructor:hover {
  background: #2d8500;
  transform: translateY(-2px);
}

.filters-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  position: relative;
  width: 250px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
}

.search-input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.2rem;
  border: 1px solid var(--borde, #dee2e6);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: var(--sena-verde, #39A900);
}

/* ==========================================================================
   TABLA ESTILO SENA (Copia de InstructoresView)
   ========================================================================== */
.instructors-table-container {
    width: 100%;
    animation: fadeIn 0.4s ease;
  }
  
  .sena-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    font-size: 0.9rem;
  }
  
  .sena-table th {
    background-color: var(--fondo-app, #f8fafc);
    color: var(--texto-secundario, #64748b);
    font-weight: 700;
    text-transform: uppercase;
    padding: 1rem;
    text-align: left;
    border-bottom: 2px solid var(--borde, #e2e8f0);
    font-size: 0.8rem;
  }
  
  .sena-table td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid var(--borde, #e2e8f0);
    vertical-align: middle;
  }
  
  .sena-table tr:hover td {
    background-color: #f8f9fa;
  }
  
  .table-instructor-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .instructor-name-table {
    display: block;
    font-weight: 700;
    color: var(--sena-azul-oscuro);
    font-size: 1rem;
  }
  
  .instructor-specialty-table {
    font-size: 0.9rem;
    color: var(--texto-secundario);
  }
  
  .status-badge {
    padding: 0.35rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
  }
  .badge-planta {
    background: rgba(57, 169, 0, 0.15);
    color: #2d8500;
  }
  .badge-contratista {
    background: rgba(41, 128, 185, 0.15);
    color: #2980b9;
  }
  
  .table-actions-group {
    display: flex;
    gap: 8px;
    justify-content: center;
  }
  
  .btn-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--texto-secundario);
    background: #f8f9fa;
  }
  
  .btn-icon:hover {
    background: #e9ecef;
    color: var(--sena-azul-oscuro);
  }
.action-view:hover { color: #2980b9; }
.action-edit:hover { color: #f39c12; }
.action-delete:hover { color: #c0392b; }

.module-card {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--borde);
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

/* Modals Overlay */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* ── Detalle del mes ── */
.titulo-lista { margin-bottom: 1rem; }

.lista-asignaciones {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asig-fila {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 0.7rem 0.9rem;
}

.asig-franja {
  width: 5px;
  align-self: stretch;
  border-radius: 3px;
  flex-shrink: 0;
}

.asig-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.asig-principal {
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.asig-principal small { color: var(--texto-secundario); }

.asig-secundario { font-size: 0.72rem; color: var(--texto-secundario); }

/* ── Disponibilidad por jornadas ── */
.jornadas-ocupacion {
  display: flex;
  gap: 6px;
}

.jornada-badge {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 800;
  cursor: help;
  transition: transform 0.1s ease;
}

.jornada-badge:hover {
  transform: scale(1.1);
}

.jornada-badge.libre {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.jornada-badge.ocupado {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}
</style>
