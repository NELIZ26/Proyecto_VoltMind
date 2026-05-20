<script setup>
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

const router = useRouter();
const toast = useToast();

const handleAzureLogin = () => {
  // 1. Simulación de respuesta exitosa del Active Directory de Azure
  toast.success("Autenticación institucional exitosa con Microsoft");

  // 2. Despacho inmediato hacia el entorno de desarrollo / selector de interfaces
  router.push("/route-selector");
};
</script>

<template>
  <div class="login-shell">
    <div class="login-card">
      <div class="card-corner top-left"></div>
      <div class="card-corner bottom-right"></div>

      <header class="login-header">
        <div class="brand-assets">
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind Logo"
            class="logo-voltmind"
          />
          <div class="brand-divider"></div>
          <img src="@/assets/LogoSena.png" alt="SENA Logo" class="logo-sena" />
        </div>
        <h1>VoltMind Access</h1>
        <p class="subtitle">
          Gestión IoT de Asistencia y Eficiencia Energética para Ambientes de
          Formación
        </p>
      </header>

      <main class="login-body">
        <div class="notice-box">
          <div class="icon-glow-wrapper">
            <font-awesome-icon
              icon="fa-solid fa-shield-halved"
              class="icon-notice"
            />
          </div>
          <div class="notice-text">
            <span>SISTEMA DE CONTROL RESTRINGIDO</span>
            <p>
              Acceso exclusivo para Instructores y Personal Administrativo
              autorizado.
            </p>
          </div>
        </div>

        <button class="btn-azure" @click="handleAzureLogin">
          <div class="microsoft-icon">
            <span class="ms-box red"></span>
            <span class="ms-box green"></span>
            <span class="ms-box blue"></span>
            <span class="ms-box yellow"></span>
          </div>
          <span>Autenticación Institucional Azure AD</span>
        </button>
      </main>

      <footer class="login-footer">
        <p>&copy; 2026 VoltMind Ecosystem. Todos los derechos reservados.</p>
        <div class="terminal-badge">
          <span class="pulse-dot"></span>
          <small>ESTACIÓN DE CONTROL LOCAL • TABLET ED. v2.4</small>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   CONSOLA DE AUTENTICACIÓN - TERMINAL PRINCIPAL (VoltMind Access UI)
   ========================================================================== */
.login-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: radial-gradient(circle at center, #111115 0%, #060608 100%);
  font-family: var(--fuente-principal, "Inter", sans-serif);
  position: relative;
}

/* Rejilla de fondo emulando trazado electrónico sutil */
.login-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.006) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.006) 1px, transparent 1px);
  background-size: 30px 30px;
  mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
  pointer-events: none;
}

.login-card {
  background: linear-gradient(145deg, #0a0a0c 0%, #0e0e12 100%);
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.06));
  border-radius: 18px;
  width: 100%;
  max-width: 450px;
  padding: 3rem 2.25rem;
  text-align: center;
  box-shadow:
    0 30px 60px -15px rgba(0, 0, 0, 0.8),
    inset 0 1px 0px rgba(255, 255, 255, 0.05);
  position: relative;
  transition:
    border-color 0.4s ease,
    box-shadow 0.4s ease;
}

/* Efecto Hover predictivo en la tarjeta global */
.login-card:hover {
  border-color: rgba(57, 169, 0, 0.2);
  box-shadow:
    0 30px 60px -15px rgba(0, 0, 0, 0.9),
    0 0 40px -10px rgba(57, 169, 0, 0.05),
    inset 0 1px 0px rgba(255, 255, 255, 0.05);
}

/* Micro-Detalles de Esquinas Industriales */
.card-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 2px solid transparent;
  pointer-events: none;
  opacity: 0.3;
  transition: opacity 0.3s ease;
}
.login-card:hover .card-corner {
  opacity: 0.7;
}

