<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>GESTOR DE FICHAS Y CATÁLOGO</h1>
          <p class="header-meta">
            Centro de gestión académica | VoltMind
          </p>
        </div>
      </div>
    </header>

    <main class="dash-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 24px;">
      <!-- Tarjeta Catálogo -->
      <article class="module-card">
        <h2 class="module-title">
          <font-awesome-icon icon="fa-solid fa-book" /> CATÁLOGO DE PROGRAMAS
        </h2>
        <p style="margin-bottom: 20px; color: #8a8d93;">
          Gestione los programas de formación disponibles, asigne horas y actualice versiones antes de asignarlos a una ficha.
        </p>
        <button class="btn-principal" @click="showModalCatalogo = true" style="width: 100%; display: flex; justify-content: center; padding: 12px;">
          <font-awesome-icon icon="fa-solid fa-book-open" /> 
          ABRIR CATÁLOGO
        </button>
      </article>

      <!-- Tarjeta Nueva Ficha -->
      <article class="module-card">
        <h2 class="module-title">
          <font-awesome-icon icon="fa-solid fa-plus-circle" /> NUEVA FICHA TITULADA
        </h2>
        <p style="margin-bottom: 20px; color: #8a8d93;">
          Registre una nueva ficha de formación titulada vinculándola a un programa existente en el catálogo.
        </p>
        <button class="btn-principal btn-naranja" @click="showModalNueva = true" style="width: 100%; display: flex; justify-content: center; padding: 12px; background: #FF6B00;">
          <font-awesome-icon icon="fa-solid fa-plus" /> 
          CREAR NUEVA FICHA
        </button>
      </article>
    </main>

    <!-- Modales -->
    <ModalNuevaFicha v-model:show="showModalNueva" />
    <ModalCatalogoProgramas v-model:show="showModalCatalogo" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ModalNuevaFicha from '@/components/admin/modals/ModalNuevaFicha.vue';
import ModalCatalogoProgramas from '@/components/admin/modals/ModalCatalogoProgramas.vue';
import { useTituladasStore } from '@/stores/tituladas';

const store = useTituladasStore();

const showModalNueva = ref(false);
const showModalCatalogo = ref(false);

onMounted(() => {
  store.initStore();
});
</script>

<style scoped>
.admin-view-shell {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.module-card {
  background: var(--fondo-tarjetas, #1E232B);
  border: 1px solid var(--borde, #2D333B);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.module-title {
  color: var(--texto-principal, #ffffff);
  font-size: 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-principal {
  background: var(--sena-verde, #39A900);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 8px;
}
.btn-principal:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--fondo-tarjetas);
  padding: 1.25rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--borde);
  border-left: 5px solid var(--sena-verde);
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  gap: 1rem;
  flex-wrap: wrap;
}
.environment-badge h1 {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0;
}
.header-meta {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
