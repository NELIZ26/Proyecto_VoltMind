<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import AlertPanel from "@/components/AlertPanel.vue";
import { useRole } from "@/composables/useRole";

const router = useRouter();
const toast = useToast();
const { hasRole } = useRole();
const currentTime = ref(new Date().toLocaleTimeString());

// Estado de los ambientes bajo vigilancia (Enfoque de control perimetral)
const environmentsSurveillance = ref([
  {
    id: 402,
    bloque: "Bloque C",
    estado: "ENERGIZADO",
    consumo: 1420,
    anomalía: true,
    tipoAnomalía: "Consumo Fantasma",
  },
  {
    id: 403,
    bloque: "Bloque C",
    estado: "APAGADO",
    consumo: 0,
    anomalía: false,
    tipoAnomalía: "",
  },
  {
    id: 104,
    bloque: "Bloque A",
    estado: "APAGADO",
    consumo: 0,
    anomalía: false,
    tipoAnomalía: "",
  },
  {
    id: 201,
    bloque: "Bloque B",
    estado: "ENERGIZADO",
    consumo: 4200,
    anomalía: false,
    tipoAnomalía: "",
  },
]);

// Alertas específicas para el personal de seguridad
const securityAlerts = ref([
  {
    id: 201,
    severity: "critical",
    message:
      "Detección de consumo fantasma masivo en Ambiente 402 post-jornada.",
    source: "Sensor Nodo 402",
    timestamp: "10:14 PM",
  },
  {
    id: 202,
    severity: "info",
    message: "Bloque A reportado como cerrado y sin carga eléctrica.",
    source: "Cierre Maestro",
    timestamp: "09:30 PM",
  },
]);

const handleSecurityResolution = (alertId) => {
  securityAlerts.value = securityAlerts.value.filter(
    (alert) => alert.id !== alertId,
  );
  toast.success("Novedad registrada y archivada en la bitácora.");
};

// Protección de seguridad a nivel de componente
onMounted(() => {
  if (!hasRole(["celador", "dinamizador"])) {
    toast.error(
      "Acceso denegado. Perfil no autorizado para monitoreo perimetral.",
    );
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
          <h1>SISTEMA DE SEGURIDAD PERIFÉRICA</h1>
          <p class="header-meta">
            Monitoreo de Contingencias | Rol: Personal de Seguridad |
            <span>{{ currentTime }}</span>
          </p>
        </div>
      </div>

      <button class="btn-dev-back" @click="router.push('/route-selector')">
        <font-awesome-icon icon="fa-solid fa-code" /> Cambiar Rol
      </button>
    </header>

    <main class="dash-grid security-grid">
      <section class="dash-col">
        <div class="module-card">
          <h2 class="module-title">
            <font-awesome-icon icon="fa-solid fa-eye" /> ESTADO DE AMBIENTES EN
            TIEMPO REAL
          </h2>
          <p class="section-desc">
            Monitoreo de disyuntores activos fuera de la jornada formativa.
          </p>

          <div class="surveillance-list">
            <div
              v-for="env in environmentsSurveillance"
              :key="env.id"
              class="env-strip"
              :class="{ 'strip-anomaly': env.anomalía }"
            >
              <div class="env-info-block">
                <span class="env-name">AMBIENTE {{ env.id }}</span>
                <span class="env-sub">{{ env.bloque }}</span>
              </div>

              <div class="env-status-block">
                <span
                  class="badge-state"
                  :class="
                    env.estado === 'ENERGIZADO' ? 'state-on' : 'state-off'
                  "
                >
                  {{ env.estado }}
                </span>
                <span class="env-power-read" v-if="env.estado === 'ENERGIZADO'">
                  {{ env.consumo }}W
                </span>
              </div>

              <div class="env-alert-block" v-if="env.anomalía">
                <div class="anomaly-tag">
                  <font-awesome-icon icon="fa-solid fa-ghost" />
                  {{ env.tipoAnomalía }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="dash-col">
        <AlertPanel
          title="ALERTAS DE CONTINGENCIA"
          icon="fa-solid fa-shield-heart"
          :alerts="securityAlerts"
          @resolve="handleSecurityResolution"
        />

        <div class="module-card info-logs-card">
          <h3>
            <font-awesome-icon icon="fa-solid fa-clipboard-list" /> PROTOCOLO DE
            INCIDENCIAS
          </h3>
          <p>
            Al marcar una alerta como resuelta, el sistema guarda
            automáticamente tu ID de usuario, la hora exacta y el estado de la
            carga eléctrica en el Common Data Model de Dataverse para auditorías
            energéticas.
          </p>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* BASE Y REUTILIZACIÓN DE ESTILOS INSTITUCIONALES (CASO 1: BLANCO) */
.dashboard-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  background-color: var(--fondo-app);
  padding: 1.5rem;
  box-sizing: border-box;
}
.dash-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.logo-duo {
  display: flex;
  align-items: center;
  gap: 16px;
}
.logo-sena {
  height: 38px;
}
.logo-volt {
  height: 34px;
}
.logo-divider {
  width: 1px;
  height: 26px;
  background: var(--borde);
}
.environment-badge h1 {
  font-size: 1.25rem;
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

@media (min-width: 992px) {
  .dash-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  .header-left {
    flex-direction: row;
    gap: 2.5rem;
  }
  .environment-badge h1 {
    font-size: 1.4rem;
  }
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

/* GRID DISTRIBUCIÓN */
.security-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 992px) {
  .security-grid {
    grid-template-columns: 1fr 400px;
  }
}

.dash-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.02);
}
.module-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
}
.section-desc {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  margin: 4px 0 1.5rem 0;
  font-weight: 500;
}

/* LISTA DE VIGILANCIA PERIMETRAL */
.surveillance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.env-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--fondo-app);
  padding: 12px 18px;
  border-radius: 12px;
  border: 1px solid var(--borde);
  flex-wrap: wrap;
  gap: 12px;
  transition: transform 0.2s ease;
}
.env-strip:hover {
  transform: translateX(3px);
}

/* Alerta de Consumo Vampiro Nocturno */
.strip-anomaly {
  border-color: var(--sena-amarillo);
  background: rgba(253, 195, 0, 0.04);
}

.env-info-block {
  display: flex;
  flex-direction: column;
  min-width: 120px;
}
.env-name {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}
.env-sub {
  font-size: 0.65rem;
  color: var(--texto-secundario);
  font-weight: 600;
  text-transform: uppercase;
  margin-top: 2px;
}

.env-status-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.badge-state {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}
.state-on {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
}
.state-off {
  background: #e2e8f0;
  color: var(--texto-secundario);
}
.env-power-read {
  font-family: monospace;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-principal);
}

.anomaly-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 6px 12px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  animation: flashBorder 2s infinite alternate;
}

@keyframes flashBorder {
  0% {
    box-shadow: 0 0 4px rgba(229, 62, 62, 0.2);
  }
  100% {
    box-shadow: 0 0 10px rgba(229, 62, 62, 0.4);
  }
}

/* BITÁCORA AUXILIAR */
.info-logs-card {
  background: var(--fondo-app);
  border-style: dashed;
}
.info-logs-card h3 {
  font-size: 0.75rem;
  color: var(--sena-azul-oscuro);
  font-weight: 800;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.info-logs-card p {
  font-size: 0.7rem;
  color: var(--texto-secundario);
  line-height: 1.4;
  margin: 0;
  font-weight: 500;
}
</style>
