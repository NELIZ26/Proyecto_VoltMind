<script setup>
import { computed } from 'vue';
import { useRole } from '@/composables/useRole';

// Importamos el gestor de roles para proteger el botón de resolución
const { hasRole } = useRole();

const props = defineProps({
  title: { 
    type: String, 
    default: "PANEL DE ALERTAS" 
  },
  alerts: { 
    type: Array, 
    required: true, 
    default: () => [] 
  },
  icon: { 
    type: String, 
    default: "fa-solid fa-bell" 
  }
});

// Definimos el evento que avisa al componente padre (ej. Dashboard) qué alerta se cerró
const emit = defineEmits(['resolve']);

// Asignamos estilos según la gravedad
const getAlertStyle = (severity) => {
  const styles = { 
    critical: 'alert-critical', 
    warning: 'alert-warning', 
    info: 'alert-info' 
  };
  return styles[severity] || 'alert-info';
};

// Asignamos íconos según la gravedad
const getAlertIcon = (severity) => {
  const icons = { 
    critical: 'fa-solid fa-bolt-lightning', 
    warning: 'fa-solid fa-triangle-exclamation', 
    info: 'fa-solid fa-circle-info' 
  };
  return icons[severity] || 'fa-solid fa-bell';
};
</script>

<template>
  <div class="module-card alert-panel-card">
    <h2 class="module-title">
      <font-awesome-icon :icon="icon" /> {{ title }}
      <span class="badge-count" v-if="alerts.length > 0">{{ alerts.length }}</span>
    </h2>

    <div class="alert-list" v-if="alerts.length > 0">
      <div 
        v-for="alert in alerts" 
        :key="alert.id" 
        class="alert-item"
        :class="getAlertStyle(alert.severity)"
      >
        <div class="alert-icon-wrapper">
          <font-awesome-icon :icon="getAlertIcon(alert.severity)" />
        </div>
        
        <div class="alert-content">
          <span class="alert-message">{{ alert.message }}</span>
          <span class="alert-meta">{{ alert.timestamp }} • {{ alert.source }}</span>
        </div>

        <button 
          v-if="hasRole(['dinamizador', 'celador', 'instructor'])"
          class="btn-resolve" 
          title="Marcar como resuelta"
          @click="emit('resolve', alert.id)"
        >
          <font-awesome-icon icon="fa-solid fa-check" />
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <font-awesome-icon icon="fa-solid fa-shield" class="empty-icon" />
      <p>Todos los sistemas operando con normalidad.</p>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   PANEL DE ALERTAS (SENA 2024 - UI Limpia y Profesional)
   ========================================================================== */
.alert-panel-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 48, 64, 0.03);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.module-title {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  text-transform: uppercase;
}

.badge-count {
  background: #E2E8F0;
  color: var(--sena-azul-oscuro);
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: auto;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

/* Scrollbar estilizado para la lista */
.alert-list::-webkit-scrollbar {
  width: 4px;
}
.alert-list::-webkit-scrollbar-thumb {
  background-color: var(--borde);
  border-radius: 4px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  border-left: 4px solid transparent;
  background: var(--fondo-app);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.alert-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.alert-icon-wrapper {
  font-size: 1.1rem;
  margin-top: 2px;
}

.alert-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1; /* Empuja el botón a la derecha */
}

.alert-message {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-principal);
  line-height: 1.3;
}

.alert-meta {
  font-size: 0.6rem;
  color: var(--texto-secundario);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

/* --- ESTILOS DINÁMICOS DE GRAVEDAD --- */
.alert-critical {
  border-left-color: #E53E3E;
  background: rgba(229, 62, 62, 0.05);
}
.alert-critical .alert-icon-wrapper { color: #E53E3E; }

.alert-warning {
  border-left-color: var(--sena-amarillo);
  background: rgba(253, 195, 0, 0.08);
}
.alert-warning .alert-icon-wrapper { color: #D69E2E; }

.alert-info {
  border-left-color: var(--sena-azul-claro);
  background: rgba(80, 229, 249, 0.08);
}
.alert-info .alert-icon-wrapper { color: var(--sena-azul-claro); }

/* --- BOTÓN DE RESOLVER (Interactivo) --- */
.btn-resolve {
  margin-left: auto;
  background: transparent;
  border: 1px solid transparent;
  color: var(--borde);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.alert-item:hover .btn-resolve {
  color: var(--texto-secundario);
  border-color: var(--borde);
  background: var(--sena-blanco);
}

.btn-resolve:hover {
  color: var(--sena-verde) !important;
  border-color: var(--sena-verde) !important;
  background: rgba(57, 169, 0, 0.1) !important;
  transform: scale(1.1);
}

/* --- ESTADO VACÍO (Sin alertas) --- */
.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--texto-secundario);
}
.empty-icon {
  font-size: 2rem;
  color: var(--sena-verde);
  margin-bottom: 0.75rem;
  opacity: 0.5;
}
.empty-state p {
  font-size: 0.75rem;
  font-weight: 600;
  margin: 0;
}
</style>