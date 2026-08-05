<template>
  <div class="admin-view-shell">
    <!-- Encabezado institucional -->
    <header class="dash-header">
      <div class="header-left">
        <div class="environment-badge">
          <h1>FICHAS TITULADAS</h1>
          <p class="header-meta">
            Programación académica de la etapa lectiva
            <span v-if="store.indicadores">
              | {{ store.indicadores.total_fichas }} fichas ·
              {{ store.indicadores.promedio_programacion }}% programado en promedio
            </span>
            <span v-if="store.modoDemo" class="chip-demo">MODO DEMO</span>
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-limpiar" title="Recargar la información desde el servidor" @click="store.cargarTodo()">
          <font-awesome-icon icon="fa-solid fa-arrows-rotate" /> Actualizar
        </button>
        <button
          class="btn-limpiar"
          title="Programas de formación con su matriz de competencias"
          @click="showCatalogo = true"
        >
          <font-awesome-icon icon="fa-solid fa-folder-open" /> Catálogo de programas
        </button>
        <button class="btn-action" title="Crear una ficha desde el catálogo de programas" @click="showNuevaFicha = true">
          <font-awesome-icon icon="fa-solid fa-plus" />
          <span>NUEVA FICHA</span>
        </button>
      </div>
    </header>

    <!-- ── INDICADORES ── -->
    <section v-if="store.indicadores && !store.errorConexion" class="indicadores-grid">
      <!-- Meta del 70% -->
      <article class="module-card ind-card">
        <p class="ind-titulo">
          <font-awesome-icon icon="fa-solid fa-chart-simple" /> META DE PROGRAMACIÓN
        </p>
        <div class="ind-principal">
          <span class="ind-numero" :class="{ alerta: bajoMetaPromedio }">
            {{ store.indicadores.promedio_programacion }}%
          </span>
          <span class="ind-contexto">promedio frente a la meta del {{ store.indicadores.meta_programacion }}%</span>
        </div>
        <div class="barra">
          <div
            class="barra-relleno"
            :class="bajoMetaPromedio ? 'barra-alerta' : 'barra-ok'"
            :style="{ width: Math.min(store.indicadores.promedio_programacion, 100) + '%' }"
          ></div>
          <span class="barra-meta" :style="{ left: store.indicadores.meta_programacion + '%' }"></span>
        </div>
        <p v-if="store.indicadores.fichas_bajo_meta.length" class="ind-detalle">
          {{ store.indicadores.fichas_bajo_meta.length }}
          {{ store.indicadores.fichas_bajo_meta.length === 1 ? 'ficha está' : 'fichas están' }} bajo la meta:
          <router-link
            v-for="f in store.indicadores.fichas_bajo_meta"
            :key="f.id"
            :to="`/admin/tituladas/${f.id}`"
            class="chip-ficha"
            :title="f.programa"
          >
            {{ f.codigo }} · {{ f.porcentaje }}%
          </router-link>
        </p>
        <p v-else class="ind-detalle ok">
          <font-awesome-icon icon="fa-solid fa-circle-check" /> Todas las fichas cumplen la meta.
        </p>
      </article>

      <!-- Alerta de técnicas < 60% -->
      <article class="module-card ind-card">
        <p class="ind-titulo">
          <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> COMPETENCIAS TÉCNICAS
        </p>
        <template v-if="store.indicadores.alertas_tecnica.length">
          <div class="ind-principal">
            <span class="ind-numero alerta">{{ store.indicadores.alertas_tecnica.length }}</span>
            <span class="ind-contexto">
              {{ store.indicadores.alertas_tecnica.length === 1 ? 'ficha con la parte técnica' : 'fichas con la parte técnica' }}
              por debajo del {{ store.indicadores.meta_tecnica }}% de lo programado
            </span>
          </div>
          <ul class="ind-lista">
            <li v-for="a in store.indicadores.alertas_tecnica" :key="a.id">
              <router-link :to="`/admin/tituladas/${a.id}`" class="chip-ficha alerta" :title="a.programa">
                {{ a.codigo }} · técnica {{ a.porcentaje_tecnica }}%
              </router-link>
              <span class="ind-lista-texto">{{ a.programa }}</span>
            </li>
          </ul>
        </template>
        <template v-else>
          <div class="ind-principal">
            <span class="ind-numero ok"><font-awesome-icon icon="fa-solid fa-circle-check" /></span>
            <span class="ind-contexto">
              La parte técnica supera el {{ store.indicadores.meta_tecnica }}% en todas las fichas programadas.
            </span>
          </div>
        </template>
      </article>

      <!-- Carga mensual por instructor -->
      <article class="module-card ind-card">
        <div class="ind-carga-header">
          <p class="ind-titulo">
            <font-awesome-icon icon="fa-solid fa-chalkboard-user" /> CARGA DE INSTRUCTORES
          </p>
          <div class="mes-nav">
            <button class="mes-flecha" aria-label="Mes anterior" @click="cambiarMesCarga(-1)">
              <font-awesome-icon icon="fa-solid fa-chevron-left" />
            </button>
            <span class="mes-actual">{{ etiquetaMesCarga }}</span>
            <button class="mes-flecha" aria-label="Mes siguiente" @click="cambiarMesCarga(1)">
              <font-awesome-icon icon="fa-solid fa-chevron-right" />
            </button>
          </div>
        </div>
        <ul class="carga-lista">
          <li v-for="c in cargaVisible" :key="c.id" class="carga-fila">
            <span class="punto-color" :style="{ background: c.color }" :title="c.iniciales"></span>
            <span class="carga-nombre" :title="`${c.nombre} (${c.tipo_vinculacion})`">{{ c.nombre }}</span>
            <div class="barra carga-barra">
              <div
                class="barra-relleno"
                :class="c.horas_mes > c.limite ? 'barra-roja' : 'barra-ok'"
                :style="{ width: Math.min(c.porcentaje, 100) + '%' }"
              ></div>
            </div>
            <span class="carga-horas" :class="{ excedida: c.horas_mes > c.limite }">
              {{ c.horas_mes }}/{{ c.limite }} h
            </span>
          </li>
        </ul>
        <p class="ind-nota">Límite mensual de formación directa: 160 h contratista · 128 h planta.</p>
      </article>
    </section>

    <!-- Filtros -->
    <div class="module-card filtros-card">
      <div class="filters-group">
        <div class="search-box">
          <font-awesome-icon icon="fa-solid fa-magnifying-glass" class="search-icon" />
          <input
            v-model="busqueda"
            type="text"
            class="form-input search-input"
            placeholder="Buscar por código, programa o instructor titular..."
          />
        </div>
        <select v-model="filtroJornada" class="form-input select-filter">
          <option value="">Todas las jornadas</option>
          <option v-for="j in JORNADAS_TITULADAS" :key="j.valor" :value="j.valor">
            {{ j.valor }} ({{ j.horario }})
          </option>
        </select>
        <select v-model="filtroSede" class="form-input select-filter">
          <option value="">Todas las sedes</option>
          <option v-for="s in store.sedes" :key="s" :value="s">{{ s }}</option>
        </select>
        <button v-if="hayFiltros" class="btn-limpiar" @click="limpiarFiltros">
          <font-awesome-icon icon="fa-solid fa-xmark" /> Limpiar
        </button>
      </div>
    </div>

    <!-- Estado de error de conexión -->
    <div v-if="store.errorConexion" class="module-card estado-panel estado-error">
      <font-awesome-icon icon="fa-solid fa-triangle-exclamation" class="estado-icono" />
      <div>
        <strong>No se pudieron cargar las fichas tituladas.</strong>
        <p>{{ store.errorConexion }}</p>
      </div>
      <button class="btn-action" @click="store.cargarTodo()">
        <font-awesome-icon icon="fa-solid fa-arrows-rotate" /> Reintentar
      </button>
    </div>

    <!-- Estado de carga -->
    <div v-else-if="store.cargando && store.fichas.length === 0" class="module-card estado-panel">
      <font-awesome-icon :icon="['fas', 'circle-notch']" spin class="estado-icono" />
      <p>Cargando la programación de las fichas tituladas...</p>
    </div>

    <!-- Estado vacío global -->
    <div v-else-if="store.fichas.length === 0" class="module-card estado-panel">
      <font-awesome-icon icon="fa-solid fa-graduation-cap" class="estado-icono" />
      <div>
        <strong>Aún no hay fichas tituladas registradas.</strong>
        <p>Cuando existan fichas en el sistema aparecerán aquí con su porcentaje de programación.</p>
      </div>
    </div>

    <!-- ── DIRECTORIO DE FICHAS ── -->
    <main v-else class="module-card tabla-card">
      <div class="tabla-toolbar">
        <h2 class="module-title">
          <font-awesome-icon icon="fa-solid fa-clipboard-list" /> DIRECTORIO DE FICHAS TITULADAS
        </h2>
        <span class="tabla-conteo">
          {{ fichasFiltradas.length }} de {{ store.fichas.length }} fichas
        </span>
      </div>

      <p v-if="fichasFiltradas.length === 0" class="tabla-vacia">
        Ninguna ficha coincide con los filtros aplicados.
      </p>

      <div v-else class="tabla-scroll">
        <table class="tabla-fichas">
          <thead>
            <tr>
              <th>CÓDIGO</th>
              <th>PROGRAMA DE FORMACIÓN</th>
              <th>INSTRUCTOR TITULAR</th>
              <th class="text-center">JORNADA</th>
              <th>SEDE</th>
              <th class="col-progreso">PROGRAMACIÓN</th>
              <th class="text-center">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="f in fichasFiltradas"
              :key="f.id"
              class="fila-ficha"
              :title="`Abrir el diagnóstico y el calendario de la ficha ${f.codigo}`"
              @click="abrirFicha(f)"
            >
              <td><strong class="col-codigo">{{ f.codigo }}</strong></td>
              <td>
                <div class="programa-info">
                  <span class="programa-nombre">{{ f.programa }}</span>
                  <span class="programa-nivel">{{ f.nivel }} · {{ f.numero_aprendices }} aprendices</span>
                </div>
              </td>
              <td>
                <span v-if="f.instructor_titular" class="titular">
                  <span class="punto-color" :style="{ background: f.instructor_titular.color }"></span>
                  {{ f.instructor_titular.nombre }}
                </span>
                <span v-else class="titular sin-titular">Sin titular asignado</span>
              </td>
              <td class="text-center">
                <span class="badge-jornada" :class="`jornada-${f.jornada.toLowerCase()}`">
                  {{ f.jornada }}
                  <small>{{ horarioJornada(f.jornada) }}</small>
                </span>
              </td>
              <td><span class="celda-sede">{{ f.sede }}</span></td>
              <td class="col-progreso">
                <span
                  v-if="!f.tiene_diagnostico"
                  class="chip-sin-diagnostico"
                  title="Registre la matriz de competencias en el detalle de la ficha para poder programarla"
                >
                  <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> Sin diagnóstico
                </span>
                <div v-else class="progreso-celda">
                  <div class="barra">
                    <div
                      class="barra-relleno"
                      :class="f.porcentaje_programacion >= META_PROGRAMACION ? 'barra-ok' : 'barra-alerta'"
                      :style="{ width: Math.min(f.porcentaje_programacion, 100) + '%' }"
                    ></div>
                    <span class="barra-meta" :style="{ left: META_PROGRAMACION + '%' }"></span>
                  </div>
                  <span class="progreso-texto">
                    {{ f.porcentaje_programacion }}%
                    <small>({{ f.horas_programadas }}/{{ f.total_horas_programa }} h)</small>
                  </span>
                  <font-awesome-icon
                    v-if="f.alerta_tecnica"
                    icon="fa-solid fa-triangle-exclamation"
                    class="icono-alerta"
                    :title="`La parte técnica es solo el ${f.porcentaje_tecnica}% de lo programado (mínimo ${META_TECNICA}%)`"
                  />
                </div>
              </td>
              <td class="text-center">
                <button
                  class="btn-tabla"
                  title="Ver diagnóstico y calendario"
                  @click.stop="abrirFicha(f)"
                >
                  <font-awesome-icon icon="fa-solid fa-eye" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- Alta de fichas (desde el catálogo) y catálogo de programas -->
    <ModalNuevaFicha
      :show="showNuevaFicha"
      @update:show="showNuevaFicha = $event"
      @close="showNuevaFicha = false"
      @creada="abrirFicha"
    />
    <ModalCatalogoProgramas
      :show="showCatalogo"
      @update:show="showCatalogo = $event"
      @close="showCatalogo = false"
    />
  </div>