.top-left {
  top: 14px;
  left: 14px;
  border-top-color: var(--texto-secundario, #a0aec0);
  border-left-color: var(--texto-secundario, #a0aec0);
}
.bottom-right {
  bottom: 14px;
  right: 14px;
  border-bottom-color: var(--sena-verde, #39a900);
  border-right-color: var(--sena-verde, #39a900);
}

/* ==========================================================================
   IDENTIDAD VISUAL SUPERIOR (BRAND HEADER)
   ========================================================================== */
.brand-assets {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 1.75rem;
}

.logo-voltmind {
  height: 34px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.logo-sena {
  height: 38px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.brand-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
}

.login-header h1 {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--texto-principal, #ffffff);
  margin: 0 0 0.6rem 0;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--texto-secundario, #a0aec0);
  line-height: 1.5;
  margin: 0;
  opacity: 0.75;
  padding: 0 10px;
}

/* ==========================================================================
   CUERPO DE ACCIÓN (LOGIN CORE)
   ========================================================================== */
.login-body {
  margin: 2.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Caja de Aviso Técnico */
.notice-box {
  background: rgba(0, 50, 77, 0.12);
  border: 1px solid rgba(0, 50, 77, 0.35);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
}

.icon-glow-wrapper {
  background: rgba(255, 107, 0, 0.06);
  border: 1px solid rgba(255, 107, 0, 0.15);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-notice {
  color: var(--sena-naranja, #ff6b00);
  font-size: 1rem;
}

.notice-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notice-text span {
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--sena-naranja, #ff6b00);
  letter-spacing: 0.05em;
}

.notice-text p {
  font-size: 0.75rem;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  line-height: 1.35;
  opacity: 0.85;
}

/* ==========================================================================
   BOTÓN ACRÍLICO PERSONALIZADO (AZURE INTEGRATION)
   ========================================================================== */
.btn-azure {
  background: rgba(255, 255, 255, 0.03);
  color: var(--texto-principal, #ffffff);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(4px);
  padding: 13px 18px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-azure:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.4),
    inset 0 1px 0px rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.btn-azure:active {
  transform: translateY(0);
  background: rgba(255, 255, 255, 0.02);
}

/* Icono Nativo Centrado */
.microsoft-icon {
  width: 16px;
  height: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2px;
  flex-shrink: 0;
}

.ms-box {
  width: 7px;
  height: 7px;
}
.ms-box.red {
  background-color: #f25022;
  filter: drop-shadow(0 0 2px rgba(242, 80, 34, 0.4));
}
.ms-box.green {
  background-color: #7fba00;
  filter: drop-shadow(0 0 2px rgba(127, 186, 0, 0.4));
}
.ms-box.blue {
  background-color: #00a4ef;
  filter: drop-shadow(0 0 2px rgba(0, 164, 239, 0.4));
}
.ms-box.yellow {
  background-color: #ffb900;
  filter: drop-shadow(0 0 2px rgba(255, 185, 0, 0.4));
}

/* ==========================================================================
   FOOTER CORPORATIVO DE LA TERMINAL
   ========================================================================== */
.login-footer {
  border-top: 1px solid var(--borde, rgba(255, 255, 255, 0.06));
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.login-footer p {
  font-size: 0.68rem;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  opacity: 0.4;
}

/* Badge de Estado Activo Local */
.terminal-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.05);
  border: 1px solid rgba(57, 169, 0, 0.15);
  padding: 4px 10px;
  border-radius: 4px;
}

.pulse-dot {
  width: 5px;
  height: 5px;
  background-color: var(--sena-verde, #39a900);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--sena-verde, #39a900);
  animation: hardwarePulse 2s infinite;
}

@keyframes hardwarePulse {
  50% {
    opacity: 0.3;
  }
}

.terminal-badge small {
  font-size: 0.6rem;
  color: var(--sena-verde-claro, #deff9a);
  font-weight: 700;
  letter-spacing: 0.04em;
}
</style>
