<template>
  <main class="carpetas-vista">
    <!-- Nivel 1: el archivo mensual (carpetas por período) -->
    <template v-if="!mesSeleccionado">
      <!-- Barra del archivo -->
      <div class="module-card archivo-toolbar">
        <div class="archivo-titulos">
          <p class="archivo-eyebrow">
            <font-awesome-icon icon="fa-solid fa-folder-open" /> Archivo por mes
          </p>
          <p class="archivo-hint">
            Cada solicitud se archiva automáticamente en la carpeta del mes en que fue solicitada.
          </p>
        </div>
        <button
          class="btn-nueva-carpeta"
          :class="{ abierto: showCreadorCarpeta }"
          :title="showCreadorCarpeta ? 'Cerrar el selector de período' : 'Crear la carpeta de un mes y año'"
          @click="alternarCreadorCarpeta"
        >
          <font-awesome-icon :icon="showCreadorCarpeta ? 'fa-solid fa-xmark' : 'fa-solid fa-plus'" />
          {{ showCreadorCarpeta ? 'Cancelar' : 'Nueva carpeta' }}
        </button>
      </div>

      <!-- Selector de período (mes + año) -->
      <Transition name="creador">
        <div
          v-if="showCreadorCarpeta"
          class="module-card creador-carpeta"
          role="group"
          aria-label="Crear la carpeta de un período"
        >
          <div class="creador-anio">
            <button
              class="anio-flecha"
              :disabled="anioCreador <= ANIO_MINIMO"
              aria-label="Año anterior"
              @click="anioCreador--"
            >
              <font-awesome-icon icon="fa-solid fa-chevron-left" />
            </button>
            <span class="anio-actual">{{ anioCreador }}</span>
            <button
              class="anio-flecha"
              :disabled="anioCreador >= ANIO_MAXIMO"
              aria-label="Año siguiente"
              @click="anioCreador++"
            >
              <font-awesome-icon icon="fa-solid fa-chevron-right" />
            </button>
          </div>
          <div class="creador-meses">
            <button
              v-for="(nombre, i) in NOMBRES_MESES"
              :key="nombre"
              type="button"
              class="mes-opcion"
              :class="{
                existente: carpetaExiste(claveDe(anioCreador, i)),
                actual: claveDe(anioCreador, i) === claveMesActual,
              }"
              :title="carpetaExiste(claveDe(anioCreador, i))
                ? `${nombre} ${anioCreador} ya tiene carpeta; clic para abrirla`
                : `Crear la carpeta de ${nombre} ${anioCreador}`"
              @click="crearCarpeta(i)"
            >
              {{ nombre.slice(0, 3) }}
              <span
                v-if="carpetaExiste(claveDe(anioCreador, i))"
                class="mes-marca"
                aria-hidden="true"
              >
                <font-awesome-icon icon="fa-solid fa-folder" />
              </span>
            </button>
          </div>
          <p class="creador-nota">
            Los meses con <font-awesome-icon icon="fa-solid fa-folder" /> ya tienen carpeta;
            selecciónelos para abrirla directamente.
          </p>
        </div>
      </Transition>

      <!-- Carpetas agrupadas por año -->
      <template v-if="carpetasPorAnio.length">
        <section v-for="grupo in carpetasPorAnio" :key="grupo.anio" class="archivo-anio">
          <h2 class="anio-etiqueta">{{ grupo.anio }}</h2>
          <div class="carpetas-grid">
            <div
              v-for="carpeta in grupo.carpetas"
              :key="carpeta.clave"
              class="carpeta"
              :class="{ vacia: carpeta.items.length === 0 }"
              role="button"
              tabindex="0"
              :title="`Abrir las solicitudes de ${carpeta.etiqueta}`"
              @click="abrirCarpeta(carpeta.clave)"
              @keydown.enter="abrirCarpeta(carpeta.clave)"
            >
              <span v-if="carpeta.clave === claveMesActual" class="chip-mes-actual">Mes actual</span>
              <button
                v-if="carpeta.items.length === 0 && esManual(carpeta.clave)"
                class="carpeta-borrar"
                title="Eliminar esta carpeta vacía"
                :aria-label="`Eliminar la carpeta vacía de ${carpeta.etiqueta}`"
                @click.stop="eliminarCarpeta(carpeta.clave)"
              >
                <font-awesome-icon icon="fa-solid fa-trash-can" />
              </button>
              <font-awesome-icon icon="fa-solid fa-folder" class="carpeta-icono" />
              <span class="carpeta-nombre">{{ carpeta.mes }}</span>
              <span class="carpeta-conteo">
                {{ carpeta.items.length }} {{ carpeta.items.length === 1 ? 'solicitud' : 'solicitudes' }}
              </span>
            </div>
          </div>
        </section>
      </template>
      <div v-else class="module-card estado-panel">
        <font-awesome-icon icon="fa-solid fa-folder-open" class="estado-icono" />
        <div>
          <strong>El archivo está vacío.</strong>
          <p>No hay solicitudes con los filtros aplicados. Cree una carpeta para preparar un período.</p>
        </div>
        <button class="btn-nueva-carpeta" @click="showCreadorCarpeta = true">
          <font-awesome-icon icon="fa-solid fa-plus" /> Nueva carpeta
        </button>
      </div>
    </template>

    <!-- Nivel 2: contenido de la carpeta abierta -->
    <template v-else>
      <div class="carpeta-abierta-header">
        <button class="btn-volver" @click="mesSeleccionado = null">
          <font-awesome-icon icon="fa-solid fa-arrow-left" /> Todos los meses
        </button>
        <h2 class="carpeta-titulo">
          <font-awesome-icon icon="fa-solid fa-folder-open" />
          {{ etiquetaMes(mesSeleccionado) }}
          <span class="columna-contador">{{ solicitudesDelMes.length }}</span>
        </h2>
      </div>

      <div v-if="solicitudesDelMes.length === 0" class="module-card estado-panel">
        <font-awesome-icon icon="fa-solid fa-folder-open" class="estado-icono" />
        <div>
          <strong>Esta carpeta aún está vacía.</strong>
          <p>
            Las solicitudes registradas en {{ etiquetaMes(mesSeleccionado) }} se archivarán aquí
            automáticamente.
          </p>
        </div>
      </div>

      <div v-else class="carpeta-contenido">
        <TarjetaComplementaria
          v-for="s in solicitudesDelMes"
          :key="s.id"
          :solicitud="s"
          mostrar-estado
          @abrir="abrirDetalle"
        />
      </div>
    </template>
  </main>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { useComplementariasStore } from '@/stores/complementarias';