</template>

<script setup>
// Listado de Fichas Tituladas: reemplaza la vista general de la matriz de Excel
// de programación (una fila por ficha, con su avance frente a la meta del 70 %).
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import ModalNuevaFicha from '@/components/admin/modals/ModalNuevaFicha.vue';
import ModalCatalogoProgramas from '@/components/admin/modals/ModalCatalogoProgramas.vue';
import { tituladasService } from '@/services/tituladasService';
import {
  useTituladasStore,
  JORNADAS_TITULADAS,
  META_PROGRAMACION,
  META_TECNICA,
  horarioJornada,
} from '@/stores/tituladas';

const store = useTituladasStore();
const router = useRouter();
const toast = useToast();

const NOMBRES_MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

// ── Modales de alta de ficha y catálogo de programas ──
const showNuevaFicha = ref(false);
const showCatalogo = ref(false);

// ── Filtros (en memoria: el listado ya está cargado en el store) ──
const busqueda = ref('');
const filtroJornada = ref('');
const filtroSede = ref('');

const hayFiltros = computed(() => busqueda.value || filtroJornada.value || filtroSede.value);

const limpiarFiltros = () => {
  busqueda.value = '';
  filtroJornada.value = '';
  filtroSede.value = '';
};

const fichasFiltradas = computed(() => {
  let fichas = store.fichas;
  if (filtroJornada.value) fichas = fichas.filter((f) => f.jornada === filtroJornada.value);
  if (filtroSede.value) fichas = fichas.filter((f) => f.sede === filtroSede.value);
  if (busqueda.value) {
    const q = busqueda.value.toLowerCase();
    fichas = fichas.filter(
      (f) =>
        f.codigo.toLowerCase().includes(q) ||
        f.programa.toLowerCase().includes(q) ||
        (f.instructor_titular?.nombre || '').toLowerCase().includes(q)
    );
  }
  return fichas;
});

