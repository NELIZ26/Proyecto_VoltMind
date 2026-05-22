<script setup>
import UserAvatar from "@/components/UserAvatar.vue";

const props = defineProps({
  apprentice: {
    type: Object,
    required: true,
  },
});

defineEmits(["close"]);
</script>

<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <div class="modal-header">
        <div class="header-indicator"></div>
        <h3>FICHA TÉCNICA DEL APRENDIZ</h3>
      </div>

      <div class="profile-summary">
        <UserAvatar 
          :src="apprentice.photo" 
          :alt="apprentice.name" 
        />

        <div class="profile-title">
          <span class="data-label">Nombre Completo</span>
          <h2 class="name-highlight">{{ apprentice.name }}</h2>
        </div>
      </div>

      <div class="modal-body">
        <div class="data-row">
          <div class="data-group">
            <span class="data-label">Documento de Identidad</span>
            <span class="data-value monospace-text">{{ apprentice.doc }}</span>
          </div>

          <div class="data-group">
            <span class="data-label">Rol en el Sistema</span>
            <span class="badge-role">Aprendiz SENA</span>
          </div>
        </div>

        <div class="data-group text-left">
          <span class="data-label">Correo Institucional</span>
          <span class="data-value email-text">{{ apprentice.email }}</span>
        </div>

        <div class="data-group text-left">
          <span class="data-label">Número de Teléfono</span>
          <span class="data-value enum-text">{{
            apprentice.enum || "No registrado"
          }}</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-modal-close" @click="$emit('close')">CERRAR</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 48, 64, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
}

.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--sena-verde);
  border-radius: 2px;
}

.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
}

.profile-summary {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--borde);
  margin-bottom: 1.25rem;
}

.profile-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-highlight {
  font-size: 1.1rem;
  color: var(--sena-azul-oscuro);
  margin: 0;
}

.data-row {
  display: flex;
  gap: 2rem;
}

.badge-role {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.7rem;
  display: inline-block;
  width: fit-content;
}

.data-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 1rem;
  text-align: left;
}

.data-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--texto-secundario);
  text-transform: uppercase;
}

.data-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--sena-azul-oscuro);
}

.modal-footer {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.btn-modal-close {
  background: var(--sena-azul-oscuro);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-modal-close:hover {
  background: #001F2A;
}
</style>