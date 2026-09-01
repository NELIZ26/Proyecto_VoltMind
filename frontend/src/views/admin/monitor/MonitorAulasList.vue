<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import DarkModeToggle from "@/components/DarkModeToggle.vue";

const router = useRouter();

// Mocks de ambientes
const ambientes = ref([
  { id: '101', name: 'Aula 101', status: 'nominal', load: 1200 },
  { id: '102', name: 'Aula 102', status: 'warning', load: 4500 }, // Simulando consumo alto
  { id: '103', name: 'Aula 103', status: 'nominal', load: 800 },
  { id: '104', name: 'Aula 104', status: 'nominal', load: 0 },
  { id: 'lego', name: 'Ambiente Lego', status: 'critical', load: 6000 },
  { id: 'cocina', name: 'Cocina', status: 'nominal', load: 2400 },
  { id: 'admin', name: 'Administrativo', status: 'nominal', load: 1500 }
]);

const navigateToDetail = (id) => {
  router.push(`/admin/monitor-aulas/${id}`);
};
</script>

<template>
  <div class="monitor-list-shell">
    <header class="page-header">
      <div class="header-content">
        <h1><font-awesome-icon icon="fa-solid fa-layer-group" /> Selector de Aulas</h1>
        <p>Selecciona un ambiente para visualizar su control individual y configuración de relevadores.</p>
      </div>
      <button class="btn-back" @click="router.push('/dashboard-admin')">
        <font-awesome-icon icon="fa-solid fa-arrow-left" /> Volver al Dashboard
      </button>
    </header>

    <div class="ambientes-grid">
      <div 
        v-for="amb in ambientes" 
        :key="amb.id" 
        class="ambiente-card" 
        :class="'status-' + amb.status"
        @click="navigateToDetail(amb.id)"
      >
        <div class="card-status-bar"></div>
        <div class="card-content">
          <div class="card-header">
            <h2>{{ amb.name }}</h2>
            <font-awesome-icon v-if="amb.status === 'critical'" icon="fa-solid fa-triangle-exclamation" class="icon-critical" />
            <font-awesome-icon v-else-if="amb.status === 'warning'" icon="fa-solid fa-circle-exclamation" class="icon-warning" />
            <font-awesome-icon v-else icon="fa-solid fa-circle-check" class="icon-nominal" />
          </div>
          <div class="card-body">
            <span class="load-label">Carga actual:</span>
            <span class="load-val">{{ (amb.load / 1000).toFixed(1) }} <small>kW</small></span>
          </div>
          <div class="card-footer">
            <span>Ver controles</span>
            <font-awesome-icon icon="fa-solid fa-chevron-right" />
          </div>
        </div>
      </div>
    </div>
    
    <DarkModeToggle />
  </div>
</template>

<style scoped>
.monitor-list-shell {
  padding: 2rem;
  background-color: var(--fondo-app);
  min-height: 100vh;
  font-family: var(--fuente-principal);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}
.header-content h1 {
  font-size: 1.8rem;
  color: var(--sena-azul-oscuro);
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-content p {
  color: var(--texto-secundario);
  margin: 0;
  font-size: 1rem;
}
.btn-back {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  color: var(--texto-principal);
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-back:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.ambientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.ambiente-card {
  background: var(--fondo-tarjetas);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
  border: 1px solid var(--borde);
  position: relative;
}
.ambiente-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px rgba(0,0,0,0.1);
}
.card-status-bar {
  height: 6px;
  width: 100%;
}
.status-nominal .card-status-bar { background: var(--sena-verde); }
.status-warning .card-status-bar { background: var(--sena-amarillo); }
.status-critical .card-status-bar { background: #ef4444; }

.status-warning { background: linear-gradient(to bottom, rgba(253, 195, 0, 0.05), white); }
.status-critical { background: linear-gradient(to bottom, rgba(239, 68, 68, 0.05), white); }

.card-content { padding: 1.25rem; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.card-header h2 {
  font-size: 1.25rem;
  color: var(--sena-azul-oscuro);
  margin: 0;
  font-weight: 800;
}
.icon-nominal { color: var(--sena-verde); font-size: 1.25rem; }
.icon-warning { color: var(--sena-amarillo); font-size: 1.25rem; }
.icon-critical { color: #ef4444; font-size: 1.25rem; }

.card-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
}
.load-label { font-size: 0.85rem; color: var(--texto-secundario); font-weight: 600; }
.load-val { font-size: 1.5rem; font-weight: 900; color: var(--texto-principal); font-family: monospace;}
.load-val small { font-size: 0.8rem; font-weight: 600; color: var(--texto-secundario); }

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--borde);
  padding-top: 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--sena-azul);
}
</style>
