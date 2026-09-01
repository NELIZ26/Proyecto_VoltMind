<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import DarkModeToggle from "@/components/DarkModeToggle.vue";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const aulaId = ref(route.params.id);
const aulaName = ref(`Aula ${aulaId.value.toUpperCase()}`);

// Estado de los focos simulados (16 focos por defecto para la demostración)
// True = encendido (consumiendo), False = apagado
const luces = ref(Array.from({ length: 16 }, (_, i) => ({
  id: i + 1,
  encendido: true,
  nombre: `Luminaria ${i + 1}`,
  canal: `Relay ${i + 1}`
})));

const toggleLuz = (luz) => {
  luz.encendido = !luz.encendido;
  if (luz.encendido) {
    toast.success(`${luz.nombre} ENCENDIDA (${luz.canal})`);
  } else {
    toast.info(`${luz.nombre} APAGADA (${luz.canal})`);
  }
};

const apagarTodo = () => {
  luces.value.forEach(l => l.encendido = false);
  toast.success("Corte general aplicado: Todas las luces apagadas.");
};

const encenderTodo = () => {
  luces.value.forEach(l => l.encendido = true);
  toast.success("Todas las luces encendidas.");
};
</script>

<template>
  <div class="monitor-detail-shell">
    <header class="page-header">
      <div class="header-left">
        <button class="btn-icon" @click="router.push('/admin/monitor-aulas')">
          <font-awesome-icon icon="fa-solid fa-arrow-left" />
        </button>
        <div class="header-content">
          <h1>{{ aulaName }} <span class="badge-status">En línea</span></h1>
          <p>Panel de Control Individual de Circuitos Eléctricos</p>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-action btn-danger" @click="apagarTodo">
          <font-awesome-icon icon="fa-solid fa-power-off" /> Corte General
        </button>
        <button class="btn-action btn-edit" @click="router.push(`/admin/monitor-aulas/${aulaId}/edit`)">
          <font-awesome-icon icon="fa-solid fa-pen-to-square" /> Configurar Hardware
        </button>
      </div>
    </header>

    <div class="controls-container">
      <div class="panel-section">
        <div class="section-header">
          <h2><font-awesome-icon icon="fa-solid fa-lightbulb" /> Circuito de Iluminación</h2>
          <span class="luz-count">{{ luces.filter(l => l.encendido).length }} / {{ luces.length }} encendidas</span>
        </div>
        
        <div class="luces-grid">
          <div 
            v-for="luz in luces" 
            :key="luz.id" 
            class="luz-card"
            :class="{ 'is-on': luz.encendido }"
          >
            <div class="luz-header">
              <span class="luz-name">{{ luz.nombre }}</span>
              <span class="luz-canal">{{ luz.canal }}</span>
            </div>
            <div class="luz-body">
              <font-awesome-icon icon="fa-solid fa-lightbulb" class="luz-icon" />
              <label class="switch">
                <input type="checkbox" v-model="luz.encendido" @click.prevent="toggleLuz(luz)">
                <span class="slider round"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <DarkModeToggle />
  </div>
</template>

<style scoped>
.monitor-detail-shell {
  padding: 2rem;
  background-color: var(--fondo-app);
  min-height: 100vh;
  font-family: var(--fuente-principal);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--fondo-tarjetas);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.header-left { display: flex; align-items: center; gap: 1.5rem; }
.btn-icon {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  transition: transform 0.2s;
}
.btn-icon:hover { transform: translateX(-3px); }
.header-content h1 {
  font-size: 1.8rem;
  color: var(--sena-azul-oscuro);
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.badge-status {
  font-size: 0.75rem;
  background: #dcfce7;
  color: var(--sena-verde-oscuro);
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 700;
  border: 1px solid #bbf7d0;
  text-transform: uppercase;
}
.header-content p { color: var(--texto-secundario); margin: 0; font-size: 0.9rem; }

.header-right { display: flex; gap: 1rem; }
.btn-action {
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}
.btn-action:hover { opacity: 0.9; }
.btn-danger { background: #ef4444; color: white; }
.btn-edit { background: var(--fondo-app); color: var(--sena-azul-oscuro); border: 1px solid var(--borde); }
.btn-edit:hover { background: #e2e8f0; }

.controls-container {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 2rem;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--borde);
}
.section-header h2 {
  font-size: 1.4rem;
  color: var(--texto-principal);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.luz-count {
  font-size: 0.9rem;
  font-weight: 700;
  background: var(--fondo-app);
  padding: 6px 12px;
  border-radius: 8px;
  color: var(--sena-azul-oscuro);
}

.luces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.luz-card {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1.25rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.luz-card.is-on {
  border-color: #fde047;
  background: #fefce8;
  box-shadow: 0 0 15px rgba(253, 224, 71, 0.2);
}

.luz-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.luz-name { font-weight: 800; font-size: 1rem; color: var(--texto-principal); }
.luz-canal { font-size: 0.7rem; background: #e2e8f0; color: #64748b; padding: 2px 6px; border-radius: 4px; font-weight: 700; }

.luz-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.luz-icon {
  font-size: 2.5rem;
  color: #cbd5e1;
  transition: color 0.3s;
}
.luz-card.is-on .luz-icon {
  color: #eab308; /* Amarillo sol */
  filter: drop-shadow(0 0 8px rgba(234, 179, 8, 0.6));
}

/* TOGGLE SWITCH STYLE */
.switch { position: relative; display: inline-block; width: 50px; height: 26px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #ccc; transition: .4s;
}
.slider:before {
  position: absolute; content: ""; height: 18px; width: 18px;
  left: 4px; bottom: 4px; background-color: white; transition: .4s;
}
input:checked + .slider { background-color: var(--sena-verde); }
input:focus + .slider { box-shadow: 0 0 1px var(--sena-verde); }
input:checked + .slider:before { transform: translateX(24px); }
.slider.round { border-radius: 26px; }
.slider.round:before { border-radius: 50%; }
</style>
