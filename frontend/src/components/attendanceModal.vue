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
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
}
.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--sena-naranja);
  border-radius: 2px;
}
.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  letter-spacing: 0.08em;
}

.attendance-dashboard-box {
  display: flex;
  gap: 12px;
  margin-bottom: 1.5rem;
}
.stat-card {
  flex: 1;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.border-orange {
  border-left: 4px solid var(--sena-naranja);
}
.border-sena {
  border-left: 4px solid var(--sena-verde);
}

.stat-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
}
.stat-value {
  font-size: 1.4rem;
  font-weight: 800;
}
.text-orange {
  color: var(--sena-naranja);
}
.text-sena-claro {
  color: var(--sena-verde);
}

.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin-bottom: 1rem;
}

.timeline-container {
  position: relative;
  max-height: 250px;
  overflow-y: auto;
  padding-left: 8px;
}
.timeline-line {
  position: absolute;
  left: 17px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: var(--borde);
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
  background: var(--fondo-tarjetas);
}
.icon-status {
  font-size: 0.95rem;
  background: var(--fondo-tarjetas);
  border-radius: 50%;
}
.text-green {
  color: var(--sena-verde);
}
.text-red {
  color: var(--sena-amarillo);
}

.timeline-content-box {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 8px 12px;
  border-radius: 8px;
  margin-left: 12px;
}
.session-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--sena-azul-oscuro);
}
.badge-status {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}
.badge-presente {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde);
}
.badge-falta {
  background: rgba(253, 195, 0, 0.1);
  color: var(--sena-azul-oscuro);
}

.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}
.btn-modal-close {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  transition: opacity 0.2s;
}
.btn-modal-close:hover {
  opacity: 0.9;
}
</style>