import TarjetaComplementaria from '@/components/admin/TarjetaComplementaria.vue';

const toast = useToast();
const store = useComplementariasStore();
const emit = defineEmits(['abrir-detalle']);

const abrirDetalle = (solicitud) => {
  emit('abrir-detalle', solicitud);
};

// ── Archivo por mes (respaldo ordenado, tipo carpetas de OneDrive) ──
const mesSeleccionado = ref(null);

const NOMBRES_MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

const etiquetaMes = (clave) => {
  if (clave === 'sin-fecha') return 'Sin fecha de solicitud';
  const [anio, mes] = clave.split('-');
  return `${NOMBRES_MESES[Number(mes) - 1]} ${anio}`;
};

const nombreMes = (clave) =>
  clave === 'sin-fecha' ? 'Sin fecha' : NOMBRES_MESES[Number(clave.slice(5, 7)) - 1];

const CLAVE_ALMACEN_CARPETAS = 'voltmind_carpetas_complementarias';

const cargarCarpetasManuales = () => {
  try {
    const lista = JSON.parse(localStorage.getItem(CLAVE_ALMACEN_CARPETAS) || '[]');
    return Array.isArray(lista) ? lista.filter((c) => /^\d{4}-\d{2}$/.test(c)) : [];
  } catch {
    return [];
  }
};

const carpetasManuales = ref(cargarCarpetasManuales());

