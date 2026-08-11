<template>
  <div class="admin-view-shell">
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>DASHBOARD COMPLEMENTARIAS</h1>
          <p class="header-meta">
            Resumen general de las solicitudes de formación
            <span v-if="store.indicadores">
              | {{ store.indicadores.total }} solicitudes registradas
            </span>
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-limpiar" title="Recargar la información desde el servidor" @click="store.cargarTodo()">
          <font-awesome-icon icon="fa-solid fa-arrows-rotate" /> Actualizar
        </button>
      </div>
    </header>

    <div v-if="store.errorConexion" class="estado-panel">
      <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="alerta-icono" />
      <div>
        <strong>Sin conexión al servidor</strong>
        <p>No se pudo cargar la información del dashboard.</p>
      </div>
    </div>
    
    <div v-else-if="!store.indicadores" class="loading-wrapper">
      <GlobalSpinner message="Cargando métricas..." :isModal="false" />
    </div>
    
    <template v-else>
      <section class="indicadores-grid">
        <!-- Tarjeta de Solicitudes Totales -->
        <article class="module-card ind-card principal">
          <div class="card-icon principal-icon">
            <font-awesome-icon icon="fa-solid fa-file-invoice" />
          </div>
          <div class="card-content">
            <h2 class="ind-titulo">TOTAL SOLICITUDES</h2>
            <p class="ind-numero">{{ store.indicadores.total }}</p>
            <p class="ind-contexto">Registradas en el sistema</p>
          </div>
        </article>

        <!-- Tarjeta de Aprendices Inscritos -->
        <article class="module-card ind-card secundarios">
          <div class="card-icon info-icon">
            <font-awesome-icon icon="fa-solid fa-users" />
          </div>
          <div class="card-content">
            <h2 class="ind-titulo">TOTAL INSCRITOS</h2>
            <p class="ind-numero">{{ store.indicadores.inscritos_total }}</p>
            <p class="ind-contexto">Aprendices en formación</p>
          </div>
        </article>
      </section>

      <!-- Desglose por estados -->
      <section class="estados-section module-card">
        <h2 class="section-title">
          <font-awesome-icon icon="fa-solid fa-chart-pie" /> Desglose por Estado
        </h2>
        
        <div class="estados-grid">
          <div class="estado-box pendiente">
            <div class="estado-header">
              <span class="estado-nombre">Pendientes</span>
              <font-awesome-icon icon="fa-solid fa-clock" />
            </div>
            <div class="estado-valor">{{ store.indicadores.pendientes }}</div>
            <div class="barra-mini">
              <div class="barra-relleno" :style="{ width: porcentaje(store.indicadores.pendientes) + '%' }"></div>
            </div>
          </div>

          <div class="estado-box publicada">
            <div class="estado-header">
              <span class="estado-nombre">Publicadas</span>
              <font-awesome-icon icon="fa-solid fa-bullhorn" />
            </div>
            <div class="estado-valor">{{ store.indicadores.publicadas }}</div>
            <div class="barra-mini">
              <div class="barra-relleno" :style="{ width: porcentaje(store.indicadores.publicadas) + '%' }"></div>
            </div>
          </div>

          <div class="estado-box ejecucion">
            <div class="estado-header">
              <span class="estado-nombre">En Ejecución</span>
              <font-awesome-icon icon="fa-solid fa-person-chalkboard" />
            </div>
            <div class="estado-valor">{{ store.indicadores.en_ejecucion }}</div>
            <div class="barra-mini">
              <div class="barra-relleno" :style="{ width: porcentaje(store.indicadores.en_ejecucion) + '%' }"></div>
            </div>
          </div>

          <div class="estado-box cancelada">
            <div class="estado-header">
              <span class="estado-nombre">Canceladas</span>
              <font-awesome-icon icon="fa-solid fa-ban" />
            </div>
            <div class="estado-valor">{{ store.indicadores.canceladas }}</div>
            <div class="barra-mini">
              <div class="barra-relleno" :style="{ width: porcentaje(store.indicadores.canceladas) + '%' }"></div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Solicitudes de Atención Prioritaria -->
      <section v-if="solicitudesPendientes.length > 0" class="atencion-section module-card">
        <div class="atencion-header">
          <h2 class="section-title text-alerta">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> Atención Requerida
          </h2>
          <span class="atencion-badge">{{ solicitudesPendientes.length }} pendientes</span>
        </div>
        <p class="atencion-desc">
          Las siguientes solicitudes han sido enviadas por los instructores y requieren ser gestionadas para su publicación:
        </p>
        
        <div class="atencion-lista">
          <router-link 
            v-for="s in solicitudesPendientes" 
            :key="s.id"
            to="/programador-complementarios/fichas/tablero"
            class="atencion-item"
            @click="store.filtroEstado = 'Pendiente'"
          >
            <div class="item-icono">
              <font-awesome-icon icon="fa-solid fa-file-signature" />
            </div>
            <div class="item-info">
              <h3>{{ s.nombre_programa }}</h3>
              <p>Instructor: {{ s.nombre_instructor }} · Solicitado: {{ s.fecha_creacion }}</p>
            </div>
            <div class="item-accion">
              <font-awesome-icon icon="fa-solid fa-arrow-right" />
            </div>
          </router-link>
        </div>
      </section>
      <section v-else class="atencion-section module-card success-state">
        <font-awesome-icon icon="fa-solid fa-circle-check" class="success-icon" />
        <div>
          <h2 class="section-title">Todo al día</h2>
          <p>No hay solicitudes pendientes de revisión en este momento.</p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useComplementariasStore } from '@/stores/complementarias';
