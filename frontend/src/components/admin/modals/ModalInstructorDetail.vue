<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content detail-modal" style="height: 85vh; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; background-color: #181818;">
      
      <!-- HEADER (FIJO) -->
      <header class="modal-header" style="flex-shrink: 0;">
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

      <!-- CONTENIDO MEDIO SCROLLEABLE (STAT CARDS + TABS + CONTENIDO) -->
      <div class="modal-body-scrollable" style="flex: 1; min-height: 0; overflow-y: auto; padding-right: 4px;">
        
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
          <!-- Fechas de Contrato -->
          <div class="stat-card">
            <span class="stat-label">Inicio Contrato</span>
            <span class="stat-value">{{ formatDate(instructorData?.fecha_inicio_contrato || instructorData?.fechaInicioContrato) }}</span>
          </div>

          <div class="stat-card">
            <span class="stat-label">Fin Contrato</span>
            <span class="stat-value">{{ formatDate(instructorData?.fecha_fin_contrato || instructorData?.fechaFinContrato) }}</span>
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
                <span class="info-value">{{ instructorData?.document || 'No registrado' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Correo</span>
                <span class="info-value">{{ instructorData?.email || 'No registrado' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Teléfono</span>
                <span class="info-value">{{ instructorData?.phone || 'No registrado' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Perfil Profesional</span>
                <span class="info-value">{{ instructorData?.specialty || 'General' }}</span>
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
                    <span class="conn-title">Tiempo Con.</span>
                    <span class="conn-value-main">28h 45 min</span>
                  </div>
                </div>
                <span class="conn-date">En los últimos días</span>
              </div>
            </div>
          </div>

          <!-- ASIGNACIONES TAB -->
          <div v-if="activeTab === 'asignaciones'" class="tab-pane">
            <div v-if="cargandoAsignaciones" class="empty-state">
              <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="empty-icon" />
              <p>Cargando asignaciones...</p>
            </div>
            <div v-else-if="realAsignaciones.length > 0" class="assignments-grid">
              <div class="assignment-card" v-for="item in realAsignaciones" :key="item.id">
                <h5>Ficha: {{ item.ficha_codigo || 'N/A' }} | {{ item.jornada || 'N/A' }}</h5>
                <p class="subtitle">{{ item.programa?.nombre || 'General' }}</p>
                <div class="detail-line">
                  <span class="label">Competencia:</span>
                  <span class="val" :title="item.competencia?.nombre || 'N/A'">
                    {{ (item.competencia?.nombre || 'N/A').substring(0, 30) }}...
                  </span>
                </div>
                <div class="detail-line font-bold">
                  <span class="label">Horas:</span>
                  <span class="val text-green">{{ item.horas }}h</span>
                </div>
                <div class="detail-line">
                  <span class="label">Inicio:</span>
                  <span class="val">{{ formatDate(item.fecha_inicio) }}</span>
                </div>
                <div class="detail-line">
                  <span class="label">Fin:</span>
                  <span class="val">{{ formatDate(item.fecha_fin) }}</span>
                </div>
                <div class="detail-line">
                  <span class="label">Ambiente:</span>
                  <span class="val">{{ item.ambiente?.nombre || 'N/A' }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <font-awesome-icon icon="fa-solid fa-list-check" class="empty-icon" />
              <p>No hay asignaciones ni horarios registrados para este instructor.</p>
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

      </div>

      <!-- FOOTER NORMAL -->
<footer v-if="!showConfirmDelete" class="modal-footer" style="flex-shrink: 0; display: flex; justify-content: space-between; align-items: center; width: 100%; padding-top: 1rem; margin-top: auto; border-top: 1px solid #333; background-color: #181818;">
  <button 
    type="button" 
    class="btn-delete" 
    style="background-color: #dc3545; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; font-weight: bold;"
    @click="showConfirmDelete = true"
  >
    <font-awesome-icon icon="fa-solid fa-trash" /> Eliminar Instructor
  </button>

  <button type="button" class="btn-cancel" @click="closeModal">Cerrar</button>
</footer>

<!-- CONFIRMACIÓN INTEGRADA (Misma estética VoltMind) -->
<footer v-else class="modal-footer" style="flex-shrink: 0; display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 0.8rem 1rem; margin-top: auto; border-top: 1px solid #dc3545; background-color: #2a1215; border-radius: 6px;">
  <span style="color: #f8d7da; font-size: 0.9rem; font-weight: 500;">
    ⚠️ ¿Seguro que deseas eliminar este instructor?
  </span>
  
  <div style="display: flex; gap: 0.5rem;">
    <button 
      type="button" 
      style="background-color: #dc3545; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; font-weight: bold;"
      @click="$emit('delete', instructorData?.cr6a3_instructorid || instructorData?.id); showConfirmDelete = false;"
    >
      Sí, eliminar
    </button>
    
    <button 
      type="button" 
      style="background-color: #444; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer;"
      @click="showConfirmDelete = false"
    >
      Cancelar
    </button>
  </div>
</footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue';
import { useProgramacionStore } from '@/stores/programacion';
import UserAvatar from '@/components/UserAvatar.vue';
import { tituladasService } from '@/services/tituladasService';

const props = defineProps({
  show: Boolean,
  instructorData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'close', 'delete']);

const formatDate = (dateStr) => {
  if (!dateStr || dateStr === 'Sin fecha') return 'Sin fecha';
  return dateStr.split('T')[0];
};

const store = useProgramacionStore();
const realAsignaciones = ref([]);
const cargandoAsignaciones = ref(false);

const activeTab = ref('resumen');

const tabs = [
  { id: 'resumen', label: 'Resumen' },
  { id: 'asignaciones', label: 'Asignaciones / Horarios' },
  { id: 'novedades', label: 'Novedades' }
];

watch(() => props.show, async (newVal) => {
  if (newVal) {
    activeTab.value = 'resumen';
    realAsignaciones.value = [];
    if (props.instructorData && props.instructorData.id) {
      cargandoAsignaciones.value = true;
      try {
        const data = await tituladasService.getCalendarioInstructor({ instructorId: props.instructorData.id });
        if (data && data.asignaciones) {
          realAsignaciones.value = data.asignaciones;
        }
      } catch (e) {
        console.error("Error cargando asignaciones:", e);
      } finally {
        cargandoAsignaciones.value = false;
      }
    }
  }
});



//alerta de eliminacion//
const showConfirmDelete = ref(false)
  
const getInitials = (name) => {
  if (!name) return '';
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
};

const getAvailableHours = computed(() => {
  if (!props.instructorData) return 0;
  return props.instructorData.maxHours - props.instructorData.hours;
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
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: var(--fondo-app, #f8fafc);
  border-bottom: 1px solid var(--borde, #cbd5e1);
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.25rem;
  border: 1px solid var(--borde, #cbd5e1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario, #64748b);
  text-transform: uppercase;
  white-space: nowrap;
}

.stat-value {
  font-size: 1.1rem;
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
  grid-template-columns: repeat(2, 1fr);
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assignment-card .subtitle {
  margin: 4px 0 10px 0;
  font-size: 0.75rem;
  color: var(--texto-secundario, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* Todo tu CSS actual del modal va aquí arriba ... */

.detail-modal {
  max-height: 85vh !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.tab-content-container {
  overflow-y: auto !important;
  flex: 1 !important;
}

.modal-footer {
  flex-shrink: 0 !important;
}

</style>
