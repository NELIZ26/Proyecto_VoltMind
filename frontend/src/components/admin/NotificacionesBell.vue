<template>
  <div ref="raiz" class="campana-wrapper">
    <!-- Botón campana con badge de no leídas -->
    <button
      class="btn-campana"
      :class="{ activa: abierta }"
      :title="`Notificaciones (${store.totalNoLeidas} sin leer)`"
      aria-label="Abrir notificaciones"
      @click="abierta = !abierta"
    >
      <font-awesome-icon icon="fa-solid fa-bell" />
      <span v-if="store.totalNoLeidas > 0" class="badge">
        {{ store.totalNoLeidas > 9 ? '9+' : store.totalNoLeidas }}
      </span>
    </button>

    <!-- Panel con la lista de avisos -->
    <transition name="panel">
      <div v-if="abierta" class="panel">
        <header class="panel-header">
          <h3>NOTIFICACIONES</h3>
          <span v-if="store.totalNoLeidas" class="panel-contador">{{ store.totalNoLeidas }} sin leer</span>
        </header>

        <p v-if="store.notificaciones.length === 0" class="panel-vacio">
          <font-awesome-icon icon="fa-solid fa-bell" />
          No hay notificaciones por ahora.
        </p>

        <ul v-else class="lista">
          <li v-for="n in store.notificaciones" :key="n.id">
            <button
              class="aviso"
              :class="{ 'no-leida': !n.leida }"
              :title="n.ficha_relacionada ? 'Abrir la solicitud relacionada' : 'Marcar como leída'"
              @click="abrirAviso(n)"
            >
              <span class="aviso-punto" aria-hidden="true"></span>
              <span class="aviso-cuerpo">
                <span class="aviso-texto">{{ n.texto }}</span>
                <span class="aviso-fecha">{{ formatearFecha(n.fecha) }}</span>
              </span>
              <font-awesome-icon
                v-if="n.ficha_relacionada"
                icon="fa-solid fa-arrow-up-right-from-square"
                class="aviso-enlace"
              />
            </button>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup>
// Campana de notificaciones (módulo Fichas Complementarias).
// Polling cada ~45 s vía el store; cada aviso enlaza a su solicitud y se
// marca como leído (PATCH) al abrirlo. Reutilizable: en el panel admin
// (destinatario 'admin') y en la vista del instructor (su correo).
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useNotificacionesStore } from '@/stores/notificaciones';

const props = defineProps({
  // 'admin' o el correo institucional del instructor
  destinatario: { type: String, default: 'admin' },
  // Ruta a la que navega un aviso con solicitud relacionada
  rutaSolicitud: { type: String, default: '/admin/complementarias' },
});

const store = useNotificacionesStore();
const router = useRouter();
const abierta = ref(false);
const raiz = ref(null);

const cerrarSiClicFuera = (evento) => {
  if (abierta.value && raiz.value && !raiz.value.contains(evento.target)) {
    abierta.value = false;
  }
};

onMounted(() => {
  store.configurarDestinatario(props.destinatario);
  store.iniciarPolling();
  document.addEventListener('click', cerrarSiClicFuera);
});

onBeforeUnmount(() => {
  store.detenerPolling();
  document.removeEventListener('click', cerrarSiClicFuera);
});

/** Marca el aviso como leído y navega a la solicitud relacionada. */
const abrirAviso = async (n) => {
  await store.marcarLeida(n.id);
  abierta.value = false;
  if (n.ficha_relacionada) {
    router.push({ path: props.rutaSolicitud, query: { solicitud: n.ficha_relacionada } });
  }
};

const formatearFecha = (iso) => {
  if (!iso) return '';
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleString('es-CO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
};
</script>

<style scoped>
/* Flotante: arriba a la derecha en escritorio; en móvil baja junto al
   botón de modo oscuro para no chocar con la topbar de hamburguesa. */
.campana-wrapper {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 95;
}

.btn-campana {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--borde);
  background: var(--fondo-tarjetas);
  color: var(--sena-azul-oscuro);
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px var(--sombra-suave);
  transition: all 0.2s ease;
}

.btn-campana:hover,
.btn-campana.activa {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
  transform: translateY(-2px);
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 10px;
  background: #e53e3e;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--fondo-tarjetas);
  box-sizing: border-box;
}

/* ── Panel desplegable ── */
.panel {
  position: absolute;
  top: 56px;
  right: 0;
  width: 340px;
  max-width: calc(100vw - 48px);
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(0, 48, 64, 0.16);
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.9rem 1.1rem;
  border-bottom: 1px solid var(--borde);
}

.panel-header h3 {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-principal);
}

.panel-contador {
  background: rgba(57, 169, 0, 0.12);
  color: var(--sena-verde-oscuro);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.68rem;
  font-weight: 800;
}

.panel-vacio {
  margin: 0;
  padding: 1.75rem 1rem;
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.82rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.panel-vacio svg {
  font-size: 1.4rem;
  opacity: 0.4;
}

.lista {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 340px;
  overflow-y: auto;
}

.aviso {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 0.8rem 1.1rem;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--fondo-app);
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease;
}

.aviso:hover {
  background: rgba(57, 169, 0, 0.06);
}

.aviso-punto {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  margin-top: 6px;
  flex-shrink: 0;
}

.aviso.no-leida .aviso-punto {
  background: var(--sena-verde);
}

.aviso-cuerpo {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.aviso-texto {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  line-height: 1.35;
}

.aviso.no-leida .aviso-texto {
  color: var(--texto-principal);
  font-weight: 700;
}

.aviso-fecha {
  font-size: 0.68rem;
  color: var(--texto-secundario);
  font-family: monospace;
}

.aviso-enlace {
  font-size: 0.7rem;
  color: var(--texto-secundario);
  margin-top: 5px;
}

/* Animación de apertura */
.panel-enter-active,
.panel-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Móvil: junto al botón flotante de modo oscuro ── */
@media (max-width: 992px) {
  .campana-wrapper {
    top: auto;
    bottom: 84px;
    right: 24px;
  }

  .panel {
    top: auto;
    bottom: 56px;
  }
}
</style>