// ── Carga de instructores con navegación de mes (consulta directa a la API) ──
const cargaMes = ref(null); // null = usar los indicadores del store (mes actual)

const mesCargaActivo = computed(() => cargaMes.value?.mes || store.indicadores?.mes || '');
const cargaVisible = computed(
  () => (cargaMes.value || store.indicadores)?.carga_instructores || []
);

const etiquetaMesCarga = computed(() => {
  if (!mesCargaActivo.value) return '';
  const [anio, mes] = mesCargaActivo.value.split('-').map(Number);
  return `${NOMBRES_MESES[mes - 1]} ${anio}`;
});

const cambiarMesCarga = async (delta) => {
  if (!mesCargaActivo.value) return;
  const [anio, mes] = mesCargaActivo.value.split('-').map(Number);
  const fecha = new Date(anio, mes - 1 + delta, 1);
  const objetivo = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
  try {
    cargaMes.value = await tituladasService.getIndicadores(objetivo);
  } catch (e) {
    toast.error(e.message);
  }
};

// Si el store se recarga (tras programar), volver al mes que muestra el store
watch(() => store.indicadores, () => { cargaMes.value = null; });

const abrirFicha = (ficha) => router.push(`/admin/tituladas/${ficha.id}`);

onMounted(() => store.initStore());
</script>

