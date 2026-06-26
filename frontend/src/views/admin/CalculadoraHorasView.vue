<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>CALCULADORA DE HORAS</h1>
          <p class="header-meta">
            Asignación y proyección de horas de instructores
          </p>
        </div>
      </div>
    </header>
    
    <main class="dash-grid">
      <!-- Panel Izquierdo: Selección de Ficha -->
      <section class="dash-col">
        <div class="module-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-clipboard-list" /> SELECCIONAR FICHA
          </h2>
          
          <div class="form-group">
            <label for="ficha-select" class="form-label">Programa de Formación</label>
            <select id="ficha-select" v-model="selectedFicha" class="form-select">
              <option disabled value="">Seleccione una ficha...</option>
              <option v-for="ficha in fichas" :key="ficha.id" :value="ficha.id">
                {{ ficha.code }} - {{ ficha.name }}
              </option>
            </select>
          </div>

          <div v-if="selectedFicha" class="fade-in-content mt-4">
            <h3 class="section-subtitle">Resultados de Aprendizaje (RAP)</h3>
            
            <div class="rap-group">
              <h4 class="rap-group-title">TÉCNICAS</h4>
              <ul class="rap-list">
                <li v-for="rap in currentRaps.tecnicas" :key="rap.id" class="rap-item">
                  <span class="rap-name">{{ rap.name }}</span>
                  <span class="rap-hours time-cell">{{ rap.hours }}h</span>
                </li>
              </ul>
            </div>

            <div class="rap-group">
              <h4 class="rap-group-title">TRANSVERSALES</h4>
              <ul class="rap-list">
                <li v-for="rap in currentRaps.transversales" :key="rap.id" class="rap-item">
                  <span class="rap-name">{{ rap.name }}</span>
                  <span class="rap-hours time-cell">{{ rap.hours }}h</span>
                </li>
              </ul>
            </div>
          </div>
          <div v-else class="empty-state">
            Seleccione una ficha para ver sus materias.
          </div>
        </div>
      </section>

      <!-- Panel Derecho: Simulador -->
      <section class="dash-col">
        <div class="module-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-calculator" /> SIMULADOR DE ASIGNACIÓN
          </h2>
          
          <div class="summary-box">
            <div class="summary-row">
              <span class="summary-label">Base Mensual:</span>
              <strong class="summary-value">154h</strong>
            </div>
            <div class="summary-row summary-error">
              <span class="summary-label">Festivos Estimados:</span>
              <strong class="summary-value">- 14h</strong>
            </div>
            <div class="summary-row summary-total">
              <span class="summary-label">Horas Hábiles:</span>
              <strong class="summary-value">140h</strong>
            </div>
          </div>

          <div class="form-group mt-4">
            <label for="instructor-select" class="form-label">Asignar Instructor</label>
            <select id="instructor-select" v-model="selectedInstructor" class="form-select">
              <option disabled value="">Seleccione instructor...</option>
              <option v-for="inst in instructors" :key="inst.id" :value="inst">
                {{ inst.name }} (Actual: {{ inst.currentHours }}h)
              </option>
            </select>
          </div>

          <div v-if="selectedInstructor" class="fade-in-content mt-4">
            <h3 class="section-subtitle">Proyección de Carga</h3>
            <div class="progress-container">
              <div 
                class="progress-bar" 
                :class="{ 'progress-bar-error': projectedHours > 160 }"
                :style="{ width: Math.min((projectedHours / 160) * 100, 100) + '%' }"
              ></div>
            </div>
            <p class="progress-text time-cell">
              {{ projectedHours }}h / 160h
            </p>
            
            <div v-if="projectedHours > 160" class="alert-box alert-error">
              <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="alert-icon" />
              <span>Alerta: La carga superará el máximo de 160h mensuales.</span>
            </div>
            <div v-else class="alert-box alert-success">
              <font-awesome-icon icon="fa-solid fa-circle-check" class="alert-icon" />
              <span>Asignación viable.</span>
            </div>

            <button class="btn-confirm mt-4">
              <font-awesome-icon icon="fa-solid fa-check" />
              CONFIRMAR ASIGNACIÓN
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

// Mock Data
const fichas = reactive([
  { id: 1, code: '2693821', name: 'ADSO' },
  { id: 2, code: '2693822', name: 'Multimedia' }
]);

