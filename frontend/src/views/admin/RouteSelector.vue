<template>
  <div class="selector-shell">
    <div class="selector-container">
      <div class="brand-header">
        <span class="text-volt">Volt</span><span class="text-mind">Mind</span>
        <h2>Hola, {{ userStore.name }}</h2>
        <p>Selecciona tu entorno de trabajo</p>
      </div>

      <!-- 🟢 AVISO DE CLASE ACTIVA (Reemplaza al escudo zombie) -->
      <div v-if="sesionRecuperada" class="active-session-banner alert-success" style="margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; text-align: left;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
          <font-awesome-icon icon="fa-solid fa-chalkboard-user" style="font-size: 1.5rem;" />
          <div>
            <strong style="display: block;">¡Tienes una clase activa en curso!</strong>
            <span style="font-size: 0.9em;">Iniciada a las: {{ horaInicioFormateada }}</span>
          </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 10px;">
          <button @click="retomarDashboard" class="btn-action-green" style="flex: 2; padding: 10px; border-radius: 4px; border: none; cursor: pointer; background: #28a745; color: white; font-weight: bold; font-size: 1rem;">
            Ir al Panel de Control <font-awesome-icon icon="fa-solid fa-arrow-right" style="margin-left: 5px;" />
          </button>
          <button @click="forzarCierreSesion" class="btn-action-red" style="flex: 1; padding: 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">
            Finalizar
          </button>
        </div>
      </div>

      <!-- Bloqueamos visualmente las opciones si hay una sesión zombie -->
      <div class="options-grid" :style="{ opacity: sesionRecuperada ? '0.5' : '1', pointerEvents: sesionRecuperada ? 'none' : 'auto' }">
        
        <!-- Opción 1: Panel de Control -->
        <button class="option-card" @click="goToDashboard">
          <div class="icon-wrapper bg-blue">
            <font-awesome-icon icon="fa-solid fa-desktop" />
          </div>
          <h3>Panel de Control</h3>
          <p>Gestiona el aula de forma remota.</p>
        </button>

        <!-- Opción 2: Carnet Digital -->
        <button class="option-card" @click="goToCard">
          <div class="icon-wrapper bg-green">
            <font-awesome-icon icon="fa-solid fa-id-badge" />
          </div>
          <h3>Carnet Maestro</h3>
          <p>Utiliza tu dispositivo para encender el aula presencialmente.</p>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useToast } from 'vue-toastification';

const router = useRouter();
const userStore = useUserStore();
const toast = useToast();

const sesionRecuperada = ref(false); 
const idSesionFantasma = ref(null);
const horaInicioFormateada = ref('');
const fichaFantasma = ref('');
const ambienteFantasma = ref('');

onMounted(async () => {
  const nombreGuardado = localStorage.getItem('instructorName');
  const correoGuardado = localStorage.getItem('instructorEmail');
  const rolGuardado = localStorage.getItem('user_role');

  if (nombreGuardado && correoGuardado) {
    userStore.name = nombreGuardado;
    userStore.email = correoGuardado; 
    userStore.role = rolGuardado || 'instructor';

    // 🛡️ PRIMER FILTRO: Revisar memoria local (Si el navegador quedó "sucio")
    const sesionLocal = localStorage.getItem('sesionActivaId');
    if (sesionLocal) {
      console.warn("🧟 Zombie detectado en memoria local");
      idSesionFantasma.value = sesionLocal;
      horaInicioFormateada.value = localStorage.getItem('horaInicio') || 'Sesión anterior';
      sesionRecuperada.value = true;
      return; // Detenemos la ejecución aquí, no hace falta preguntar a Dataverse
    }

    // 📡 SEGUNDO FILTRO: Radar Backend (Por si la clase quedó "En Curso" en Dataverse)
    try {
      const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const radar = await fetch(`${BASE_URL}/api/sesiones/activa/${correoGuardado}`);
      if (radar.ok) {
        const dataRadar = await radar.json();
        
        if (dataRadar.activa) {
          console.warn("🧟 Zombie detectado en Dataverse");
          idSesionFantasma.value = dataRadar.sesion_id;
          const fechaEntrada = new Date(dataRadar.hora_entrada);
          horaInicioFormateada.value = fechaEntrada.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
          fichaFantasma.value = dataRadar.ficha_numero;
          ambienteFantasma.value = dataRadar.ambiente_id;
          sesionRecuperada.value = true;
        }
      }
    } catch (error) {
      console.error("Error en el radar de sesiones:", error);
    }
  } else {
    router.push('/login');
  }
});

// 💥 FUNCIÓN PARA MATAR LA SESIÓN
const forzarCierreSesion = async () => {
  if (!idSesionFantasma.value) return;
  
  toast.info("Limpiando sesión atascada...");
  
  try {
    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${BASE_URL}/api/sesiones/finalizar?sesion_id=${idSesionFantasma.value}`, {
      method: "POST"
    });

    if (response.ok) {
      // Limpiamos cualquier rastro local
      localStorage.removeItem('sesionActivaId');
      localStorage.removeItem('horaInicio');
      localStorage.removeItem('fichaActiva');
      localStorage.removeItem('nombrePrograma');
      
      sesionRecuperada.value = false;
      toast.success("Limpieza completa. Ya puedes iniciar una nueva clase.");
    } else {
      toast.error("Error al cerrar en Dataverse.");
    }
  } catch (error) {
    console.error("Error forzando cierre:", error);
    toast.error("Fallo de red al intentar limpiar la sesión.");
  }
};

const retomarDashboard = () => {
  localStorage.setItem('sesionActivaId', idSesionFantasma.value);
  localStorage.setItem('horaInicio', horaInicioFormateada.value);
  localStorage.setItem('isPowerOn', 'true');
  if (fichaFantasma.value) localStorage.setItem('fichaActiva', fichaFantasma.value);
  if (ambienteFantasma.value) localStorage.setItem('ambienteActivoId', ambienteFantasma.value);
  
  router.push("/dashboard");
};

const goToDashboard = () => {
  router.push('/select-ficha'); 
};

const goToCard = () => {
  router.push('/card');
};
</script>

<style scoped>
.selector-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--fondo-app);
  font-family: var(--fuente-principal);
}
.selector-container {
  text-align: center;
  max-width: 600px;
  padding: 2rem;
}
.brand-header {
  margin-bottom: 3rem;
}
.text-volt { color: var(--sena-azul-oscuro); font-size: 2rem; font-weight: 800; }
.text-mind { color: var(--sena-verde); font-size: 2rem; font-weight: 800; }
.brand-header h2 { margin-top: 1rem; color: var(--texto-principal); }
.brand-header p { color: var(--texto-secundario); }

.options-grid {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}
.option-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 2rem;
  width: 250px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  border-color: var(--sena-verde);
}
.icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: white;
}
.bg-blue { background-color: var(--sena-azul-oscuro); }
.bg-green { background-color: var(--sena-verde); }
.option-card h3 { color: var(--texto-principal); margin: 0 0 0.5rem 0; font-size: 1.2rem; }
.option-card p { color: var(--texto-secundario); font-size: 0.9rem; margin: 0; }

@media (max-width: 600px) {
  .options-grid {
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  .option-card {
    width: 100%;
    max-width: 320px;
    padding: 1.5rem;
  }
  .selector-container {
    padding: 1.5rem;
  }
  .brand-header {
    margin-bottom: 2rem;
  }
}
</style>