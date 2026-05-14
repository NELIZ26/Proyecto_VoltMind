<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="header-info">
        <font-awesome-icon icon="fa-solid fa-microchip" class="text-sena" />
        <span>Ambiente: <strong>Sistemas 1</strong></span>
      </div>
      <div class="user-profile">
        <span>Instructor: {{ userStore.name }}</span>
        <button @click="logout" class="btn-logout">
          <font-awesome-icon icon="fa-solid fa-power-off" />
        </button>
      </div>
    </header>

    <main class="dashboard-grid">
      <section class="card status-card">
        <div class="card-header">
          <font-awesome-icon icon="fa-solid fa-bolt" />
          <h3>Control de Energía</h3>
        </div>
        <div class="card-body">
          <div class="energy-status" :class="{ 'active': relayActive }">
            {{ relayActive ? 'Ambiente Energizado' : 'Energía Cortada' }}
          </div>
          <button @click="toggleRelay" class="btn-relay" :class="{ 'btn-off': relayActive }">
            {{ relayActive ? 'Apagar Ambiente' : 'Encender Ambiente' }}
          </button>
        </div>
      </section>

      <section class="card monitoring-card">
        <div class="card-header">
          <font-awesome-icon icon="fa-solid fa-microchip" />
          <h3>Consumo Actual</h3>
        </div>
        <div class="card-body">
          <div class="watt-display">
            <span class="value">240</span>
            <span class="unit">Watts</span>
          </div>
          <p class="status-text">Sensor de corriente activo</p>
        </div>
      </section>

      <section class="card attendance-card">
        <div class="card-header">
          <font-awesome-icon icon="fa-solid fa-user-check" />
          <h3>Últimos Ingresos</h3>
        </div>
        <div class="card-body">
          <ul class="attendance-list">
            <li><span>Vanessa Diaz</span> <small>17:45</small></li>
            <li><span>Kevin Portilla</span> <small>17:30</small></li>
            <li><span>Mayer Gomez</span> <small>17:15</small></li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const relayActive = ref(true);

const toggleRelay = () => {
  relayActive.value = !relayActive.value;
  // Aquí Nelson llamará al endpoint de FastAPI para activar el GPIO de la Raspberry
};

const logout = () => {
  userStore.logout();
  router.push('/');
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  padding: 20px;
  background-color: var(--sena-gris-fondo);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--sena-blanco);
  padding: 15px 25px;
  border-radius: 15px;
  margin-bottom: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: var(--sena-blanco);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
  border-top: 5px solid var(--sena-verde);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  color: var(--sena-azul);
}

.energy-status {
  padding: 10px;
  border-radius: 10px;
  background: #fee2e2;
  color: #dc2626;
  text-align: center;
  font-weight: bold;
  margin-bottom: 15px;
}

.energy-status.active {
  background: var(--sena-verde-claro);
  color: var(--sena-verde);
}

.watt-display {
  text-align: center;
  padding: 20px 0;
}

.watt-display .value {
  font-size: 3.5rem;
  font-weight: 800;
  color: var(--sena-azul);
}

.btn-relay {
  width: 100%;
  padding: 15px;
  border-radius: 12px;
  border: none;
  background: var(--sena-verde);
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.btn-relay.btn-off {
  background: var(--sena-azul);
}

.attendance-list {
  list-style: none;
}

.attendance-list li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--borde);
}
</style>