const selectedFicha = ref('');
const selectedInstructor = ref('');

const allRaps = {
  1: {
    tecnicas: [
      { id: 101, name: 'Construcción de Software', hours: 60 },
      { id: 102, name: 'Bases de Datos', hours: 40 }
    ],
    transversales: [
      { id: 201, name: 'Inglés', hours: 20 },
      { id: 202, name: 'Ética', hours: 10 }
    ]
  },
  2: {
    tecnicas: [
      { id: 301, name: 'Diseño UX/UI', hours: 50 }
    ],
    transversales: [
      { id: 401, name: 'Comunicación', hours: 15 }
    ]
  }
};

const instructors = reactive([
  { id: 1, name: 'Juan Pérez', currentHours: 120 },
  { id: 2, name: 'Ana Gómez', currentHours: 150 },
  { id: 3, name: 'Carlos Díaz', currentHours: 80 }
]);

const currentRaps = computed(() => {
  return selectedFicha.value ? allRaps[selectedFicha.value] : null;
});

const totalRapHours = computed(() => {
  if (!currentRaps.value) return 0;
  let t = currentRaps.value.tecnicas.reduce((acc, rap) => acc + rap.hours, 0);
  let tr = currentRaps.value.transversales.reduce((acc, rap) => acc + rap.hours, 0);
  return t + tr;
});

const projectedHours = computed(() => {
  if (!selectedInstructor.value) return 0;
  return selectedInstructor.value.currentHours + totalRapHours.value;
});
</script>

<style scoped>
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL (SENA 2024 - CASO BLANCO MÁXIMO)
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

.dash-grid {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.dash-col {
  flex: 1;
  min-width: 320px;
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
  gap: 1.25rem;
  flex-grow: 1;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--borde);
  border-radius: 8px;
  background-color: var(--fondo-app);
  color: var(--texto-principal);
  outline: none;
  font-family: inherit;
  font-size: 0.9rem;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-select:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.fade-in-content {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.mt-4 {
  margin-top: 1rem;
}

.section-subtitle {
  font-size: 1rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0 0 16px 0;
}

.rap-group {
  margin-bottom: 16px;
}

.rap-group-title {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-secundario);
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
}

.rap-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rap-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--fondo-app);
  border-radius: 8px;
  border: 1px solid var(--borde);
}

.rap-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--texto-principal);
}

.time-cell {
  font-family: monospace;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
  background: var(--fondo-app);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--borde);
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--texto-secundario);
  font-size: 0.85rem;
  background-color: var(--fondo-app);
  border-radius: 8px;
  margin-top: 1rem;
  border: 1px dashed var(--borde);
}

.summary-box {
  background-color: var(--fondo-app);
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.summary-label {
  color: var(--texto-secundario);
  font-weight: 600;
}

.summary-value {
  color: var(--texto-principal);
  font-family: monospace;
  font-size: 1rem;
}

.summary-error {
  color: #E53E3E;
}

.summary-error .summary-value {
  color: #E53E3E;
}

.summary-total {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--sena-verde-oscuro);
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px dashed var(--borde);
}

.summary-total .summary-value {
  color: var(--sena-verde-oscuro);
  font-size: 1.2rem;
}

.progress-container {
  width: 100%;
  height: 12px;
  background-color: var(--borde);
  border-radius: 999px;
  overflow: hidden;
  margin: 8px 0;
}

.progress-bar {
  height: 100%;
  background-color: var(--sena-verde);
  transition: width 0.5s ease-out, background-color 0.3s;
}

.progress-bar-error {
  background-color: #E53E3E;
}

.progress-text {
  align-self: flex-end;
  display: inline-block;
  margin-bottom: 1rem;
}

.alert-box {
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  gap: 12px;
  align-items: center;
}

.alert-error {
  background-color: rgba(229, 62, 62, 0.1);
  color: #E53E3E;
  border: 1px solid #E53E3E;
}

.alert-success {
  background-color: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
  border: 1px solid var(--sena-verde);
}

[data-theme="dark"] .alert-success { color: #81c784; }

.btn-confirm {
  width: 100%;
  padding: 12px 24px;
  background-color: var(--sena-verde);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-confirm:hover {
  background-color: var(--sena-verde-oscuro);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
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
  }
  .dash-col {
    min-width: 100%;
  }
}
</style>
