<template>
  <div class="admin-shell">
    <!-- Overlay Móvil -->
    <div 
      class="mobile-overlay" 
      :class="{ 'overlay-active': isSidebarOpen }"
      @click="closeSidebar"
    ></div>

    <AdminSidebar 
      :isOpen="isSidebarOpen" 
      @close="closeSidebar" 
    />
    
    <main class="admin-main-content">
      <!-- Topbar Móvil (Hamburguesa) -->
      <div class="mobile-topbar">
        <button class="btn-hamburger" @click="toggleSidebar">
          <font-awesome-icon icon="fa-solid fa-bars" />
        </button>
        <div class="mobile-brand">
          <span class="text-volt">Volt</span><span class="text-mind">Mind</span>
        </div>
      </div>

      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
      
      <!-- Botón Flotante Global de Modo Oscuro -->
      <DarkModeToggle />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import AdminSidebar from '@/components/AdminSidebar.vue';
import DarkModeToggle from '@/components/DarkModeToggle.vue';

const isSidebarOpen = ref(false);

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

const closeSidebar = () => {
  isSidebarOpen.value = false;
};
</script>

<style scoped>
.admin-shell {
  display: flex;
  min-height: 100vh;
  background-color: var(--fondo-app);
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
  box-sizing: border-box;
  user-select: none;
}

.admin-main-content {
  flex: 1;
  margin-left: 280px; 
  padding: 1.5rem;
  min-height: 100vh;
  transition: margin-left 0.3s ease, padding 0.3s ease;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 48, 64, 0.5);
  backdrop-filter: blur(2px);
  z-index: 90;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.mobile-overlay.overlay-active {
  opacity: 1;
  pointer-events: auto;
}

.mobile-topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  background-color: var(--fondo-tarjetas);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--borde);
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

.btn-hamburger {
  background: transparent;
  border: none;
  color: var(--texto-principal);
  font-size: 1.4rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background-color: var(--fondo-app);
  border: 1px solid var(--borde);
}

.btn-hamburger:active {
  background-color: var(--sena-verde);
  color: white;
}

.mobile-brand {
  font-size: 1.2rem;
  font-weight: 800;
}

.text-volt { color: var(--sena-azul-oscuro); }
.text-mind { color: var(--sena-verde); }

/* Simple fade transition for router views */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 992px) {
  .admin-main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .mobile-topbar {
    display: flex;
  }
  
  .mobile-overlay {
    display: block;
  }
}
</style>
