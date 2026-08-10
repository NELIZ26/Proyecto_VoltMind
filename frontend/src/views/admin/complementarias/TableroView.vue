<template>
  <main class="tablero">
    <section
      v-for="estado in columnasVisibles"
      :key="estado"
      class="columna"
      :class="claseColumna(estado)"
    >
      <header class="columna-header">
        <h2>{{ estado }}</h2>
        <span class="columna-contador">{{ agrupadas[estado].length }}</span>
      </header>

      <p v-if="agrupadas[estado].length === 0" class="columna-vacia">
        Sin solicitudes {{ store.busqueda || store.filtroEstado || store.filtroMunicipio || store.filtroJornada || store.filtroInstructor ? 'con los filtros aplicados' : 'en este estado' }}.
      </p>

      <TarjetaComplementaria
        v-for="s in agrupadas[estado]"
        :key="s.id"
        :solicitud="s"
        @abrir="abrirDetalle"
      />
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue';
import { useComplementariasStore, ESTADOS_TABLERO } from '@/stores/complementarias';
import TarjetaComplementaria from '@/components/admin/TarjetaComplementaria.vue';

const store = useComplementariasStore();
const emit = defineEmits(['abrir-detalle']);

const abrirDetalle = (solicitud) => {
  emit('abrir-detalle', solicitud);
};

// Agrupación por estado para el tablero (orden: Publicada → En Ejecución → Cancelada)
const agrupadas = computed(() => {
  const grupos = Object.fromEntries(ESTADOS_TABLERO.map((e) => [e, []]));
  for (const s of store.filtradas) {
    if (grupos[s.estado]) grupos[s.estado].push(s);
  }
  return grupos;
});

// Con filtro de estado activo, el tablero muestra solo esa columna
const columnasVisibles = computed(() =>
  store.filtroEstado ? [store.filtroEstado] : ESTADOS_TABLERO
);

const claseColumna = (estado) => ({
  'col-pendiente': estado === 'Pendiente',
  'col-publicada': estado === 'Publicada',
  'col-ejecucion': estado === 'En Ejecución',
  'col-cancelada': estado === 'Cancelada',
});
</script>

<style scoped>
/* ══ TABLERO POR ESTADO ══ */
.tablero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  align-items: start;
}

.columna {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.col-pendiente { border-top: 4px solid #fdc300; }
.col-publicada { border-top: 4px solid var(--sena-azul-oscuro); }
.col-ejecucion { border-top: 4px solid var(--sena-verde); }
.col-cancelada { border-top: 4px solid #e53e3e; }

.columna-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0.5rem;
}

.columna-header h2 {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin: 0;
  color: var(--texto-principal);
}

.columna-contador {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  min-width: 28px;
  text-align: center;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--texto-secundario);
}

.columna-vacia {
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.8rem;
  font-style: italic;
  padding: 1.5rem 0.5rem;
  margin: 0;
  border: 1px dashed var(--borde);
  border-radius: 12px;
}

@media (max-width: 992px) {
  .tablero {
    grid-template-columns: 1fr;
  }
}
</style>
