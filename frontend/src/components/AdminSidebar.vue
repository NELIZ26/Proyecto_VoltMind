<template>
  <nav class="admin-sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <div class="logo-duo">
        <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
        <img src="@/assets/VoltMindAccess.svg" alt="VoltMind" class="logo-volt" />
      </div>
      <div class="brand-text">
        <h1 class="brand-title"><span class="text-volt">Volt</span><span class="text-mind">Mind</span></h1>
        <p class="brand-subtitle">ADMIN ACCESS</p>
      </div>
    </div>
    
    <ul class="sidebar-menu">
      <li class="menu-category">MONITOREO GENERAL</li>
      <li>
        <router-link to="/admin/dashboard" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-chart-pie" fixed-width />
          </div>
          <span class="menu-text">Dashboard Global</span>
        </router-link>
      </li>

      <li class="menu-category">PLANIFICACIÓN ACADÉMICA</li>
      <li>
        <router-link to="/admin/calculadora" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-calculator" fixed-width />
          </div>
          <span class="menu-text">Calculadora de Horas</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/fichas" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-graduation-cap" fixed-width />
          </div>
          <span class="menu-text">Gestión de Fichas</span>
        </router-link>
      </li>

      <li class="menu-category">CONTROL DE PERSONAL</li>
      <li>
        <router-link to="/admin/instructores" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-chalkboard-user" fixed-width />
          </div>
          <span class="menu-text">Instructores</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/aprendices" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-users" fixed-width />
          </div>
          <span class="menu-text">Aprendices</span>
        </router-link>
      </li>

      <li class="menu-category">INFRAESTRUCTURA E IOT</li>
      <li>
        <router-link to="/admin/ambientes" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-location-dot" fixed-width />
          </div>
          <span class="menu-text">Ambientes y Horarios</span>
        </router-link>
      </li>
      <li>
        <router-link to="/admin/iot" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-microchip" fixed-width />
          </div>
          <span class="menu-text">Configuración Relés</span>
        </router-link>
      </li>
      
      <li class="logout-item">
        <router-link to="/login" class="menu-link logout-link" @click="handleMenuClick">
          <div class="icon-box logout-icon-box">
            <font-awesome-icon icon="fa-solid fa-right-from-bracket" fixed-width />
          </div>
          <span class="menu-text">Salir</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const handleMenuClick = () => {
  emit('close');
};
</script>

<style scoped>
.admin-sidebar {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 0 16px 16px 0;
  box-shadow: 0 4px 12px var(--sombra-suave);
  width: 280px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 1.5rem;
  user-select: none;
  transition: transform 0.3s ease;
}

@media (max-width: 992px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  
  .admin-sidebar.sidebar-open {
    transform: translateX(0);
  }
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--borde);
}

.logo-duo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.logo-sena {
  height: 55px;
  width: auto;
}
.logo-volt {
  height: 60px;
  width: auto;
}

.brand-text {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  line-height: 1;
}

.text-volt {
  color: var(--sena-azul-oscuro);
}

.text-mind {
  color: var(--sena-verde);
}

.brand-subtitle {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  letter-spacing: 1.5px;
  margin: 0;
  text-transform: uppercase;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-grow: 1;
}

.menu-category {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--texto-secundario);
  letter-spacing: 1px;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  padding-left: 0.5rem;
}

.menu-link {
  text-decoration: none;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  transition: all 0.2s ease;
  font-weight: 600;
  font-size: 0.95rem;
  border: 1px solid transparent;
}

.menu-text {
  line-height: 1.15;
}

.icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--fondo-app);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--texto-secundario);
  transition: all 0.2s ease;
}

.menu-link:hover {
  background-color: var(--fondo-app);
  border-color: var(--borde);
}

.menu-link:hover .icon-box {
  background-color: var(--sena-verde);
  color: var(--sena-blanco);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.menu-link.router-link-active {
  background-color: rgba(57, 169, 0, 0.05);
  border-color: rgba(57, 169, 0, 0.2);
  color: var(--sena-verde-oscuro);
}

.menu-link.router-link-active .icon-box {
  background-color: var(--sena-verde);
  color: var(--sena-blanco);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.logout-item {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--borde);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dark-mode-toggle {
  background: transparent;
  width: 100%;
  text-align: left;
  cursor: pointer;
  border: 1px solid transparent;
}

.logout-link {
  color: #E53E3E; 
  background-color: rgba(229, 62, 62, 0.05);
  border: 1px solid rgba(229, 62, 62, 0.1);
}

.logout-icon-box {
  background: rgba(229, 62, 62, 0.1);
  color: #E53E3E;
}

.logout-link:hover {
  background-color: rgba(229, 62, 62, 0.1);
  border-color: rgba(229, 62, 62, 0.3);
  color: #E53E3E;
}

.logout-link:hover .logout-icon-box {
  background-color: #E53E3E;
  color: white;
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.25);
}
</style>
