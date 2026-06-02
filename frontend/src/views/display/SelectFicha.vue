<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { useRole } from "@/composables/useRole";

const router = useRouter();
const toast = useToast();
const { hasRole } = useRole();

// Estado para la animación de carga
const connectingId = ref(null);

// Variables reactivas
const fichas = ref([]);
const isLoading = ref(true);

// 1. UNIFICAMOS EL CICLO DE VIDA (Protección + Consulta)
onMounted(async () => {
  // A) Primero protegemos la ruta (Lógica del equipo)
  if (!hasRole(["instructor", "dinamizador"])) {
    toast.error("Acceso denegado. Se requiere credencial de Instructor.");
    router.push("/route-selector");
    return; // Detenemos la ejecución si no tiene permiso
  }

  // B) Luego hacemos tu consulta a la base de datos (Tu lógica)
  const correoInstructor = localStorage.getItem('instructorEmail');

  if (!correoInstructor) {
    toast.error("No se encontró la sesión del instructor. Volviendo al inicio.");
    router.push("/route-selector");
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/api/fichas/${correoInstructor}`);
    
    if (!response.ok) {
      throw new Error("No se encontraron fichas para este instructor.");
    }
    
    const data = await response.json();
    
    // Mapeamos para el diseño
    fichas.value = data.map((ficha, index) => ({
      id: index + 1,
      numero: ficha.numero_ficha,
      programa: ficha.nombre_programa,
      instructor: ficha.instructor, // Aseguramos traer al instructor del backend
      jornada: "Asignada"
    }));

  } catch (error) {
    console.error("Error consultando la base de datos:", error);
    toast.error("No se pudieron cargar las fichas asignadas.");
  } finally {
    isLoading.value = false;
  }
});

// 2. ARREGLAMOS LA FUNCIÓN DE SELECCIÓN (Animación + Guardado real)
const seleccionarFicha = (ficha) => {
  console.log("Iniciando sincronización con ficha:", ficha); 
  
  // A) Activamos la animación de tu equipo INMEDIATAMENTE
  connectingId.value = ficha.id;
  toast.info(`Sincronizando Ambiente 402 con Ficha ${ficha.numero}...`);

  // B) Preparamos TUS datos correctos para Dataverse
  const numeroAguardar = ficha.numero || "Sin Número";
  const programaAguardar = ficha.programa || "Programa no definido";
  const instructorAguardar = ficha.instructor || localStorage.getItem('instructorEmail') || "Instructor SENA";

  // C) Simulamos la carga y luego guardamos (Unimos ambos mundos)
  setTimeout(() => {
    // Guardamos tus variables limpias para el Dashboard
    localStorage.setItem('fichaActiva', numeroAguardar);
    localStorage.setItem('nombrePrograma', programaAguardar); 
    localStorage.setItem('nombreInstructor', instructorAguardar); 

    toast.success("Conexión establecida. Iniciando telemetría.");
    
    // D) Hacemos UN SOLO redireccionamiento al final
    router.push('/dashboard');
  }, 1200);
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
        <button
          v-for="ficha in fichas"
          :key="ficha.id"
          class="ficha-card"
          :class="{ 'is-connecting': connectingId === ficha.id }"
          :disabled="connectingId !== null"
          @click="seleccionarFicha(ficha)"
        >
          <div v-if="connectingId === ficha.id" class="connecting-overlay">
            <font-awesome-icon
              icon="fa-solid fa-circle-notch"
              spin
              class="spinner-icon"
            />
            <span>Sincronizando...</span>
          </div>

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
        </button>
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
/* (MANTÉN TU CSS ORIGINAL AQUÍ HASTA ".ficha-card:hover") */
.select-shell {
  min-height: 100vh;
  background: var(--fondo-app);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  font-family: var(--fuente-principal);
  position: relative;
  overflow: hidden;
}
.select-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 48, 64, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 48, 64, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black, transparent 80%);
  pointer-events: none;
  z-index: 0;
}
.select-container {
  width: 100%;
  max-width: 1100px;
  position: relative;
  z-index: 1;
}
.select-header {
  margin-bottom: 3.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
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
  filter: drop-shadow(0 2px 4px rgba(0, 48, 64, 0.08));
}
.logo-sena {
  height: 42px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 48, 64, 0.08));
}
.brand-divider {
  width: 1px;
  height: 28px;
  background: var(--borde);
}
.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.08);
  border: 1px solid rgba(57, 169, 0, 0.2);
  padding: 6px 14px;
  border-radius: 8px;
  color: var(--sena-verde-oscuro);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  margin-bottom: 1.25rem;
}
.select-header h1 {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--sena-azul-oscuro);
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem 0;
}
.instruction {
  font-size: 0.95rem;
  color: var(--texto-secundario);
  font-weight: 500;
}
.fichas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

/* AJUSTES A LA TARJETA PARA SOPORTAR EL ESTADO DE CARGA */
.ficha-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.75rem;
  text-align: left;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 240px;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  font-family: inherit; /* Heredar fuente al ser un <button> ahora */
}

.ficha-card:hover:not(:disabled) {
  transform: translateY(-6px);
  background: var(--sena-blanco);
  border-color: var(--sena-verde);
  box-shadow:
    0 12px 24px rgba(0, 48, 64, 0.08),
    0 0 0 1px var(--sena-verde);
}

.ficha-card:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* --- OVERLAY DE CARGA (NUEVO) --- */
.connecting-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--sena-verde-oscuro);
  font-weight: 700;
  font-size: 0.85rem;
}

.spinner-icon {
  font-size: 2rem;
  color: var(--sena-verde);
}

.is-connecting {
  border-color: var(--sena-verde) !important;
  transform: scale(0.98);
}

/* (RESTO DE TU CSS ORIGINAL) */
.card-status {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 0.6rem;
  font-weight: 800;
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  letter-spacing: 0.08em;
}
.card-icon {
  width: 48px;
  height: 48px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--sena-azul-oscuro);
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}
.ficha-card:hover:not(:disabled) .card-icon {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border-color: var(--sena-verde);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.3);
}
.label {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.ficha-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}
.program-name {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  line-height: 1.4;
  margin: 0;
  font-weight: 500;
}
.card-footer {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--fondo-app);
  padding-top: 1rem;
  width: 100%;
}
.jornada-tag {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--sena-verde-oscuro);
  text-transform: uppercase;
}
.arrow {
  font-size: 0.9rem;
  color: var(--borde);
  transition: all 0.3s ease;
}
.ficha-card:hover:not(:disabled) .arrow {
  color: var(--sena-verde);
  transform: translateX(5px);
}
.select-footer {
  margin-top: 4rem;
  text-align: center;
}
.btn-back {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 48, 64, 0.03);
}
.btn-back:hover {
  border-color: var(--sena-azul-oscuro);
  color: var(--sena-blanco);
  background: var(--sena-azul-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 48, 64, 0.15);
}
</style>
