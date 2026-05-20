<script setup>
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

const routes = [
  {
    path: '/select-ficha',
    name: 'Selección de Ficha',
    desc: 'Panel para que el instructor elija el grupo y ambiente de formación.',
    icon: 'fa-graduation-cap',
    color: 'var(--sena-azul, #00324d)',
    glow: 'rgba(0, 50, 77, 0.25)'
  },
  {
    path: '/dashboard',
    name: 'Dashboard de la Tablet',
    desc: 'Centro de control IoT, mapa de carga eléctrica y asistencia en vivo.',
    icon: 'fa-microchip',
    color: 'var(--sena-verde, #39a900)',
    glow: 'rgba(57, 169, 0, 0.25)'
  },
  {
    path: '/card',
    name: 'Carnet de Aprendiz',
    desc: 'Vista móvil del carnet digital con el código QR dinámico y token.',
    icon: 'fa-address-card',
    color: 'var(--sena-naranja, #FF6B00)',
    glow: 'rgba(255, 107, 0, 0.25)'
  }
]

const navigateTo = (path, name) => {
  toast.info(`Navegando a: ${name}`)
  router.push(path)
}
</script>

<template>
  <div class="selector-shell">
    <div class="selector-container">
      
      <header class="selector-header">
        <div class="brand-wrapper">
          <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="brand-logo" />
          <span class="badge-status-dev">SANDBOX v2.0</span>
        </div>
        <h2>ENTORNO DE DESARROLLO</h2>
        <div class="status-message">
          <div class="pulse-dot"></div>
          <p>Azure Control Mock exitoso. Selecciona la interfaz que deseas verificar:</p>
        </div>
      </header>

      <div class="routes-grid">
        <button 
          v-for="route in routes" 
          :key="route.path" 
          class="route-card"
          :style="{ '--card-color': route.color, '--card-glow': route.glow }"
          @click="navigateTo(route.path, route.name)"
        >
          <div class="icon-wrap">
            <font-awesome-icon :icon="['fas', route.icon]" />
          </div>
          
          <div class="card-text">
            <div class="card-title-row">
              <h3>{{ route.name }}</h3>
              <span class="path-label">{{ route.path }}</span>
            </div>
            <p>{{ route.desc }}</p>
          </div>
          
          <div class="arrow-indicator">
            <font-awesome-icon icon="fa-solid fa-arrow-right-to-bracket" />
          </div>
        </button>
      </div>

      <footer class="selector-footer-info">
        <p>VoltMind Access Core • Entorno Local de Pruebas</p>
      </footer>

    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   ESTRUCTURA DE CONTEXTO PRINCIPAL (SHELL GLOBAL)
   ========================================================================== */
.selector-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: radial-gradient(circle at center, #101014 0%, #070709 100%);
  font-family: var(--fuente-principal, "Inter", sans-serif);
  position: relative;
  overflow: hidden;
}

/* Líneas decorativas de fondo emulando cuadrícula de hardware (Opcional/Minimalista) */
.selector-shell::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
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

/* ==========================================================================
   SECCIÓN DE ENCABEZADO (TERMINAL HEADER)
   ========================================================================== */
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
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));
}

.badge-status-dev {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--texto-secundario, #a0aec0);
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
  color: var(--texto-principal, #ffffff);
  margin: 0 0 0.75rem 0;
}

/* Barra de Estado Exitoso */
.status-message {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(57, 169, 0, 0.04);
  border: 1px solid rgba(57, 169, 0, 0.12);
  padding: 6px 14px;
  border-radius: 20px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background-color: var(--sena-verde, #39a900);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--sena-verde, #39a900);
  animation: telemetryPulse 1.8s infinite;
}

@keyframes telemetryPulse {
  50% { opacity: 0.3; transform: scale(0.9); }
}

.status-message p {
  color: var(--sena-verde-claro, #deff9a);
  font-size: 0.8rem;
  font-weight: 500;
  margin: 0;
}

/* ==========================================================================
   CONSOLA DE BOTONES / TARJETAS (ROUTES GRID)
   ========================================================================== */
.routes-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.route-card {
  background: #0d0d0f;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.06));
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  text-align: left;
  cursor: pointer;
  width: 100%;
  color: var(--texto-principal, #ffffff);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

/* Hover de la Tarjeta */
.route-card:hover {
  background: #121216;
  border-color: var(--card-color);
  transform: translateY(-2px);
  box-shadow: 0 12px 30px -10px var(--card-glow),
              inset 0 1px 0px rgba(255, 255, 255, 0.1);
}

/* Envoltura del Icono */
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
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: var(--texto-secundario, #a0aec0);
  transition: all 0.3s ease;
}

.route-card:hover .icon-wrap {
  color: #ffffff;
  background: var(--card-color);
  border-color: var(--card-color);
  box-shadow: 0 0 12px var(--card-glow);
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
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--texto-principal, #ffffff);
  margin: 0;
}

/* Indicador de Ruta Física */
.path-label {
  font-family: monospace;
  font-size: 0.7rem;
  color: var(--texto-secundario, #a0aec0);
  opacity: 0.5;
}

.route-card:hover .path-label {
  color: var(--card-color);
  opacity: 0.8;
}

.card-text p {
  font-size: 0.8rem;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  line-height: 1.4;
  opacity: 0.85;
}

/* Flecha de Navegación Derecha */
.arrow-indicator {
  color: var(--borde, rgba(255, 255, 255, 0.1));
  font-size: 1.05rem;
  transition: all 0.3s ease;
  margin-left: 1.25rem;
}

.route-card:hover .arrow-indicator {
  color: var(--card-color);
  transform: translateX(5px);
}

/* Clic Activo Físico */
.route-card:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px -5px var(--card-glow);
}

/* ==========================================================================
   FOOTER INFORMATIVO SUTIL
   ========================================================================== */
.selector-footer-info {
  margin-top: 3rem;
  opacity: 0.3;
}

.selector-footer-info p {
  font-size: 0.7rem;
  color: var(--texto-secundario, #a0aec0);
  letter-spacing: 0.02em;
  margin: 0;
}
</style>