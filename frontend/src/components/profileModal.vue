<script setup>
import { computed } from "vue";

const props = defineProps({
  apprentice: {
    type: Object,
    required: true,
  },
});

defineEmits(["close"]);

// 🤖 FUNCIÓN PARA GENERAR UN COLOR ÚNICO BASADO EN EL TEXTO
const getUniqueColor = (text, type) => {
  if (!text) return type === "head" ? "#5c4a42" : "#ffd700";

  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Paletas de colores tecnológicos controlados para mantener la estética oscura
  const headColors = [
    "#5c4a42",
    "#2c3e50",
    "#34495e",
    "#7f8c8d",
    "#1e3d59",
    "#433d3c",
    "#2e4057",
    "#1f2421",
  ];
  const neonColors = [
    "#ffd700",
    "#00ffcc",
    "#ff3366",
    "#3399ff",
    "#ff6600",
    "#b533ff",
    "#4ade80",
  ];

  const index = Math.abs(hash);

  if (type === "head") {
    return headColors[index % headColors.length];
  } else {
    return neonColors[index % neonColors.length];
  }
};

// Propiedades computadas para asignar los colores según el aprendiz actual
const robotHeadColor = computed(() =>
  getUniqueColor(props.apprentice.name, "head"),
);
const robotNeonColor = computed(() =>
  getUniqueColor(props.apprentice.doc, "neon"),
);
</script>

<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <div class="modal-header">
        <div class="header-indicator"></div>
        <h3>FICHA TÉCNICA DEL APRENDIZ</h3>
      </div>

      <div class="profile-summary">
        <div
          class="avatar-container"
          :style="{ '--robot-neon': robotNeonColor }"
        >
          <img
            v-if="apprentice.photo"
            :src="apprentice.photo"
            alt="Foto del Aprendiz"
            class="avatar-image"
          />

          <div v-else class="robot-avatar">
            <div class="robot-antenna">
              <div
                class="antenna-ball"
                :style="{
                  backgroundColor: robotNeonColor,
                  boxShadow: '0 0 8px ' + robotNeonColor,
                }"
              ></div>
            </div>
            <div
              class="robot-head"
              :style="{ backgroundColor: robotHeadColor }"
            >
              <div class="robot-visor">
                <div class="visor-reflection"></div>
              </div>
              <div class="robot-mouth">
                <div class="mouth-dot"></div>
                <div class="mouth-dot"></div>
                <div class="mouth-dot"></div>
                <div class="mouth-dot"></div>
              </div>
            </div>
            <div class="robot-neck-bolts"></div>
          </div>
        </div>

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
/* ==========================================================================
   ESTILOS DEL MODAL (Alineados estrictamente a tus variables de estilo)
   ========================================================================== */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  font-family: var(--fuente-principal, "Inter", sans-serif);
}

.modal-card {
  background: #0d0d0f;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Encabezado */
.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1.5rem;
}

.header-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--sena-verde, #39a900);
  border-radius: 2px;
  box-shadow: 0 0 10px rgba(57, 169, 0, 0.4);
}

.modal-header h3 {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario, #a0aec0);
  margin: 0;
  letter-spacing: 0.08em;
}

/* Sección de Foto / Perfil Superior */
.profile-summary {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  margin-bottom: 1.25rem;
}

.avatar-container {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  background: #121214;
  border: 2px solid var(--borde, rgba(255, 255, 255, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

/* ==========================================================================
   DISEÑO DEL ROBOT AVATAR (CSS PURO)
   ========================================================================== */
.robot-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  padding-top: 8px;
}

/* Antena Superior */
.robot-antenna {
  width: 3px;
  height: 8px;
  background: #a0aec0;
  position: relative;
  margin-bottom: -1px;
  z-index: 2;
}

.antenna-ball {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
}

/* Cabeza del Robot */
.robot-head {
  width: 42px;
  height: 34px;
  border-radius: 8px 8px 12px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 6px 4px;
  position: relative;
  z-index: 3;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
  transition: background-color 0.3s ease;
}

/* Visor y Reflejo */
.robot-visor {
  width: 34px;
  height: 9px;
  background: #000000;
  border-radius: 3px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.visor-reflection {
  width: 12px;
  height: 100%;
  background: rgba(255, 255, 255, 0.4);
  transform: skewX(-30deg);
  position: absolute;
  left: 6px;
}

/* Altavoz / Boca de Puntos */
.robot-mouth {
  display: flex;
  gap: 3px;
  margin-top: 2px;
}

.mouth-dot {
  width: 3px;
  height: 3px;
  background: #212121;
  border-radius: 50%;
  opacity: 0.8;
}

/* Conectores / Orejas Laterales */
.robot-neck-bolts {
  width: 48px;
  height: 8px;
  background: #3a2f2a;
  position: absolute;
  bottom: 14px;
  z-index: 1;
  border-radius: 2px;
}

.profile-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.name-highlight {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--texto-principal, #ffffff);
  margin: 0;
  line-height: 1.3;
}

/* Cuerpo de Datos */
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.data-row {
  display: flex;
  gap: 1rem;
}

.data-row .data-group {
  flex: 1;
}

.data-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.data-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--texto-secundario, #a0aec0);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  opacity: 0.7;
}

.data-value {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--texto-principal, #ffffff);
}

.monospace-text,
.enum-text {
  font-family: monospace;
  letter-spacing: 0.02em;
}

.email-text {
  color: var(--texto-principal, #ffffff);
  opacity: 0.85;
  font-size: 0.85rem;
}

.badge-role {
  align-self: flex-start;
  background: rgba(57, 169, 0, 0.08);
  border: 1px solid rgba(57, 169, 0, 0.2);
  color: var(--sena-verde-claro, #deff9a);
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Footer y Botón Cerrar */
.modal-footer {
  margin-top: 1.75rem;
  display: flex;
  justify-content: flex-end;
}

.btn-modal-close {
  background: transparent;
  border: 1px solid var(--borde, rgba(255, 255, 255, 0.08));
  color: var(--texto-secundario, #a0aec0);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
}

.btn-modal-close:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--texto-principal, #ffffff);
}

/* Al hacer hover, el borde del contenedor toma el color de la luz neón del robot */
.modal-card:hover .avatar-container {
  border-color: var(--robot-neon, var(--sena-verde, #39a900));
  box-shadow: 0 0 12px var(--robot-neon, rgba(57, 169, 0, 0.2));
  transition: all 0.3s ease;
}
</style>