watch(carpetasManuales, (lista) => {
  localStorage.setItem(CLAVE_ALMACEN_CARPETAS, JSON.stringify(lista));
});

const hoy = new Date();
const claveMesActual = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`;
const ANIO_MINIMO = 2020;
const ANIO_MAXIMO = hoy.getFullYear() + 2;

const showCreadorCarpeta = ref(false);
const anioCreador = ref(hoy.getFullYear());

const alternarCreadorCarpeta = () => {
  showCreadorCarpeta.value = !showCreadorCarpeta.value;
  if (showCreadorCarpeta.value) anioCreador.value = hoy.getFullYear();
};

const claveDe = (anio, mesIndice) => `${anio}-${String(mesIndice + 1).padStart(2, '0')}`;
const carpetaExiste = (clave) => carpetasMeses.value.some((c) => c.clave === clave);
const esManual = (clave) => carpetasManuales.value.includes(clave);

const abrirCarpeta = (clave) => {
  showCreadorCarpeta.value = false;
  mesSeleccionado.value = clave;
};

const crearCarpeta = (mesIndice) => {
  const clave = claveDe(anioCreador.value, mesIndice);
  if (carpetaExiste(clave)) {
    abrirCarpeta(clave);
    toast.info(`La carpeta de ${etiquetaMes(clave)} ya existía; se abrió su contenido.`);
    return;
  }
  carpetasManuales.value = [...carpetasManuales.value, clave];
  abrirCarpeta(clave);
  toast.success(`Carpeta de ${etiquetaMes(clave)} creada.`);
};

const eliminarCarpeta = (clave) => {
  carpetasManuales.value = carpetasManuales.value.filter((c) => c !== clave);
  toast.success(`Carpeta de ${etiquetaMes(clave)} eliminada.`);
};

const carpetasMeses = computed(() => {
  const grupos = new Map();
  for (const clave of carpetasManuales.value) grupos.set(clave, []);
  for (const s of store.filtradas) {
    const clave = (s.fecha_creacion || '').slice(0, 7) || 'sin-fecha';
    if (!grupos.has(clave)) grupos.set(clave, []);
    grupos.get(clave).push(s);
  }
  return [...grupos.entries()]
    .sort(([a], [b]) => (a === 'sin-fecha' ? 1 : b === 'sin-fecha' ? -1 : b.localeCompare(a)))
    .map(([clave, items]) => ({ clave, etiqueta: etiquetaMes(clave), mes: nombreMes(clave), items }));
});

const carpetasPorAnio = computed(() => {
  const grupos = [];
  for (const carpeta of carpetasMeses.value) {
    const anio = carpeta.clave === 'sin-fecha' ? 'Sin fecha' : carpeta.clave.slice(0, 4);
    const ultimo = grupos[grupos.length - 1];
    if (ultimo && ultimo.anio === anio) ultimo.carpetas.push(carpeta);
    else grupos.push({ anio, carpetas: [carpeta] });
  }
  return grupos;
});

const solicitudesDelMes = computed(() => {
  const carpeta = carpetasMeses.value.find((c) => c.clave === mesSeleccionado.value);
  return carpeta ? carpeta.items : [];
});
</script>

<style scoped>
.carpetas-vista {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px var(--sombra-suave);
}

.carpetas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.carpeta {
  position: relative;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 16px;
  padding: 1.5rem 1rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  box-shadow: 0 4px 12px var(--sombra-suave);
  transition: all 0.2s ease;
}

.carpeta:hover,
.carpeta:focus-visible {
  border-color: var(--sena-verde);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(57, 169, 0, 0.15);
  outline: none;
}

.carpeta-icono {
  font-size: 2.4rem;
  color: #fdc300;
}

.carpeta-nombre {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

.carpeta-conteo {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.carpeta.vacia {
  border-style: dashed;
  box-shadow: none;
}

.carpeta.vacia .carpeta-icono {
  opacity: 0.45;
}

.chip-mes-actual {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(57, 169, 0, 0.14);
  color: var(--sena-verde-oscuro);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 99px;
}

[data-theme="dark"] .chip-mes-actual {
  color: var(--sena-verde);
}

.carpeta-borrar {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--texto-secundario);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.carpeta:hover .carpeta-borrar,
.carpeta-borrar:focus-visible {
  opacity: 1;
}

.carpeta-borrar:hover {
  background: rgba(229, 62, 62, 0.12);
  color: #e53e3e;
}

/* ── Barra del archivo mensual ── */
.archivo-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.5rem;
  border-left: 4px solid #fdc300;
}

.archivo-eyebrow {
  margin: 0;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.archivo-eyebrow svg {
  color: #fdc300;
}

.archivo-hint {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
}

.btn-nueva-carpeta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  border: 1.5px dashed var(--sena-verde);
  background: transparent;
  color: var(--sena-verde-oscuro);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-nueva-carpeta:hover,
.btn-nueva-carpeta:focus-visible {
  background: rgba(57, 169, 0, 0.08);
  border-style: solid;
  outline: none;
}

.btn-nueva-carpeta.abierto {
  border-style: solid;
  color: var(--texto-secundario);
  border-color: var(--borde);
}

[data-theme="dark"] .btn-nueva-carpeta {
  color: var(--sena-verde);
}

/* ── Selector de período (mes + año) ── */
.creador-carpeta {
  padding: 1.2rem 1.5rem;
}

.creador-anio {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.2rem;
  margin-bottom: 1rem;
}

.anio-actual {
  min-width: 64px;
  text-align: center;
  font-size: 1.15rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: var(--texto-principal);
}

.anio-flecha {
  width: 34px;
  height: 34px;
  border: 1px solid var(--borde);
  border-radius: 10px;
  background: var(--fondo-app);
  color: var(--texto-principal);
  cursor: pointer;
  transition: all 0.2s ease;
}

.anio-flecha:hover:not(:disabled) {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.anio-flecha:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.creador-meses {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}

.mes-opcion {
  position: relative;
  padding: 0.65rem 0.25rem;
  border: 1px solid var(--borde);
  border-radius: 10px;
  background: var(--fondo-app);
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mes-opcion:hover,
.mes-opcion:focus-visible {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  background: rgba(57, 169, 0, 0.06);
  outline: none;
}

.mes-opcion.actual {
  border-color: var(--sena-verde);
  box-shadow: inset 0 0 0 1px var(--sena-verde);
}

.mes-opcion.existente {
  background: rgba(253, 195, 0, 0.12);
  border-color: rgba(253, 195, 0, 0.55);
}

.mes-marca {
  position: absolute;
  top: 3px;
  right: 6px;
  font-size: 0.58rem;
  color: #fdc300;
}

.creador-nota {
  margin: 0.9rem 0 0;
  font-size: 0.75rem;
  color: var(--texto-secundario);
  text-align: center;
}

.creador-nota svg {
  color: #fdc300;
}

.creador-enter-active,
.creador-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.creador-enter-from,
.creador-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Carpetas agrupadas por año ── */
.archivo-anio {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.anio-etiqueta {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 10px;
}

.anio-etiqueta::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--borde);
}

@media (prefers-reduced-motion: reduce) {
  .creador-enter-active,
  .creador-leave-active {
    transition: none;
  }
  .carpeta:hover,
  .carpeta:focus-visible {
    transform: none;
  }
}

.carpeta-abierta-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-volver {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-volver:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
}

.carpeta-titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.carpeta-titulo svg {
  color: #fdc300;
}

.carpeta-contenido {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

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

.estado-panel p {
  margin: 0;
  font-size: 0.85rem;
}

.estado-icono {
  font-size: 1.8rem;
  color: var(--sena-verde);
}

/* ── Responsive ── */
@media (max-width: 992px) {
  .creador-meses {
    grid-template-columns: repeat(4, 1fr);
  }
  .archivo-toolbar {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  .archivo-eyebrow {
    justify-content: center;
  }
  .btn-nueva-carpeta {
    justify-content: center;
  }
}
</style>
