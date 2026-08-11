<template>
  <nav class="admin-sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <div class="logo-duo">
        <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
        <img src="@/assets/VoltMindAccess1.svg" alt="VoltMind" class="logo-volt" />
      </div>
      <div class="brand-text">
        <h1 class="brand-title"><span class="text-volt">Volt</span><span class="text-mind">Mind</span></h1>
        <p class="brand-subtitle">ADMIN ACCESS</p>
      </div>
    </div>
    
    <ul class="sidebar-menu">
      <li class="menu-category">PROGRAMACIÓN COMPLEMENTARIA</li>
      <li>
        <router-link to="/programador-complementarios/dashboard" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-chart-pie" fixed-width />
          </div>
          <span class="menu-text">Dashboard</span>
        </router-link>
      </li>
      <li>
        <router-link to="/programador-complementarios/fichas" class="menu-link" @click="handleMenuClick" :class="{ 'active': $route.path.includes('/fichas') && !$route.path.includes('/directorio') }">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-file-circle-plus" fixed-width />
          </div>
          <span class="menu-text">Solicitudes</span>
        </router-link>
      </li>
      <li>
        <router-link to="/programador-complementarios/directorio" class="menu-link" @click="handleMenuClick">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-folder-open" fixed-width />
          </div>
          <span class="menu-text">Directorio de Fichas</span>
        </router-link>
      </li>
    </ul>

    <div class="sidebar-footer">
      <div class="user-profile">
        <div class="avatar">
          <font-awesome-icon icon="fa-solid fa-user" />
        </div>
        <div class="user-info">
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ userRoleFormatted }}</span>
        </div>
      </div>
      
      <router-link to="/login" class="menu-link logout-link mt-3" @click="handleMenuClick">
        <div class="icon-box logout-icon-box">
          <font-awesome-icon icon="fa-solid fa-right-from-bracket" fixed-width />
        </div>
        <span class="menu-text">Salir</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const userName = ref('');
const userRoleFormatted = ref('');

onMounted(() => {
  userName.value = localStorage.getItem('instructorName') || localStorage.getItem('microsoft_user_name') || 'Usuario VoltMind';
  
  const roleRaw = localStorage.getItem('user_role') || 'Usuario';
  userRoleFormatted.value = roleRaw.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
});

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
  border-right: 1px solid var(--borde);
  width: 240px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 1rem;
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
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--borde);
}

.logo-duo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.logo-sena {
  height: 45px;
  width: auto;
}
.logo-volt {
  height: 50px;
  width: auto;
}
.brand-text {
  text-align: center;
}
.brand-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.text-volt { color: var(--sena-verde); }
.text-mind { color: var(--sena-azul-oscuro); }
.brand-subtitle {
  margin: 2px 0 0;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  letter-spacing: 1px;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.menu-category {
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--texto-secundario);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0.5rem 0 0.25rem 0.5rem;
}

.menu-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.85rem;
  text-decoration: none;
  color: var(--texto-principal);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.menu-link:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.menu-link.router-link-active, .menu-link.active {
  background-color: var(--fondo-app);
  color: var(--sena-verde);
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  width: 24px;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid var(--borde);
  display: flex;
  flex-direction: column;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--fondo-app);
  color: var(--sena-azul-oscuro);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--texto-principal);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.user-role {
  font-size: 0.75rem;
  color: var(--sena-verde);
  font-weight: 600;
}

.logout-link {
  color: #ef4444;
  margin-top: 1rem;
}

.logout-link:hover {
  background: #fef2f2;
}

.logout-link.router-link-active {
  background: transparent;
  box-shadow: none;
}
</style>
