<template>
  <!--
    Tarjeta de una solicitud de ficha complementaria.
    Se usa en las dos vistas del tablero del admin:
      · Tablero por estado  → chip de inscritos + rango de formación
      · Carpetas por mes    → badge de estado + fecha de solicitud (mostrar-estado)
  -->
  <article
    class="tarjeta"
    role="button"
    tabindex="0"
    @click="$emit('abrir', solicitud)"
    @keydown.enter="$emit('abrir', solicitud)"
  >
    <div class="tarjeta-top">
      <span class="tarjeta-codigo">{{ solicitud.codigo_programa }} · v{{ solicitud.version_programa || '1' }}</span>
      <span v-if="mostrarEstado" :class="['status-badge', claseEstado(solicitud.estado)]">
        {{ solicitud.estado }}
      </span>
      <span v-else class="tarjeta-inscritos" :title="`${solicitud.cantidad_inscritos} inscritos`">
        <font-awesome-icon icon="fa-solid fa-users" /> {{ solicitud.cantidad_inscritos }}
      </span>
    </div>
    <h3 class="tarjeta-programa">{{ solicitud.nombre_programa }}</h3>
    <p class="tarjeta-dato">
      <font-awesome-icon icon="fa-solid fa-user-tie" fixed-width /> {{ solicitud.nombre_instructor }}
    </p>
    <p class="tarjeta-dato">
      <font-awesome-icon icon="fa-solid fa-location-dot" fixed-width />
      {{ solicitud.municipio || 'Sin municipio' }}<template v-if="solicitud.jornada"> · {{ solicitud.jornada }}</template>
    </p>
    <p class="tarjeta-dato">
      <font-awesome-icon icon="fa-solid fa-calendar-days" fixed-width />
      <template v-if="mostrarEstado">Solicitada el {{ solicitud.fecha_creacion || 'sin fecha' }}</template>
      <span v-else class="tarjeta-fechas">{{ rangoFormacion }}</span>
    </p>
    <p
      v-if="solicitud.estado === 'Publicada'"
      class="tarjeta-aviso"
      :class="solicitud.notificado ? 'avisado' : 'sin-avisar'"
      :title="solicitud.notificado ? 'El instructor ya recibió el aviso de publicación' : 'El instructor aún no ha sido avisado'"
    >
      <font-awesome-icon :icon="solicitud.notificado ? 'fa-solid fa-envelope' : 'fa-solid fa-triangle-exclamation'" fixed-width />
      {{ etiquetaAviso }}
    </p>
    <footer class="tarjeta-footer">
      <div class="mini-pasos" :title="`Seguimiento: ${completados} de ${PASOS_SEGUIMIENTO.length} pasos`">
        <span
          v-for="paso in PASOS_SEGUIMIENTO"
          :key="paso.campo"
          class="mini-paso"
          :class="{ hecho: solicitud[paso.campo] }"
        ></span>
        <span class="mini-pasos-texto">{{ completados }}/{{ PASOS_SEGUIMIENTO.length }}</span>
      </div>
      <span v-if="solicitud.codigo_ficha" class="tarjeta-ficha">Ficha {{ solicitud.codigo_ficha }}</span>
    </footer>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import {
  PASOS_SEGUIMIENTO,
  claseEstado,
  pasosCompletados,
  formatearRango,
} from '@/stores/complementarias';

const props = defineProps({
  solicitud: { type: Object, required: true },
  // true → badge de estado y fecha de solicitud (vista de carpetas por mes)
  mostrarEstado: { type: Boolean, default: false },
});

defineEmits(['abrir']);

const completados = computed(() => pasosCompletados(props.solicitud));

const rangoFormacion = computed(() =>
  formatearRango(props.solicitud.fecha_inicio_formacion, props.solicitud.fecha_fin_formacion)
);

/** Marca de aviso en las tarjetas Publicadas: "Avisado el DD/MM" o "Pendiente de avisar". */
const etiquetaAviso = computed(() => {
  if (!props.solicitud.notificado) return 'Pendiente de avisar';
  const fecha = new Date(props.solicitud.notificado);
  if (Number.isNaN(fecha.getTime())) return 'Avisado';
  return `Avisado el ${fecha.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit' })}`;
});
</script>

<style scoped>
/* Tarjeta de solicitud (mismo estilo institucional del tablero) */
.tarjeta {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tarjeta:hover,
.tarjeta:focus-visible {
  border-color: var(--sena-verde);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.12);
  outline: none;
}

.tarjeta-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tarjeta-codigo {
  font-family: monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.tarjeta-inscritos {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(57, 169, 0, 0.12);
  color: var(--sena-verde-oscuro);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 800;
}

.tarjeta-programa {
  font-size: 0.92rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0;
  line-height: 1.3;
}

.tarjeta-dato {
  margin: 0;
  font-size: 0.78rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
}

.tarjeta-fechas {
  font-family: monospace;
  font-size: 0.75rem;
}

/* Marca de aviso al instructor (solo tarjetas Publicadas) */
.tarjeta-aviso {
  margin: 2px 0 0;
  font-size: 0.72rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  padding: 3px 8px;
  width: fit-content;
}

.tarjeta-aviso.avisado {
  background: rgba(57, 169, 0, 0.12);
  color: var(--sena-verde-oscuro);
}

.tarjeta-aviso.sin-avisar {
  background: rgba(253, 195, 0, 0.18);
  color: #8a6d00;
}

[data-theme="dark"] .tarjeta-aviso.sin-avisar { color: #fdc300; }

.tarjeta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  padding-top: 8px;
  border-top: 1px dashed var(--borde);
}

.tarjeta-ficha {
  font-family: monospace;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--sena-verde-oscuro);
}

/* Mini indicador del checklist (4 pasos) */
.mini-pasos {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mini-paso {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--borde);
  transition: background 0.2s ease;
}

.mini-paso.hecho {
  background: var(--sena-verde);
}

.mini-pasos-texto {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--texto-secundario);
  margin-left: 4px;
}

/* Badge de estado (vista de carpetas) */
.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.8rem;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.status-green {
  background: rgba(57, 169, 0, 0.15);
  color: var(--sena-verde-oscuro);
}

.status-blue {
  background: rgba(0, 48, 64, 0.1);
  color: var(--sena-azul-oscuro);
}

[data-theme="dark"] .status-blue {
  background: rgba(80, 229, 249, 0.12);
}

.status-red {
  background: rgba(244, 67, 54, 0.15);
  color: #d32f2f;
}

.status-yellow {
  background: rgba(253, 195, 0, 0.18);
  color: #8a6d00;
}

[data-theme="dark"] .status-yellow { color: #fdc300; }
</style>