<style scoped>
/* ==========================================================================
   ESTILO ESTRUCTURAL E INSTITUCIONAL (SENA) — mismo shell del panel admin
   ========================================================================== */
.admin-view-shell {
  font-family: var(--fuente-principal);
  min-height: 100vh;
  color: var(--texto-principal);
  box-sizing: border-box;
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
  color: var(--sena-azul-oscuro);
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

.chip-demo {
  background: rgba(253, 195, 0, 0.18);
  color: #8a6d00;
  border: 1px solid rgba(253, 195, 0, 0.5);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

[data-theme="dark"] .chip-demo { color: var(--sena-amarillo); }

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

/* ── Indicadores ── */
.indicadores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  align-items: stretch;
}

.ind-card {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.ind-titulo {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
}

.ind-titulo svg { color: var(--sena-verde); }

.ind-principal {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.ind-numero {
  font-size: 2rem;
  font-weight: 800;
  color: var(--sena-verde);
  line-height: 1;
}

.ind-numero.alerta { color: #e67e22; }
.ind-numero.ok { color: var(--sena-verde); font-size: 1.6rem; }

.ind-contexto {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  max-width: 220px;
}

.ind-detalle {
  margin: 0;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.ind-detalle.ok { color: var(--sena-verde); font-weight: 700; }

.ind-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ind-lista li {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.ind-lista-texto {
  font-size: 0.72rem;
  color: var(--texto-secundario);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-ficha {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--texto-principal);
  text-decoration: none;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.chip-ficha:hover { border-color: var(--sena-verde); color: var(--sena-verde); }
.chip-ficha.alerta { border-color: rgba(230, 126, 34, 0.5); color: #e67e22; }

/* Barra de progreso con marca de meta */
.barra {
  position: relative;
  height: 8px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  overflow: hidden;
  flex: 1;
}

.barra-relleno {
  height: 100%;
  border-radius: 6px;
  transition: width 0.4s ease;
}

.barra-ok { background: var(--sena-verde); }
.barra-alerta { background: #e67e22; }
.barra-roja { background: #e53e3e; }

.barra-meta {
  position: absolute;
  top: -2px;
  bottom: -2px;
  width: 2px;
  background: var(--sena-azul-oscuro);
  opacity: 0.55;
}

/* Carga por instructor */
.ind-carga-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mes-nav {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mes-flecha {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  width: 26px;
  height: 26px;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  transition: all 0.2s ease;
}

.mes-flecha:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.mes-actual {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-principal);
  min-width: 110px;
  text-align: center;
}

.carga-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.carga-fila {
  display: flex;
  align-items: center;
  gap: 8px;
}

.punto-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.carga-nombre {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-principal);
  width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.carga-barra { max-width: none; }

.carga-horas {
  font-size: 0.7rem;
  font-family: monospace;
  color: var(--texto-secundario);
  min-width: 68px;
  text-align: right;
}

.carga-horas.excedida { color: #e53e3e; font-weight: 800; }

.ind-nota {
  margin: 0;
  font-size: 0.68rem;
  color: var(--texto-secundario);
  font-style: italic;
}

/* ── Filtros ── */
.filtros-card {
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}

.filters-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  position: relative;
  min-width: 260px;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--texto-secundario);
  font-size: 0.9rem;
}

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.65rem 1rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input {
  width: 100%;
  padding-left: 2.2rem;
  box-sizing: border-box;
}

.select-filter {
  min-width: 170px;
  cursor: pointer;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.btn-limpiar {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-limpiar:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.btn-action {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-action:hover {
  background: var(--sena-verde-oscuro);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(57, 169, 0, 0.3);
}

/* ── Estados ── */
.estado-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  padding: 2.5rem 2rem;
  text-align: center;
  flex-wrap: wrap;
  color: var(--texto-secundario);
}

.estado-panel strong {
  color: var(--texto-principal);
  display: block;
  margin-bottom: 4px;
}

.estado-panel p { margin: 0; font-size: 0.85rem; }
.estado-icono { font-size: 1.8rem; color: var(--sena-verde); }
.estado-error .estado-icono { color: var(--sena-amarillo); }

/* ── Directorio (tabla) ── */
.tabla-card { padding: 1.25rem 1.5rem; }

.tabla-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.module-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-title svg { color: var(--sena-verde); }

.tabla-conteo {
  font-size: 0.72rem;
  color: var(--texto-secundario);
  font-weight: 700;
}

.tabla-vacia {
  margin: 0;
  padding: 1.75rem 0.5rem;
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.82rem;
  font-style: italic;
  border: 1px dashed var(--borde);
  border-radius: 12px;
}

.tabla-scroll { overflow-x: auto; }

.tabla-fichas {
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
}

.tabla-fichas th {
  text-align: left;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid var(--borde);
  white-space: nowrap;
}

.tabla-fichas td {
  padding: 0.8rem 0.75rem;
  border-bottom: 1px solid var(--fondo-app);
  vertical-align: middle;
  font-size: 0.82rem;
}

.text-center { text-align: center; }

.fila-ficha { cursor: pointer; transition: background 0.15s ease; }
.fila-ficha:hover { background: rgba(57, 169, 0, 0.05); }

.col-codigo {
  font-family: monospace;
  font-size: 0.9rem;
  color: var(--sena-azul-oscuro);
}

[data-theme="dark"] .col-codigo { color: var(--texto-principal); }

.programa-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 200px;
}

.programa-nombre { font-weight: 700; color: var(--texto-principal); }
.programa-nivel { font-size: 0.7rem; color: var(--texto-secundario); }

.titular {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  white-space: nowrap;
}

.sin-titular { color: var(--texto-secundario); font-style: italic; font-weight: 400; }

.badge-jornada {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.2;
}

.badge-jornada small { font-size: 0.62rem; font-weight: 600; opacity: 0.8; }

.jornada-mañana { background: rgba(253, 195, 0, 0.15); color: #8a6d00; }
.jornada-tarde { background: rgba(230, 126, 34, 0.15); color: #b35c0e; }
.jornada-noche { background: rgba(41, 128, 185, 0.15); color: #1f618d; }

[data-theme="dark"] .jornada-mañana { color: #fdc300; }
[data-theme="dark"] .jornada-tarde { color: #e67e22; }
[data-theme="dark"] .jornada-noche { color: #5dade2; }

.celda-sede { font-size: 0.78rem; color: var(--texto-secundario); white-space: nowrap; }

.col-progreso { min-width: 190px; }

.progreso-celda {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progreso-texto {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--texto-principal);
  white-space: nowrap;
}

.progreso-texto small { font-weight: 600; color: var(--texto-secundario); }

.icono-alerta { color: #e67e22; font-size: 0.9rem; }

.chip-sin-diagnostico {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(230, 126, 34, 0.12);
  border: 1px solid rgba(230, 126, 34, 0.45);
  color: #b35c0e;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 800;
  white-space: nowrap;
}

[data-theme="dark"] .chip-sin-diagnostico { color: #f0a35e; }

.btn-tabla {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  width: 34px;
  height: 34px;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-tabla:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

/* ── Responsive ── */
@media (max-width: 992px) {
  .dash-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .header-actions { justify-content: center; }
  .carga-nombre { width: 96px; }
}
</style>
