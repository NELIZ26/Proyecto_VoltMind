<template>
  <div class="gestor-shell">
    <SidebarGestorFichas />
    
    <main class="gestor-main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
      
      <DarkModeToggle />
    </main>
  </div>
</template>

<script setup>
import SidebarGestorFichas from '@/components/SidebarGestorFichas.vue';
import DarkModeToggle from '@/components/DarkModeToggle.vue';
</script>

<style scoped>
.gestor-shell {
  display: flex;
  min-height: 100vh;
  background-color: var(--fondo-app);
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
}

.gestor-main-content {
  flex: 1;
  margin-left: 280px; /* Ancho del sidebar */
  padding: 32px 40px;
  background-color: var(--fondo-app);
  min-height: 100vh;
  position: relative;
  transition: margin-left 0.3s ease;
}

/* Transiciones de página */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
