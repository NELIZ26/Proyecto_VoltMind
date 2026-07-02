<script setup>
const BASE_URL = import.meta.env.VITE_API_BASE_URL;
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { useRole } from "@/composables/useRole";
import DarkModeToggle from "@/components/DarkModeToggle.vue";

const router = useRouter();
const toast = useToast();
const { hasRole } = useRole();

// --- 1. ESTADOS REACTIVOS ---
const connectingId = ref(null);
const fichas = ref([]);
const isLoading = ref(true);

// 🟢 NUEVOS ESTADOS PARA EL AMBIENTE
const showAmbienteModal = ref(false);
const ambientesDisponibles = ref([]);
const ambienteSeleccionado = ref("");
const fichaPendiente = ref(null);

// --- 2. FUNCIONES DE CONEXIÓN A DATAVERSE ---
const cargarAmbientes = async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/sesiones/ambientes`);
    if (res.ok) {
      ambientesDisponibles.value = await res.json();
    }
  } catch (error) {
    console.error("Error cargando ambientes físicos:", error);
  }
};

// --- 3. CICLO DE VIDA (Protección + Consultas) ---
onMounted(async () => {
  // A) Protección de ruta
  if (!hasRole(["instructor", "dinamizador"])) {
    toast.error("Acceso denegado. Se requiere credencial de Instructor.");
    router.push("/route-selector");
    return; 
  }

  const correoInstructor = localStorage.getItem('instructorEmail');
  if (!correoInstructor) {
    toast.error("No se encontró la sesión del instructor. Volviendo al inicio.");
    router.push("/route-selector");
    return;
  }

  // B) Cargar Fichas y Ambientes en paralelo
  try {
    await cargarAmbientes(); // 🟢 Descargamos los salones en segundo plano

    const response = await fetch(`${BASE_URL}/api/fichas/${correoInstructor}`);
    if (!response.ok) throw new Error("No se encontraron fichas para este instructor.");
    
    const data = await response.json();
    
    fichas.value = data.map((ficha, index) => ({
      id: index + 1,
      numero: ficha.numero_ficha,
      programa: ficha.nombre_programa,
      instructor: ficha.instructor, 
      jornada: "Asignada"
    }));

  } catch (error) {
    console.error("Error consultando la base de datos:", error);
    toast.error("No se pudieron cargar las fichas asignadas.");
  } finally {
    isLoading.value = false;
  }
});

// --- 4. FLUJO DE SELECCIÓN ---
// Paso 1: El instructor le da clic a la ficha
const seleccionarFicha = (ficha) => {
  fichaPendiente.value = ficha; // Guardamos la ficha temporalmente
  showAmbienteModal.value = true; // 🟢 Abrimos el modal del ambiente
};

// Paso 2: El instructor confirma el salón y entra al Dashboard
const confirmarAmbienteYContinuar = () => {
  if (!ambienteSeleccionado.value) {
    toast.warning("Debes seleccionar un ambiente para continuar.");
    return;
  }
  
  // A) Mostramos feedback visual de sincronización
  connectingId.value = fichaPendiente.value.id;
  showAmbienteModal.value = false; // Cerramos el modal
  
  const ambiente = ambientesDisponibles.value.find(a => a.id === ambienteSeleccionado.value);
  toast.info(`Sincronizando ${ambiente.nombre} con Ficha ${fichaPendiente.value.numero}...`);

  // B) Limpiamos variables (Tu truco Ninja)
  const numeroAguardar = fichaPendiente.value.numero || "Sin Número";
  const programaAguardar = fichaPendiente.value.programa || "Programa no definido";
  let instructorAguardar = fichaPendiente.value.instructor || localStorage.getItem('instructorEmail') || "Instructor SENA";

  if (instructorAguardar.includes('@')) {
    let soloNombre = instructorAguardar.split('@')[0]; 
    instructorAguardar = soloNombre.replace(/([a-z])([A-Z])/g, '$1 $2'); 
  }

  // C) Simulamos la conexión IoT y guardamos en memoria
  setTimeout(() => {
    // Variables de la Ficha
    localStorage.setItem('fichaActiva', numeroAguardar);
    localStorage.setItem('nombrePrograma', programaAguardar); 
    localStorage.setItem('nombreInstructor', instructorAguardar); 
    
    // 🟢 Variables del Ambiente (Para el Dashboard)
    localStorage.setItem('ambienteActivoId', ambienteSeleccionado.value);
    localStorage.setItem('ambienteActivoNombre', ambiente.nombre);

    toast.success("Conexión establecida. Iniciando telemetría.");
    router.push('/dashboard');
  }, 1200);
};
</script>

<template>
  <div class="select-shell">
    <div class="select-container">
      <header class="select-header">
        <div class="brand-assets-header">
          <img src="@/assets/VoltMindAccess.svg" alt="VoltMind Logo" class="logo-voltmind" />
          <div class="brand-divider"></div>
          <img src="@/assets/LogoSena.png" alt="SENA Logo" class="logo-sena" />
        </div>

        <div class="location-badge">
          <font-awesome-icon icon="fa-solid fa-location-dot" />
          <span>SISTEMA CENTRAL • VOLTMIND</span>
        </div>
        <h1>PANEL DE CONTROL VOLTMIND</h1>
        <p class="instruction">
          Seleccione el grupo que inicia sesión técnica:
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
            <font-awesome-icon icon="fa-solid fa-circle-notch" spin class="spinner-icon" />
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
    </div>

    <div v-if="showAmbienteModal" class="modal-overlay" style="z-index: 9999; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.85); position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;">
      <div class="modal-content" style="background: white; padding: 40px; border-radius: 12px; width: 450px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
        <img src="@/assets/LogoSena.png" alt="SENA" style="width: 90px; margin-bottom: 20px;" />
        <h2 style="color: #333; margin-bottom: 10px; font-size: 22px;">Ubicación de Formación</h2>
        <p style="color: #666; margin-bottom: 25px; line-height: 1.5;">Selecciona el ambiente físico donde dictarás clase a la Ficha <strong>{{ fichaPendiente?.numero }}</strong></p>
        
        <select v-model="ambienteSeleccionado" style="width: 100%; padding: 14px; border-radius: 8px; border: 2px solid #e0e0e0; margin-bottom: 25px; font-size: 16px; outline: none; transition: border 0.3s;">
          <option disabled value="">Selecciona un ambiente de la lista...</option>
          <option v-for="amb in ambientesDisponibles" :key="amb.id" :value="amb.id">
            {{ amb.nombre }}
          </option>
        </select>

        <div style="display: flex; gap: 10px;">
          <button @click="showAmbienteModal = false" style="flex: 1; padding: 14px; background: #e74c3c; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.3s;" onmouseover="this.style.background='#c0392b'" onmouseout="this.style.background='#e74c3c'">
            CANCELAR
          </button>
          <button @click="confirmarAmbienteYContinuar" style="flex: 2; padding: 14px; background: #39a900; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.3s;" onmouseover="this.style.background='#2d8500'" onmouseout="this.style.background='#39a900'">
            ENTRAR AL AULA
          </button>
        </div>
      </div>
    </div>
    
    <DarkModeToggle />
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
