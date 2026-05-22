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
   ESTRUCTURA DE CONTEXTO PRINCIPAL (Caso 1: Blanco SENA 2024)
   ========================================================================== */
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

/* Líneas decorativas sutiles adaptadas al fondo claro usando el azul oscuro SENA */
.selector-shell::before {
  content: '';
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
  filter: drop-shadow(0 2px 4px rgba(0, 48, 64, 0.1)); /* Sombra ajustada a claro */
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

/* Barra de Estado Exitoso - Adaptada con el Verde Oficial */
.status-message {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: rgba(57, 169, 0, 0.08); /* Verde con baja opacidad */
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
  50% { opacity: 0.3; transform: scale(0.9); }
}

.status-message p {
  color: var(--sena-verde-oscuro);
  font-size: 0.8rem;
  font-weight: 700;
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
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03); /* Sombra sutil de profundidad */
}

/* Hover de la Tarjeta - Usando colores dinámicos si están definidos inline, si no, fallback al verde SENA */
.route-card:hover {
  background: var(--sena-blanco);
  border-color: var(--card-color, var(--sena-verde));
  transform: translateY(-2px);
  box-shadow: 0 12px 30px -10px var(--card-glow, rgba(57, 169, 0, 0.2)),
              0 0 0 1px var(--card-color, var(--sena-verde));
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

/* Indicador de Ruta Física */
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

/* Flecha de Navegación Derecha */
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

/* Clic Activo Físico */
.route-card:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px -5px var(--card-glow, rgba(57, 169, 0, 0.1));
}

/* ==========================================================================
   FOOTER INFORMATIVO SUTIL
   ========================================================================== */
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