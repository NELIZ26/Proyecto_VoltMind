<script setup>
import { computed } from "vue";

const props = defineProps({
  apprentice: {
    type: Object,
    required: true,
  },
});

defineEmits(["close"]);

// 📊 Cálculo reactivo del porcentaje de asistencia para inflar el nivel visual
const totalSessions = computed(() => props.apprentice.history?.length || 0);
const absenceCount = computed(() => props.apprentice.absences || 0);
const attendanceRate = computed(() => {
  if (totalSessions.value === 0) return 100;
  const presence = totalSessions.value - absenceCount.value;
  return Math.round((presence / totalSessions.value) * 100);
});

// Función útil para limpiar el texto "(P)" o "(F)" en la UI
const formatLogText = (log) => {
  return log.replace("(P)", "").replace("(F)", "").trim();
};
</script>

<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <div class="modal-header">
        <div class="header-indicator"></div>
        <h3>REPORTE HISTÓRICO DE ASISTENCIA</h3>
      </div>

      <div class="modal-body">
        <div class="attendance-dashboard-box">
          <div class="stat-card border-orange">
            <span class="stat-label">Inasistencias</span>
            <strong class="stat-value text-orange">{{
              apprentice.absences
            }}</strong>
          </div>
          <div class="stat-card border-sena">
            <span class="stat-label">Tasa de Asistencia</span>
            <strong class="stat-value text-sena-claro"
              >{{ attendanceRate }}%</strong
            >
          </div>
        </div>

        <h4 class="section-title">Rastreo de las últimas sesiones:</h4>

        <div class="timeline-container">
          <div class="timeline-line"></div>

          <ul class="history-list">
            <li
              v-for="(log, idx) in apprentice.history"
              :key="idx"
              class="timeline-item"
            >
              <div class="timeline-icon-wrapper">
                <font-awesome-icon
                  icon="fa-solid fa-circle-check"
                  class="icon-status text-green"
                  v-if="log.includes('(P)')"
                />
                <font-awesome-icon
                  icon="fa-solid fa-circle-xmark"
                  class="icon-status text-red"
                  v-else
                />
              </div>

              <div class="timeline-content-box">
                <span class="session-name"
                  >Sesión {{ formatLogText(log) }}</span
                >
                <span
                  :class="[
                    'badge-status',
                    log.includes('(P)') ? 'badge-presente' : 'badge-falta',
                  ]"
                >
                  {{ log.includes("(P)") ? "Asistió" : "Falta" }}
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-modal-close" @click="$emit('close')">
          CERRAR REPORTE
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   ESTILOS PREMIUM - REPORTE DE ASISTENCIA (VoltMind UI)
   ========================================================================== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  font-family: var(--fuente-principal, "Inter", sans-serif);
}

.modal-card {
  background: #0d0d0f; /* Negro zinc texturizado corporativo */
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
}

/* Encabezado */
.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
}

.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(
    --sena-naranja,
    #ff6b00
  ); /* Cambio a naranja para denotar historial/alertas */
  border-radius: 2px;
  box-shadow: 0 0 10px rgba(255, 107, 0, 0.4);
}

.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  letter-spacing: 0.08em;
}

/* Dashboard de Estadísticas */
.attendance-dashboard-box {
  display: flex;
  gap: 12px;
  margin-bottom: 1.5rem;
}

.stat-card {
  flex: 1;
  background: #121215;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  padding: 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
}

.border-orange {
  border-left: 3px solid var(--sena-naranja, #ff6b00);
}
.border-sena {
  border-left: 3px solid var(--sena-verde, #39a900);
}

.stat-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--texto-secundario, #a0aec0);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
}

.text-orange {
  color: var(--sena-naranja, #ff6b00);
}
.text-sena-claro {
  color: var(--sena-verde-claro, #deff9a);
}

.section-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--texto-secundario, #a0aec0);
  margin-bottom: 0.75rem;
  text-align: left;
}

/* ==========================================================================
   ESTRUCTURA DE LÍNEA DE TIEMPO (TIMELINE)
   ========================================================================== */
.timeline-container {
  position: relative;
  max-height: 220px; /* Scroll controlado si el historial crece demasiado */
  overflow-y: auto;
  padding-left: 8px;
  margin-bottom: 1rem;
}

/* Barra vertical de fondo */
.timeline-line {
  position: absolute;
  left: 17px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: rgba(255, 255, 255, 0.04);
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 2;
}

.timeline-icon-wrapper {
  width: 20px;
  display: flex;
  justify-content: center;
  background: #0d0d0f; /* Tapa la línea que pasa por detrás */
}

.icon-status {
  font-size: 0.95rem;
  background: #0d0d0f;
  border-radius: 50%;
}

.text-green {
  color: var(--sena-verde, #39a900);
  box-shadow: 0 0 6px rgba(57, 169, 0, 0.2);
}
.text-red {
  color: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.2);
}

/* Contenedor de Datos de Fila */
.timeline-content-box {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: 8px;
  margin-left: 12px;
  transition: all 0.2s ease;
}

.timeline-content-box:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.06);
}

.session-name {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--texto-principal, #ffffff);
}

/* Badges Translúcidos */
.badge-status {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.badge-presente {
  background: rgba(57, 169, 0, 0.08);
  border: 1px solid rgba(57, 169, 0, 0.15);
  color: var(--sena-verde-claro, #deff9a);
}

.badge-falta {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  color: #fca5a5;
}

/* Footer y Botones */
.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.btn-modal-close {
  background: transparent;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  color: var(--texto-secundario, #a0aec0);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.btn-modal-close:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--texto-principal, #ffffff);
}

/* Personalización del Scrollbar de la línea de tiempo */
.timeline-container::-webkit-scrollbar {
  width: 4px;
}
.timeline-container::-webkit-scrollbar-track {
  background: transparent;
}
.timeline-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
</style>
