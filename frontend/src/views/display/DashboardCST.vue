<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import AlertPanel from "@/components/AlertPanel.vue";
import { useRole } from "@/composables/useRole";

const router = useRouter();
const { hasRole } = useRole();
const currentTime = ref(new Date().toLocaleTimeString());

// Mock de consumo global (agrupado por redes)
const globalMetrics = ref([
  { id: "bloque-a", label: "Bloque A (Aulas)", load: 4500, status: "nominal" },
  {
    id: "bloque-b",
    label: "Bloque B (Talleres)",
    load: 12400,
    status: "warning",
  },
  {
    id: "bloque-c",
    label: "Bloque C (Sistemas)",
    load: 8200,
    status: "nominal",
  },
  { id: "admin", label: "Área Administrativa", load: 1500, status: "nominal" },
]);

// Mock de alertas que vendrán de tu backend
const centerAlerts = ref([
  {
    id: 101,
    severity: "critical",
    message: "Caída de tensión severa detectada en Bloque B.",
    source: "Transformador Principal",
    timestamp: "Hace 5 min",
  },
  {
    id: 102,
    severity: "warning",
    message: "Consumo inusual (fuera de horario) en Ambiente 305.",
    source: "Analítica MongoDB",
    timestamp: "03:00 AM",
  },
]);

const handleGlobalResolution = (alertId) => {
  centerAlerts.value = centerAlerts.value.filter(
    (alert) => alert.id !== alertId,
  );
};

// Pequeña protección de ruta a nivel de componente
onMounted(() => {
  if (!hasRole(["dinamizador"])) {
    router.push("/route-selector");
  }
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString();
  }, 1000);
});
</script>

<template>
  <div class="dashboard-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="logo-duo">
          <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
          <div class="logo-divider" />
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind"
            class="logo-volt"
          />
        </div>
        <div class="environment-badge">
          <h1>CONSOLA GLOBAL DE EFICIENCIA</h1>
          <p class="header-meta">
            Centro de Formación | Rol: Dinamizador Energético |
            <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>

      <button class="btn-dev-back" @click="router.push('/route-selector')">
        <font-awesome-icon icon="fa-solid fa-code" /> Cambiar Rol
      </button>
    </header>

    <main class="dash-grid admin-grid">
      <section class="dash-col">
        <div class="module-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-server" /> ESTADO DE LA RED
            ELÉCTRICA
          </h2>
          <div class="metrics-list">
            <div
              v-for="metric in globalMetrics"
              :key="metric.id"
              class="metric-row"
              :class="{ 'row-warning': metric.status === 'warning' }"
            >
              <span class="metric-label">{{ metric.label }}</span>
              <div class="metric-data">
                <span class="metric-val"
                  >{{ (metric.load / 1000).toFixed(1) }} <small>kW</small></span
                >
                <font-awesome-icon
                  :icon="
                    metric.status === 'warning'
                      ? 'fa-solid fa-arrow-trend-up'
                      : 'fa-solid fa-check'
                  "
                  class="status-icon"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-col">
        <AlertPanel
          title="ALERTAS DEL CENTRO"
          icon="fa-solid fa-tower-broadcast"
          :alerts="centerAlerts"
          @resolve="handleGlobalResolution"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Aprovechamos la misma estructura base del otro Dashboard para consistencia */
.dashboard-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  background-color: var(--fondo-app);
  padding: 1.5rem;
}
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}
.logo-duo {
  display: flex;
  align-items: center;
  gap: 16px;
}
.logo-sena {
  height: 44px;
}
.logo-volt {
  height: 40px;
}
.logo-divider {
  width: 1px;
  height: 28px;
  background: var(--borde);
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
.header-meta span {
  color: var(--sena-azul-oscuro);
  font-family: monospace;
  font-weight: 600;
}

.btn-dev-back {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-dev-back:hover {
  background: var(--sena-verde-oscuro);
}

.admin-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
@media (max-width: 992px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
}
.module-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Estilos de tabla de métricas macro */
.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-app);
  padding: 1rem 1.25rem;
  border-radius: 10px;
  border-left: 4px solid var(--sena-verde);
}
.metric-row.row-warning {
  border-left-color: var(--sena-amarillo);
  background: rgba(253, 195, 0, 0.05);
}
.metric-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
}
.metric-data {
  display: flex;
  align-items: center;
  gap: 12px;
}
.metric-val {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  font-family: monospace;
}
.metric-val small {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}
.status-icon {
  color: var(--sena-verde);
}
.row-warning .status-icon {
  color: var(--sena-amarillo);
}
</style>
