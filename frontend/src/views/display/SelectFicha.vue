<script setup>
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

const router = useRouter();
const toast = useToast();

const fichas = [
  {
    id: 1,
    numero: "2997671",
    programa: "Análisis y Desarrollo de Software",
    jornada: "Mañana",
  },
  { id: 2, numero: "2800500", programa: "Sistemas", jornada: "Tarde" },
  {
    id: 3,
    numero: "3001234",
    programa: "Gestión Administrativa",
    jornada: "Mañana",
  },
  {
    id: 4,
    numero: "2856789",
    programa: "Mantenimiento de Equipos de Cómputo",
    jornada: "Noche",
  },
];

const seleccionarFicha = (ficha) => {
  toast.success(`Ambiente Vinculado: Ficha ${ficha.numero}`);
  // Simulación de carga de sesión en el ecosistema
  router.push("/dashboard");
};
</script>

<template>
  <div class="select-shell">
    <div class="select-container">
      <header class="select-header">
        <div class="brand-assets-header">
          <img
            src="@/assets/VoltMindAccess.svg"
            alt="VoltMind Logo"
            class="logo-voltmind"
          />
          <div class="brand-divider"></div>
          <img src="@/assets/LogoSena.png" alt="SENA Logo" class="logo-sena" />
        </div>

        <div class="location-badge">
          <font-awesome-icon icon="fa-solid fa-location-dot" />
          <span>AMBIENTE 402 • BLOQUE C</span>
        </div>
        <h1>PANEL DE CONTROL VOLTMIND</h1>
        <p class="instruction">
          Seleccione el grupo que inicia sesión técnica en este ambiente:
        </p>
      </header>

      <div class="fichas-grid">
        <div
          v-for="ficha in fichas"
          :key="ficha.id"
          class="ficha-card"
          @click="seleccionarFicha(ficha)"
        >
          <div class="card-status">READY</div>

          <div class="card-icon">
            <font-awesome-icon icon="fa-solid fa-user-check" />
          </div>

          <div class="card-info">
            <span class="label">NÚMERO DE FICHA</span>
            <h2 class="ficha-number">{{ ficha.numero }}</h2>
            <p class="program-name">{{ ficha.programa }}</p>
          </div>

          <div class="card-footer">
            <span class="jornada-tag">{{ ficha.jornada }}</span>
            <font-awesome-icon icon="fa-solid fa-chevron-right" class="arrow" />
          </div>
        </div>
      </div>

      <footer class="select-footer">
        <button class="btn-back" @click="router.push('/route-selector')">
          <font-awesome-icon icon="fa-solid fa-arrow-left" /> REGRESAR AL
          SELECTOR
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   CONSOLA DE SELECCIÓN DE FICHA (VoltMind Access Premium UI)
   ========================================================================== */
.select-shell {
  min-height: 100vh;
  background: radial-gradient(circle at center, #111115 0%, #060608 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  font-family: var(--fuente-principal, "Inter", sans-serif);
}

.select-container {
  width: 100%;
  max-width: 1100px;
}

/* Encabezado de la Consola */
.select-header {
  margin-bottom: 3.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ── ESTILOS PARA LA SECCIÓN DE LOGOS ── */
.brand-assets-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 2rem;
}

.logo-voltmind {
  height: 38px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.logo-sena {
  height: 42px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.brand-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.08);
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 14px;
  border-radius: 6px;
  color: var(--sena-verde, #39a900);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  margin-bottom: 1.25rem;
}

.select-header h1 {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--texto-principal, #ffffff);
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem 0;
}

.instruction {
  font-size: 0.9rem;
  color: var(--texto-secundario, #a0aec0);
  opacity: 0.7;
}

/* Grilla de Tarjetas */
.fichas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

/* Estilo Premium de la Tarjeta */
.ficha-card {
  background: #0d0d0f;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  padding: 1.75rem;
  text-align: left;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 240px;
}

.ficha-card:hover {
  transform: translateY(-8px);
  background: #121215;
  border-color: var(--sena-verde, #39a900);
  box-shadow: 0 20px 40px -15px rgba(57, 169, 0, 0.25);
}

/* Micro-Indicador de Estado */
.card-status {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 0.6rem;
  font-weight: 900;
  color: var(--sena-verde, #39a900);
  opacity: 0.5;
  letter-spacing: 0.1em;
}

.card-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--texto-secundario, #a0aec0);
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}

.ficha-card:hover .card-icon {
  background: var(--sena-verde, #39a900);
  color: white;
  border-color: var(--sena-verde, #39a900);
  box-shadow: 0 0 15px rgba(57, 169, 0, 0.3);
}

.label {
  display: block;
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--texto-secundario, #a0aec0);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.ficha-number {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--texto-principal, #ffffff);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.program-name {
  font-size: 0.85rem;
  color: var(--texto-secundario, #a0aec0);
  line-height: 1.4;
  margin: 0;
  opacity: 0.8;
}

/* Footer de la Tarjeta */
.card-footer {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 1rem;
}

.jornada-tag {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--sena-verde-claro, #deff9a);
  text-transform: uppercase;
}

.arrow {
  font-size: 0.8rem;
  color: var(--borde, rgba(255, 255, 255, 0.1));
  transition: transform 0.3s ease;
}

.ficha-card:hover .arrow {
  color: var(--sena-verde, #39a900);
  transform: translateX(5px);
}

/* Botón de Regreso */
.select-footer {
  margin-top: 4rem;
  text-align: center;
}

.btn-back {
  background: transparent;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  color: var(--texto-secundario, #a0aec0);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.btn-back:hover {
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--texto-principal, #ffffff);
  background: rgba(255, 255, 255, 0.02);
}
</style>