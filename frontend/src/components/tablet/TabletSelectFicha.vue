<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'vue-toastification';

// 🟢 RECIBIMOS EL NOMBRE DINÁMICO DEL AMBIENTE DESDE EL PADRE
const props = defineProps({
  ambienteNombre: {
    type: String,
    default: "Ambiente"
  }
});

const emit = defineEmits(['ficha-selected', 'go-back']);
const toast = useToast();

const fichas = ref([]);
const isLoading = ref(true);
const connectingId = ref(null);

onMounted(async () => {
  let correoInstructor = localStorage.getItem('instructorEmail');
  if (!correoInstructor) {
    correoInstructor = "ferley_tobon@soy.sena.edu.co"; 
    localStorage.setItem('instructorEmail', correoInstructor);
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/api/fichas/${correoInstructor}`);
    if (!response.ok) throw new Error("Error fetching fichas");
    
    const data = await response.json();
    
    fichas.value = data.map((ficha, index) => {
      let instructorLimpio = ficha.instructor || correoInstructor;
      if (instructorLimpio.includes('@')) {
        let soloNombre = instructorLimpio.split('@')[0]; 
        instructorLimpio = soloNombre.replace(/([a-z])([A-Z])/g, '$1 $2'); 
      }
      const jornadas = ["JORNADA MAÑANA", "JORNADA TARDE", "JORNADA NOCHE"];
      const jornada = jornadas[index % 3];

      return {
        id: index + 1,
        numero: ficha.numero_ficha,
        programa: ficha.nombre_programa,
        instructor: instructorLimpio,
        jornada: jornada
      };
    });
  } catch (error) {
    console.error("Error consultando fichas:", error);
    toast.error("No se pudieron cargar las fichas asignadas.");
  } finally {
    isLoading.value = false;
  }
});

// 🔄 FUNCIÓN ACTUALIZADA: YA NO TIENE EL "402" QUEMADO
const seleccionarFicha = (ficha) => {
  connectingId.value = ficha.id;
  
  // 🟢 Usamos la prop del nombre real del ambiente físico
  toast.info(`Sincronizando ${props.ambienteNombre.toUpperCase()} con Ficha ${ficha.numero}...`);

  setTimeout(() => {
    localStorage.setItem('fichaActiva', ficha.numero);
    localStorage.setItem('nombrePrograma', ficha.programa); 
    localStorage.setItem('nombreInstructor', ficha.instructor); 

    toast.success("Conexión establecida.");
    emit('ficha-selected', ficha);
  }, 1200);
};
</script>

<template>
  <div class="tablet-select-container">
    <!-- Header Area (Same as Step 1) -->
    <div class="header-logos">
      <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="logo-volt" />
      <div class="logo-divider"></div>
      <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
    </div>

    <div class="location-badge">
      <font-awesome-icon icon="fa-solid fa-location-dot" />
      <span>{{ ambienteNombre }}</span>
    </div>

    <!-- Title and Subtitle -->
    <div class="title-section">
      <h1>PANEL DE CONTROL VOLTMIND</h1>
      <p>Seleccione el grupo que inicia sesión técnica en este ambiente:</p>
    </div>

    <!-- Fichas Grid -->
    <div v-if="isLoading" class="loading-state">Cargando fichas...</div>
    <div v-else class="fichas-grid">
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

        <div class="card-top">
          <div class="card-icon">
            <font-awesome-icon icon="fa-solid fa-user-check" />
          </div>
          <div class="card-status">READY</div>
        </div>

        <div class="card-info">
          <span class="label">NÚMERO DE FICHA</span>
          <h2 class="ficha-number">{{ ficha.numero }}</h2>
          <p class="program-name">{{ ficha.programa }}</p>
          <div class="instructor-badge">
            <span class="green-dot"></span>
            <span>Ins. {{ ficha.instructor }}</span>
          </div>
        </div>

        <div class="card-footer">
          <span class="jornada-tag">{{ ficha.jornada }}</span>
        </div>
      </button>
    </div>

    <!-- Footer Button -->
    <button class="btn-back" @click="emit('go-back')">
      REGRESAR AL SELECTOR
    </button>
  </div>
</template>

<style scoped>
.tablet-select-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100vh;
  width: 100%;
  background-color: var(--fondo-app);
  padding: 3rem 2rem;
  box-sizing: border-box;
}

.header-logos {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 1rem;
}

.logo-volt { height: 40px; width: auto; }
.logo-sena { height: 40px; width: auto; }

.logo-divider {
  width: 1px;
  height: 24px;
  background-color: var(--borde);
}

.location-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.15);
  border: 1px solid rgba(57, 169, 0, 0.4);
  padding: 6px 14px;
  border-radius: 8px;
  color: var(--sena-verde-oscuro);
  font-size: 0.8rem;
  font-weight: 800;
  margin-bottom: 2rem;
}

.title-section {
  text-align: center;
  margin-bottom: 3rem;
}

.title-section h1 {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--sena-azul-oscuro);
  margin: 0 0 8px 0;
}

.title-section p {
  font-size: 1rem;
  color: var(--texto-secundario);
  margin: 0;
}

.fichas-grid {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
  max-width: 1000px;
  width: 100%;
  margin-bottom: 4rem;
}

.ficha-card {
  background: var(--sena-blanco);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.5rem;
  width: 280px;
  text-align: left;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  font-family: inherit;
}

.ficha-card:hover:not(:disabled) {
  transform: translateY(-4px);
  border-color: var(--sena-verde);
  box-shadow: 0 8px 16px rgba(0,0,0,0.06);
}

.ficha-card:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-icon {
  width: 40px;
  height: 40px;
  background: var(--fondo-app);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: var(--texto-secundario);
}

.card-status {
  background: #e5f5e5;
  color: var(--sena-verde-oscuro);
  font-size: 0.65rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 4px;
}

.label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 2px;
}

.ficha-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 4px 0;
}

.program-name {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.instructor-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--texto-secundario);
  margin-bottom: 1.5rem;
}

.green-dot {
  width: 6px;
  height: 6px;
  background-color: var(--sena-verde);
  border-radius: 50%;
}

.card-footer {
  border-top: 1px solid var(--fondo-app);
  padding-top: 1rem;
  margin-top: auto;
}

.jornada-tag {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--sena-verde);
}

.btn-back {
  background: var(--sena-blanco);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--fondo-app);
  color: var(--sena-azul-oscuro);
}

.connecting-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--sena-verde-oscuro);
  font-weight: 700;
  font-size: 0.85rem;
  z-index: 10;
}

.spinner-icon {
  font-size: 2rem;
  color: var(--sena-verde);
}
</style>