import GlobalSpinner from '@/components/GlobalSpinner.vue';

const store = useComplementariasStore();

onMounted(() => {
  if (!store.indicadores && !store.errorConexion) {
    store.initStore();
  }
});

const porcentaje = (valor) => {
  if (!store.indicadores || store.indicadores.total === 0) return 0;
  return Math.round((valor / store.indicadores.total) * 100);
};

const solicitudesPendientes = computed(() => {
  return store.solicitudes.filter(s => s.estado === 'Pendiente').slice(0, 5); // Máximo mostrar 5 para no saturar
});
</script>

<style scoped>
.admin-view-shell {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid var(--borde);
  padding-bottom: 1rem;
}

.header-left h1 {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 4px;
}

.header-meta {
  font-size: 0.85rem;
  color: var(--texto-secundario);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chip-demo {
  background: #fdc300;
  color: #000;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 1px;
}

.btn-limpiar {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-limpiar:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

.indicadores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.ind-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.principal-icon {
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde);
}

.info-icon {
  background: rgba(0, 50, 77, 0.1);
  color: var(--sena-azul-oscuro);
}

.ind-titulo {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-secundario);
  margin: 0 0 4px;
  letter-spacing: 1px;
}

.ind-numero {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--texto-principal);
  margin: 0 0 2px;
  line-height: 1;
}

.ind-contexto {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  margin: 0;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  margin: 0 0 1.25rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.estados-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.estado-box {
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid var(--borde);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.estado-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 800;
}

.estado-valor {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--texto-principal);
}

.barra-mini {
  height: 6px;
  background: var(--borde);
  border-radius: 4px;
  overflow: hidden;
}

.estado-box.pendiente .estado-header { color: #fdc300; }
.estado-box.pendiente .barra-relleno { background: #fdc300; height: 100%; border-radius: 4px; }

.estado-box.publicada .estado-header { color: var(--sena-azul-oscuro); }
.estado-box.publicada .barra-relleno { background: var(--sena-azul-oscuro); height: 100%; border-radius: 4px; }

.estado-box.ejecucion .estado-header { color: var(--sena-verde); }
.estado-box.ejecucion .barra-relleno { background: var(--sena-verde); height: 100%; border-radius: 4px; }

.estado-box.cancelada .estado-header { color: #e53e3e; }
.estado-box.cancelada .barra-relleno { background: #e53e3e; height: 100%; border-radius: 4px; }

.atencion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-alerta {
  color: #fdc300;
}

.atencion-badge {
  background: rgba(253, 195, 0, 0.15);
  color: #cc9d00;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
}

.atencion-desc {
  font-size: 0.9rem;
  color: var(--texto-secundario);
  margin-bottom: 1.5rem;
}

.atencion-lista {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.atencion-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--borde);
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.atencion-item:hover {
  border-color: #fdc300;
  background: rgba(253, 195, 0, 0.05);
  transform: translateX(4px);
}

.item-icono {
  width: 40px;
  height: 40px;
  background: rgba(253, 195, 0, 0.15);
  color: #cc9d00;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--texto-principal);
}

.item-info p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.item-accion {
  color: var(--texto-secundario);
}

.atencion-item:hover .item-accion {
  color: #fdc300;
}

.success-state {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
}

.success-icon {
  font-size: 3rem;
  color: var(--sena-verde);
}

.success-state h2 {
  margin: 0 0 4px;
}

.success-state p {
  margin: 0;
  color: var(--texto-secundario);
}

.loading-wrapper {
  padding: 4rem;
  display: flex;
  justify-content: center;
}
</style>
