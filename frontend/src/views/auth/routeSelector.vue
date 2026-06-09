<script setup>
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import DarkModeToggle from "@/components/DarkModeToggle.vue";

const router = useRouter();
const toast = useToast();

// Mapeo de entornos de desarrollo con sus roles asociados (Limpio y fusionado)
const devLogins = [
  {
    role: "dinamizador",
    path: "/dashboard-admin",
    name: "Dinamizador Energético",
    desc: "Panel de Superadmin. Analítica macro, topología global y MongoDB.",
    icon: "globe",
    color: "var(--sena-azul-oscuro, #003040)",
    glow: "rgba(0, 48, 64, 0.25)",
  },
  {
    role: "instructor",
    path: "/select-ficha", 
    name: "Instructor de Ambiente",
    desc: "Gestión local de energía, puente IoT y control de asistencia.",
    icon: "chalkboard-user",
    color: "var(--sena-verde, #39a900)",
    glow: "rgba(57, 169, 0, 0.25)",
  },
  {
    // Tu acceso directo al Dashboard, ahora estructurado con un rol para que no colapse Vue
    role: "instructor_directo",
    path: "/dashboard",
    name: "Dashboard (Acceso Directo)",
    desc: "Centro de control IoT, mapa de carga eléctrica y asistencia en vivo.",
    icon: "microchip",
    color: "var(--sena-verde, #39a900)",
    glow: "rgba(57, 169, 0, 0.25)"
  },
  {
    role: "celador",
    path: "/dashboard-seguridad",
    name: "Personal de Seguridad",
    desc: "Panel simplificado de monitoreo periférico y alertas de contingencia.",
    icon: "shield-halved",
    color: "var(--sena-amarillo, #FDC300)",
    glow: "rgba(253, 195, 0, 0.25)",
  },
  {
    role: "aprendiz",
    path: "/card",
    name: "Aprendiz (Cliente)",
    desc: "Vista Mobile-first. Identidad virtual, emisión NFC y PIN dinámico.",
    icon: "address-card",
    color: "var(--sena-naranja, #FF6B00)",
    glow: "rgba(255, 107, 0, 0.25)",
  }
];

const simulateLogin = (devAccount) => {
  // 1. Quemamos el rol temporalmente en el entorno local
  localStorage.setItem("user_role", devAccount.role);

  // 2. Notificación de éxito
  toast.success(`Sesión de desarrollo: ${devAccount.name}`);

  // 3. Redirección al flujo correspondiente
  router.push(devAccount.path);
};
</script>

<template>
  <div class="selector-shell">
    <div class="selector-container">
      <header class="selector-header">
        <div class="brand-wrapper">
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind"
            class="brand-logo"
          />
          <span class="badge-status-dev">SANDBOX v2.0</span>
        </div>
        <h2>SIMULADOR DE ROLES</h2>
        <div class="status-message">
          <div class="pulse-dot"></div>
          <p>Auth Mock Activo. Seleccione un perfil para inyectar permisos:</p>
        </div>
      </header>

      <div class="routes-grid">
        <button
          v-for="account in devLogins"
          :key="account.role"
          class="route-card"
          :style="{
            '--card-color': account.color,
            '--card-glow': account.glow,
          }"
          @click="simulateLogin(account)"
        >
          <div class="icon-wrap">
            <font-awesome-icon :icon="['fas', account.icon]" />
          </div>

          <div class="card-text">
            <div class="card-title-row">
              <h3>{{ account.name }}</h3>
              <span class="path-label"
                >Rol: {{ account.role.toUpperCase() }}</span
              >
            </div>
            <p>{{ account.desc }}</p>
          </div>

          <div class="arrow-indicator">
            <font-awesome-icon icon="fa-solid fa-arrow-right-to-bracket" />
          </div>
        </button>
      </div>

      <footer class="selector-footer-info">
        <p>VoltMind Access Core • Entorno Local de Pruebas (RBAC)</p>
      </footer>
    </div>
    <DarkModeToggle />
  </div>
</template>

<style scoped>
/* (Mantén el mismo CSS que ya tenías en tu archivo routeSelector original, es perfecto) */
.selector-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: var(--fondo-app);
  font-family: var(--fuente-principal);
  position: relative;
  overflow: hidden;
}
.selector-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 48, 64, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 48, 64, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black, transparent 70%);
  pointer-events: none;
}
.selector-container {
  width: 100%;
  max-width: 680px;
  position: relative;
  z-index: 2;
}
.selector-header {
  margin-bottom: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.25rem;
}
.brand-logo {
  height: 38px;
  filter: drop-shadow(0 2px 4px rgba(0, 48, 64, 0.1));
}
.badge-status-dev {
  background: var(--sena-blanco);
  border: 1px solid var(--borde);
  color: var(--sena-azul-oscuro);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.selector-header h2 {
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  color: var(--texto-principal);
  margin: 0 0 0.75rem 0;
}
.status-message {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(57, 169, 0, 0.08);
  border: 1px solid rgba(57, 169, 0, 0.2);
  padding: 6px 14px;
  border-radius: 20px;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  background-color: var(--sena-verde);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--sena-verde);
  animation: telemetryPulse 1.8s infinite;
}
@keyframes telemetryPulse {
  50% {
    opacity: 0.3;
    transform: scale(0.9);
  }
}
.status-message p {
  color: var(--sena-verde-oscuro);
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0;
}
.routes-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.route-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  text-align: left;
  cursor: pointer;
  width: 100%;
  color: var(--texto-principal);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
}
.route-card:hover {
  background: var(--sena-blanco);
  border-color: var(--card-color, var(--sena-verde));
  transform: translateY(-2px);
  box-shadow:
    0 12px 30px -10px var(--card-glow, rgba(57, 169, 0, 0.2)),
    0 0 0 1px var(--card-color, var(--sena-verde));
}
.icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-right: 1.25rem;
  flex-shrink: 0;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  transition: all 0.3s ease;
}
.route-card:hover .icon-wrap {
  color: var(--sena-blanco);
  background: var(--card-color, var(--sena-verde));
  border-color: var(--card-color, var(--sena-verde));
  box-shadow: 0 4px 12px var(--card-glow, rgba(57, 169, 0, 0.3));
}
.card-text {
  flex: 1;
}
.card-title-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}
.card-text h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--texto-principal);
  margin: 0;
}
.path-label {
  font-family: monospace;
  font-size: 0.7rem;
  color: var(--texto-secundario);
  opacity: 0.7;
}
.route-card:hover .path-label {
  color: var(--card-color, var(--sena-verde));
  opacity: 1;
}
.card-text p {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0;
  line-height: 1.4;
}
.arrow-indicator {
  color: var(--borde);
  font-size: 1.05rem;
  transition: all 0.3s ease;
  margin-left: 1.25rem;
}
.route-card:hover .arrow-indicator {
  color: var(--card-color, var(--sena-verde));
  transform: translateX(5px);
}
.route-card:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px -5px var(--card-glow, rgba(57, 169, 0, 0.1));
}
.selector-footer-info {
  margin-top: 3rem;
  text-align: center;
}
.selector-footer-info p {
  font-size: 0.75rem;
  color: var(--texto-secundario);
  letter-spacing: 0.02em;
  margin: 0;
}
</style>
