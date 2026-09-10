<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <button class="btn-volver" title="Volver al listado de mis fichas" @click="volver">
          <font-awesome-icon icon="fa-solid fa-arrow-left" />
        </button>
        <div class="environment-badge">
          <h1>FICHA {{ ficha?.codigo || 'Cargando...' }}</h1>
          <p class="header-meta">
            <span>{{ ficha?.programa || 'Cargando programa...' }}</span>
          </p>
        </div>
      </div>
      <div class="header-actions">
        <div class="toggle-vista" role="group">
          <button class="btn-toggle" :class="{ activo: pestana === 'competencias' }" @click="pestana = 'competencias'">
            <font-awesome-icon icon="fa-solid fa-list-check" /> Competencias (Horas)
          </button>
          <button class="btn-toggle" :class="{ activo: pestana === 'aprendices' }" @click="pestana = 'aprendices'">
            <font-awesome-icon icon="fa-solid fa-users" /> Aprendices
          </button>
          <button class="btn-toggle btn-aula" :class="{ activo: pestana === 'aula' }" @click="pestana = 'aula'">
            <font-awesome-icon icon="fa-solid fa-bolt" /> Panel Energético
          </button>
        </div>
      </div>
    </header>

    <main class="dash-grid">
      <div v-if="!ficha" style="text-align: center; padding: 3rem;">
        <GlobalSpinner size="large" />
        <p style="color: var(--texto-secundario); margin-top: 1rem;">Cargando información de la ficha...</p>
      </div>
      
      <template v-else>
        <!-- PESTAÑA COMPETENCIAS -->
        <section v-if="pestana === 'competencias'" class="module-card">
          <div class="card-header">
            <h2>Asignación de Horas a Competencias</h2>
          </div>
          <div class="card-body">
            <p>En esta sección podrás registrar la carga horaria para cada competencia asignada a esta ficha.</p>
            <button class="btn-action-green" @click="abrirEditarMatriz">
              <font-awesome-icon icon="fa-solid fa-pen-to-square" /> Editar Matriz de Horas
            </button>
          </div>
        </section>

      <!-- PESTAÑA APRENDICES -->
      <section v-if="pestana === 'aprendices'" class="module-card">
        <div class="card-header">
          <h2>Gestión de Aprendices</h2>
        </div>
        <div class="card-body">
          <p>Módulo para cargar, crear y editar aprendices matriculados en esta ficha.</p>
          <div class="placeholder-box">Módulo en construcción</div>
        </div>
      </section>

      <!-- PESTAÑA AULA / IOT -->
      <section v-if="pestana === 'aula'" class="module-card">
        <div class="card-header">
          <h2>Control Energético del Aula</h2>
        </div>
        <div class="card-body" style="text-align: center; max-width: 500px; margin: 0 auto; padding: 40px 0;">
          <img src="@/assets/LogoSena.png" alt="SENA" style="width: 90px; margin-bottom: 20px;" />
          <h2 style="color: #333; margin-bottom: 10px; font-size: 22px;">Ingresar al Aula</h2>
          <p style="color: #666; margin-bottom: 25px; line-height: 1.5;">Selecciona el ambiente físico donde dictarás clase a esta Ficha para tomar el control energético.</p>
          
          <select v-model="ambienteSeleccionado" class="form-input" style="width: 100%; padding: 14px; border-radius: 8px; border: 2px solid #e0e0e0; margin-bottom: 25px; font-size: 16px; outline: none;">
            <option disabled value="">Selecciona un ambiente de la lista...</option>
            <option v-for="amb in ambientesDisponibles" :key="amb.id" :value="amb.id">
              {{ amb.nombre }}
            </option>
          </select>

          <button @click="confirmarAmbienteYContinuar" style="width: 100%; padding: 14px; background: #39a900; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.3s;">
            ENTRAR AL AULA
          </button>
        </div>
      </section>
      </template>
    </main>

    <!-- Modal Editar Matriz -->
    <ModalDiagnostico
      :show="showDiagnostico"
      :ficha="ficha"
      @update:show="showDiagnostico = $event"
      @close="showDiagnostico = false"
      @saved="cargarFicha"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { tituladasService } from '@/services/tituladasService';
import ModalDiagnostico from '@/components/admin/modals/ModalDiagnostico.vue';

import { ambientesService } from '@/services/ambientesService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const pestana = ref('competencias');
const fichaId = route.params.id;
const ficha = ref(null);
const showDiagnostico = ref(false);

const ambientesDisponibles = ref([]);
const ambienteSeleccionado = ref('');

const cargarFicha = async () => {
  try {
    const data = await tituladasService.getFicha(fichaId);
    if (data) {
      ficha.value = data;
    }
  } catch (error) {
    console.error('Error al cargar la ficha', error);
    toast.error('La ficha solicitada no existe.');
    volver();
  }
};

const cargarAmbientes = async () => {
  try {
    const data = await ambientesService.getAll();
    ambientesDisponibles.value = data.map(amb => ({
      id: amb.cr6a3_ambiente_formacionid,
      nombre: amb.cr6a3_nombre_ambiente,
      ...amb
    }));
  } catch (error) {
    console.error('Error al cargar ambientes:', error);
  }
};

const volver = () => {
  router.push('/instructor/fichas');
};

const abrirEditarMatriz = () => {
  showDiagnostico.value = true;
};

const confirmarAmbienteYContinuar = () => {
  if (!ambienteSeleccionado.value) {
    toast.error('Debe seleccionar un ambiente de formación para iniciar su clase.');
    return;
  }
  
  const ambiente = ambientesDisponibles.value.find(a => a.id === ambienteSeleccionado.value);
  toast.info(`Sincronizando ${ambiente.nombre} con Ficha ${ficha.value.codigo}...`);

  setTimeout(() => {
    // Set variables for Dashboard compatibility
    localStorage.setItem('fichaActiva', ficha.value.codigo);
    localStorage.setItem('nombrePrograma', ficha.value.programa);
    localStorage.setItem('ambienteActivoId', ambienteSeleccionado.value);
    localStorage.setItem('ambienteActivoNombre', ambiente.nombre);
    
    router.push('/dashboard');
  }, 1200);
};

onMounted(() => {
  cargarFicha();
  cargarAmbientes();
});
</script>

<style scoped>
.admin-view-shell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 1.5rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  box-shadow: 0 4px 12px var(--sombra-suave);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.btn-volver {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  width: 44px;
  height: 44px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-volver:hover {
  background: var(--sena-azul-oscuro);
  color: white;
  border-color: var(--sena-azul-oscuro);
  transform: translateX(-3px);
}
.environment-badge h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}
.header-meta {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-secundario);
}
.toggle-vista {
  display: flex;
  background: var(--fondo-app);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid var(--borde);
}
.btn-toggle {
  background: transparent;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-toggle:hover {
  color: var(--sena-azul-oscuro);
}
.btn-toggle.activo {
  background: white;
  color: var(--sena-azul-oscuro);
  box-shadow: 0 2px 8px rgba(0, 48, 64, 0.08);
}
.btn-aula {
  color: #e67e22;
}
.btn-aula.activo {
  background: #e67e22;
  color: white;
}
.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}
.card-header h2 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  color: var(--sena-azul-oscuro);
}
.btn-action-green {
  background-color: var(--sena-verde);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 1rem;
}
.placeholder-box {
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  color: #64748b;
  font-weight: 600;
}
</style>
