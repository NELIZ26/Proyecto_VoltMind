<template>
  <BaseModal
    :show="show"
    :title="solicitud ? solicitud.nombre_programa : 'Detalle de la solicitud'"
    class="modal-detalle-comp"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <div v-if="solicitud" class="detalle-body">
      <!-- Estado + código de programa -->
      <div class="detalle-encabezado">
        <div class="codigo-version">
          <span class="chip-codigo">
            <font-awesome-icon icon="fa-solid fa-hashtag" />
            Programa {{ solicitud.codigo_programa }} · v{{ solicitud.version_programa || '1' }}
          </span>
          <span class="chip-duracion">
            <font-awesome-icon icon="fa-solid fa-clock" />
            {{ solicitud.duracion_horas }} horas
          </span>
        </div>
        <label class="selector-estado">
          <span class="etiqueta-mini">Estado</span>
          <select
            class="form-select"
            :class="claseEstado(solicitud.estado)"
            :value="solicitud.estado"
            @change="$emit('actualizar', solicitud.id, { estado: $event.target.value })"
          >
            <option v-for="e in ESTADOS_TABLERO" :key="e" :value="e">{{ e }}</option>
          </select>
        </label>
      </div>

      <!-- Gestión rápida: completar los códigos faltantes y publicar en un solo paso -->
      <section v-if="solicitud.estado === 'Pendiente'" class="seccion gestion-rapida">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-bolt" /> GESTIÓN RÁPIDA
        </h4>
        <p class="gestion-texto">
          Complete los códigos y publique la ficha: el instructor recibirá el aviso
          automáticamente por correo institucional y por la campana de la plataforma.
        </p>
        <div class="gestion-campos">
          <label class="gestion-campo">
            <span class="etiqueta-mini">Código de empresa</span>
            <input
              v-model.trim="codigoEmpresaRapido"
              class="gestion-input"
              type="text"
              placeholder="Ej: 9001234"
            />
          </label>
          <label class="gestion-campo">
            <span class="etiqueta-mini">Código de ficha</span>
            <input
              v-model.trim="codigoFichaRapido"
              class="gestion-input"
              type="text"
              placeholder="Ej: 3120045"
            />
          </label>
          <button
            class="btn-publicar"
            :disabled="!codigoEmpresaRapido || !codigoFichaRapido"
            :title="!codigoEmpresaRapido || !codigoFichaRapido
              ? 'Complete el código de empresa y el código de ficha para publicar'
              : 'Publicar la ficha y avisar al instructor automáticamente'"
            @click="publicarRapido"
          >
            <font-awesome-icon icon="fa-solid fa-paper-plane" /> Publicar ficha
          </button>
        </div>
      </section>

      <!-- Aviso de publicación al instructor (correo + campana) -->
      <section v-if="solicitud.estado === 'Publicada'" class="seccion">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-envelope" /> AVISO AL INSTRUCTOR
        </h4>
        <div class="aviso-fila">
          <p class="aviso-estado" :class="solicitud.notificado ? 'ok' : 'pendiente-aviso'">
            <font-awesome-icon
              :icon="solicitud.notificado ? 'fa-solid fa-circle-check' : 'fa-solid fa-triangle-exclamation'"
            />
            <template v-if="solicitud.notificado">
              Avisado el {{ formatearAviso(solicitud.notificado) }} (correo + campana).
            </template>
            <template v-else>
              Pendiente de avisar: el instructor aún no recibe el aviso de publicación.
            </template>
          </p>
          <button
            class="btn-reenviar"
            :disabled="enviandoAviso"
            :title="'Enviar el aviso de publicación a ' + (solicitud.correo_instructor || 'sin correo')"
            @click="$emit('reenviar-aviso', solicitud)"
          >
            <font-awesome-icon
              :icon="enviandoAviso ? ['fas', 'circle-notch'] : 'fa-solid fa-paper-plane'"
              :spin="enviandoAviso"
            />
            {{ enviandoAviso ? 'Enviando...' : solicitud.notificado ? 'Reenviar aviso' : 'Enviar aviso' }}
          </button>
        </div>
      </section>

      <!-- Checklist de seguimiento como pasos -->
      <section class="seccion">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-list-check" /> SEGUIMIENTO
        </h4>
        <ol class="stepper">
          <li
            v-for="(paso, indice) in PASOS_SEGUIMIENTO"
            :key="paso.campo"
            class="paso"
            :class="{ completado: solicitud[paso.campo] }"
          >
            <button
              type="button"
              class="paso-marcador"
              :title="solicitud[paso.campo] ? 'Marcar como pendiente' : 'Marcar como completado'"
              @click="$emit('actualizar', solicitud.id, { [paso.campo]: !solicitud[paso.campo] })"
            >
              <font-awesome-icon v-if="solicitud[paso.campo]" icon="fa-solid fa-check" />
              <span v-else>{{ indice + 1 }}</span>
            </button>
            <span class="paso-etiqueta">{{ paso.etiqueta }}</span>
          </li>
        </ol>
      </section>

      <div class="grilla-secciones">
        <!-- Solicitante -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-user-tie" /> SOLICITANTE
          </h4>
          <dl class="lista-datos">
            <div class="dato">
              <dt>Instructor</dt>
              <dd>
                <router-link to="/admin/instructores" class="enlace-interno" title="Ver en el directorio de instructores">
                  {{ solicitud.nombre_instructor }}
                  <font-awesome-icon icon="fa-solid fa-arrow-up-right-from-square" />
                </router-link>
              </dd>
            </div>
            <div class="dato">
              <dt>Correo institucional</dt>
              <dd>{{ solicitud.correo_instructor || '—' }}</dd>
            </div>
            <div class="dato">
              <dt>Celular</dt>
              <dd>{{ solicitud.celular_instructor || '—' }}</dd>
            </div>
          </dl>
        </section>

        <!-- Logística -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-location-dot" /> LOGÍSTICA
          </h4>
          <dl class="lista-datos">
            <div class="dato">
              <dt>Jornada</dt>
              <dd>{{ solicitud.jornada || '—' }}</dd>
            </div>
            <div class="dato">
              <dt>Municipio</dt>
              <dd>{{ solicitud.municipio || '—' }}</dd>
            </div>
            <div class="dato">
              <dt>Lugar de ejecución</dt>
              <dd>{{ solicitud.lugar_ejecucion || '—' }}</dd>
            </div>
          </dl>
        </section>

        <!-- Fechas -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-calendar-days" /> FECHAS
          </h4>
          <dl class="lista-datos">
            <div class="dato">
              <dt>Inscripciones</dt>
              <dd class="fecha-rango">{{ rango(solicitud.fecha_inicio_inscripcion, solicitud.fecha_cierre_inscripcion) }}</dd>
            </div>
            <div class="dato">
              <dt>Formación</dt>
              <dd class="fecha-rango">{{ rango(solicitud.fecha_inicio_formacion, solicitud.fecha_fin_formacion) }}</dd>
            </div>
            <div class="dato">
              <dt>Solicitud creada</dt>
              <dd class="fecha-rango">{{ solicitud.fecha_creacion || '—' }}</dd>
            </div>
          </dl>
        </section>

        <!-- Códigos e inscritos -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-clipboard-list" /> REGISTRO
          </h4>
          <dl class="lista-datos">
            <div class="dato">
              <dt>Código de empresa</dt>
              <dd>{{ solicitud.codigo_empresa || '—' }}</dd>
            </div>
            <div class="dato">
              <dt>Código de ficha</dt>
              <dd>
                <router-link
                  v-if="solicitud.codigo_ficha"
                  to="/admin/fichas"
                  class="enlace-interno codigo-ficha"
                  title="Ver en Gestión de Fichas"
                >
                  {{ solicitud.codigo_ficha }}
                  <font-awesome-icon icon="fa-solid fa-arrow-up-right-from-square" />
                </router-link>
                <span v-else class="pendiente">Sin asignar</span>
              </dd>
            </div>
            <div class="dato">
              <dt>Inscritos</dt>
              <dd><strong>{{ solicitud.cantidad_inscritos }}</strong> personas</dd>
            </div>
          </dl>
        </section>
      </div>

      <!-- Resultados de aprendices inscritos (Excel que adjunta la coordinación) -->
      <section class="seccion resultados-inscritos">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-user-check" /> RESULTADOS DE INSCRITOS
        </h4>
        <p class="gestion-texto">
          Adjunte el Excel con los resultados de los aprendices inscritos. Será el
          <strong>único documento que el instructor podrá descargar</strong> desde
          "Mis solicitudes" cuando la ficha esté Publicada.
        </p>

        <div v-if="archivoResultados" class="adjunto">
          <div class="adjunto-fila">
            <span class="adjunto-icono resultado" aria-hidden="true">
              <font-awesome-icon icon="fa-solid fa-user-check" />
            </span>
            <span class="adjunto-datos">
              <span class="adjunto-etiqueta">Resultados de aprendices inscritos</span>
              <span class="adjunto-nombre">{{ archivoResultados.nombre }}</span>
            </span>
            <span class="adjunto-acciones">
              <a
                class="btn-adjunto descarga"
                :href="urlResultados"
                :download="archivoResultados.nombre"
                :title="`Descargar ${archivoResultados.nombre}`"
              >
                <font-awesome-icon icon="fa-solid fa-download" /> Descargar
              </a>
              <button
                type="button"
                class="btn-adjunto"
                :disabled="subiendoResultados"
                title="Reemplazar el archivo de resultados por una versión nueva"
                @click="abrirSelectorResultados"
              >
                <font-awesome-icon
                  :icon="subiendoResultados ? ['fas', 'circle-notch'] : 'fa-solid fa-arrows-rotate'"
                  :spin="subiendoResultados"
                />
                {{ subiendoResultados ? 'Adjuntando...' : 'Reemplazar' }}
              </button>
            </span>
          </div>
        </div>

        <button
          v-else
          type="button"
          class="btn-adjuntar-resultados"
          :disabled="subiendoResultados"
          title="Adjuntar el Excel con los resultados de aprendices inscritos"
          @click="abrirSelectorResultados"
        >
          <font-awesome-icon
            :icon="subiendoResultados ? ['fas', 'circle-notch'] : 'fa-solid fa-cloud-arrow-up'"
            :spin="subiendoResultados"
          />
          {{ subiendoResultados ? 'Adjuntando...' : 'Adjuntar resultados (Excel)' }}
        </button>

        <input
          ref="inputResultados"
          type="file"
          accept=".xlsx,.xls,.xlsm"
          class="input-oculto"
          @change="seleccionarResultados"
        />
      </section>

      <!-- Documentos -->
      <section class="seccion">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-paperclip" /> DOCUMENTOS
        </h4>

        <!-- Archivos subidos por el instructor (almacenados en VoltMind) -->
        <div v-if="archivosSubidos.length" class="adjuntos">
          <div
            v-for="a in archivosSubidos"
            :key="a.campo"
            class="adjunto"
            :class="{ abierto: previewCampo === a.campo }"
          >
            <div class="adjunto-fila">
              <span class="adjunto-icono" aria-hidden="true">
                <font-awesome-icon :icon="a.icono" />
              </span>
              <span class="adjunto-datos">
                <span class="adjunto-etiqueta">{{ a.etiqueta }}</span>
                <span class="adjunto-nombre">{{ a.nombre }}</span>
              </span>
              <span class="adjunto-acciones">
                <button
                  type="button"
                  class="btn-adjunto"
                  :title="previewCampo === a.campo
                    ? 'Ocultar la vista previa'
                    : `Ver una vista previa de ${a.nombre}`"
                  @click="alternarPrevia(a)"
                >
                  <font-awesome-icon :icon="previewCampo === a.campo ? 'fa-solid fa-xmark' : 'fa-solid fa-eye'" />
                  {{ previewCampo === a.campo ? 'Ocultar' : 'Vista previa' }}
                </button>
                <a
                  class="btn-adjunto descarga"
                  :href="a.urlDescarga"
                  :download="a.nombre"
                  :title="`Descargar ${a.nombre}`"
                >
                  <font-awesome-icon icon="fa-solid fa-download" /> Descargar
                </a>
              </span>
            </div>
            <div v-if="previewCampo === a.campo" class="previa">
              <p v-if="previewCargando" class="previa-nota">
                <font-awesome-icon :icon="['fas', 'circle-notch']" spin /> Cargando vista previa...
              </p>
              <p v-else-if="previewError" class="previa-nota">{{ previewError }}</p>
              <img
                v-else-if="a.tipo === 'imagen'"
                class="previa-imagen"
                :src="a.urlInline"
                :alt="`Vista previa de ${a.nombre}`"
              />
              <iframe
                v-else-if="a.tipo === 'pdf'"
                class="previa-pdf"
                :src="a.urlInline"
                :title="`Vista previa de ${a.nombre}`"
              ></iframe>
              <pre v-else-if="a.tipo === 'texto'" class="previa-texto">{{ previewTexto }}</pre>
              <p v-else class="previa-nota">
                Los archivos de Excel o Word no tienen vista previa en el navegador;
                use <strong>Descargar</strong> para revisarlo.
              </p>
            </div>
          </div>
        </div>

        <div class="documentos">
          <a
            v-for="doc in documentos"
            :key="doc.etiqueta"
            :href="doc.url || null"
            target="_blank"
            rel="noopener"
            class="doc-chip"
            :class="{ 'doc-vacio': !doc.url }"
            :title="doc.url ? 'Abrir en una pestaña nueva' : 'Documento sin adjuntar'"
          >
            <font-awesome-icon :icon="doc.icono" />
            <span>{{ doc.etiqueta }}</span>
            <font-awesome-icon v-if="doc.url" icon="fa-solid fa-arrow-up-right-from-square" class="icono-salida" />
            <span v-else class="pendiente">Sin adjuntar</span>
          </a>
        </div>
      </section>

      <!-- Observaciones -->
      <section v-if="solicitud.observaciones" class="seccion">
        <h4 class="seccion-titulo">
          <font-awesome-icon icon="fa-solid fa-circle-info" /> OBSERVACIONES
        </h4>
        <p class="observaciones">{{ solicitud.observaciones }}</p>
      </section>
    </div>

    <template #footer>
      <button class="btn-secundario" @click="$emit('editar', solicitud)">
        <font-awesome-icon icon="fa-solid fa-pen-to-square" /> Editar solicitud
      </button>
      <button class="btn-eliminar" @click="$emit('eliminar', solicitud)">
        <font-awesome-icon icon="fa-solid fa-trash-can" /> Eliminar
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import { complementariasService } from '@/services/complementariasService';
import { ESTADOS_TABLERO, PASOS_SEGUIMIENTO, ETIQUETAS_ARCHIVO } from '@/stores/complementarias';

const props = defineProps({
  show: { type: Boolean, required: true },
  solicitud: { type: Object, default: null },
  // La vista padre pone true mientras el backend reenvía el aviso al instructor
  enviandoAviso: { type: Boolean, default: false },
  // La vista padre pone true mientras el backend guarda el Excel de resultados
  subiendoResultados: { type: Boolean, default: false },
});

const emit = defineEmits([
  'update:show',
  'close',
  'actualizar',
  'editar',
  'eliminar',
  'reenviar-aviso',
  'subir-resultados',
]);

// ── Vista previa de los archivos adjuntos ──
const previewCampo = ref(null); // campo del archivo con la vista previa abierta
const previewTexto = ref(''); // contenido mostrado para archivos de texto
const previewCargando = ref(false);
const previewError = ref('');

// ── Gestión rápida (Pendiente → Publicada en un solo paso) ──
const codigoEmpresaRapido = ref('');
const codigoFichaRapido = ref('');

const publicarRapido = () => {
  emit('actualizar', props.solicitud.id, {
    codigo_empresa: codigoEmpresaRapido.value,
    codigo_ficha: codigoFichaRapido.value,
    estado: 'Publicada',
  });
};

// Al cambiar de solicitud: precargar los códigos y cerrar la vista previa
watch(
  () => props.solicitud?.id,
  () => {
    codigoEmpresaRapido.value = props.solicitud?.codigo_empresa || '';
    codigoFichaRapido.value = props.solicitud?.codigo_ficha || '';
    previewCampo.value = null;
    previewTexto.value = '';
    previewError.value = '';
  },
  { immediate: true }
);

const rango = (inicio, fin) => {
  if (!inicio && !fin) return '—';
  return `${inicio || '—'}  →  ${fin || '—'}`;
};

/** Fecha/hora del último aviso de publicación, legible en es-CO. */
const formatearAviso = (iso) => {
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const claseEstado = (estado) => ({
  'estado-pendiente': estado === 'Pendiente',
  'estado-publicada': estado === 'Publicada',
  'estado-ejecucion': estado === 'En Ejecución',
  'estado-cancelada': estado === 'Cancelada',
});

// Iconos de los archivos subidos por el instructor (las etiquetas vienen del store)
const ICONOS_ARCHIVO = {
  matriz: 'fa-solid fa-table-list',
  plano: 'fa-solid fa-code',
  adicional: 'fa-solid fa-paperclip',
};

/** Qué renderizador de vista previa admite el archivo, según su extensión. */
const tipoPrevia = (nombre) => {
  const ext = nombre.includes('.') ? nombre.split('.').pop().toLowerCase() : '';
  if (['png', 'jpg', 'jpeg'].includes(ext)) return 'imagen';
  if (ext === 'pdf') return 'pdf';
  if (['txt', 'csv'].includes(ext)) return 'texto';
  return 'ninguna';
};

// ── Resultados de inscritos (Excel que adjunta el administrador) ──
const inputResultados = ref(null);

const archivoResultados = computed(
  () => (props.solicitud?.archivos || []).find((a) => a.campo === 'resultados') || null
);

const urlResultados = computed(() =>
  props.solicitud ? complementariasService.urlArchivo(props.solicitud.id, 'resultados') : ''
);

const abrirSelectorResultados = () => inputResultados.value?.click();

const seleccionarResultados = (evento) => {
  const archivo = evento.target.files?.[0];
  evento.target.value = ''; // permite volver a elegir el mismo archivo tras un error
  if (!archivo) return;
  // Extensión y tamaño los valida el backend (422 con mensaje claro)
  emit('subir-resultados', props.solicitud.id, archivo);
};

// Archivos entregados por el instructor (los resultados tienen su propia sección)
const archivosSubidos = computed(() => {
  if (!props.solicitud) return [];
  return (props.solicitud.archivos || [])
    .filter((a) => a.campo !== 'resultados')
    .map((a) => ({
    campo: a.campo,
    nombre: a.nombre,
    etiqueta: ETIQUETAS_ARCHIVO[a.campo] || a.campo,
    icono: ICONOS_ARCHIVO[a.campo] || 'fa-solid fa-paperclip',
    tipo: tipoPrevia(a.nombre || ''),
    urlDescarga: complementariasService.urlArchivo(props.solicitud.id, a.campo),
    urlInline: complementariasService.urlArchivo(props.solicitud.id, a.campo, { inline: true }),
  }));
});

const LINEAS_MAXIMAS_PREVIA = 60;

const alternarPrevia = async (archivo) => {
  if (previewCampo.value === archivo.campo) {
    previewCampo.value = null;
    return;
  }
  previewCampo.value = archivo.campo;
  previewTexto.value = '';
  previewError.value = '';
  if (archivo.tipo !== 'texto') return;

  // Los archivos de texto (plano / csv) se leen y se muestran recortados
  previewCargando.value = true;
  try {
    const respuesta = await fetch(archivo.urlInline);
    if (!respuesta.ok) throw new Error();
    const lineas = (await respuesta.text()).split(/\r?\n/);
    previewTexto.value = lineas.slice(0, LINEAS_MAXIMAS_PREVIA).join('\n');
    if (lineas.length > LINEAS_MAXIMAS_PREVIA) {
      previewTexto.value += `\n… (${lineas.length - LINEAS_MAXIMAS_PREVIA} líneas más; descargue el archivo completo)`;
    }
  } catch {
    previewError.value = 'No se pudo cargar la vista previa. Descargue el archivo para revisarlo.';
  } finally {
    previewCargando.value = false;
  }
};

// Documentos por enlace (flujo del admin / registros antiguos).
// Si el instructor ya subió el archivo, se oculta su gemelo de enlace vacío.
const documentos = computed(() => {
  if (!props.solicitud) return [];
  const s = props.solicitud;
  const tieneSubido = (campo) => (s.archivos || []).some((a) => a.campo === campo);
  const base = [
    { etiqueta: 'Matriz de la ficha (enlace)', url: s.enlace_matriz_ficha, icono: 'fa-solid fa-table-list', oculto: tieneSubido('matriz') },
    { etiqueta: 'Archivo plano (enlace)', url: s.enlace_archivo_plano, icono: 'fa-solid fa-code', oculto: tieneSubido('plano') },
    { etiqueta: 'Carta de la empresa', url: s.enlace_carta_empresa, icono: 'fa-solid fa-file-contract' },
    { etiqueta: 'Formato de solicitud', url: s.enlace_formato_solicitud, icono: 'fa-solid fa-clipboard-list' },
    { etiqueta: 'Lista de matriculados', url: s.enlace_lista_matriculados, icono: 'fa-solid fa-users' },
  ].filter((d) => !(d.oculto && !d.url));
  const pdfs = (s.enlaces_pdf || []).map((url, i) => ({
    etiqueta: `PDF adjunto ${i + 1}`,
    url,
    icono: 'fa-solid fa-file-pdf',
  }));
  return [...base, ...pdfs];
});
</script>

<style scoped>
/* Ensancha el BaseModal solo para este detalle */
.modal-detalle-comp :deep(.modal-container) {
  max-width: 860px;
}

.detalle-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detalle-encabezado {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.codigo-version {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip-codigo,
.chip-duracion {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.35rem 0.7rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--texto-secundario);
  font-family: monospace;
}

.selector-estado {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.etiqueta-mini {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-secundario);
  text-transform: uppercase;
}

.form-select {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--texto-principal);
  cursor: pointer;
  outline: none;
}

.form-select:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.estado-pendiente { color: #8a6d00; border-color: rgba(253, 195, 0, 0.55); }
[data-theme="dark"] .estado-pendiente { color: #fdc300; }
.estado-publicada { color: var(--sena-azul-oscuro); border-color: rgba(0, 48, 64, 0.35); }
.estado-ejecucion { color: var(--sena-verde-oscuro); border-color: rgba(57, 169, 0, 0.45); }
.estado-cancelada { color: #d32f2f; border-color: rgba(211, 47, 47, 0.4); }

/* ── Secciones ── */
.grilla-secciones {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.seccion {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.seccion-titulo {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-secundario);
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.lista-datos {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin: 0;
}

.dato {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.dato dt {
  font-size: 0.78rem;
  color: var(--texto-secundario);
  flex-shrink: 0;
}

.dato dd {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--texto-principal);
  text-align: right;
  overflow-wrap: anywhere;
}

.fecha-rango {
  font-family: monospace;
  white-space: pre;
}

.enlace-interno {
  color: var(--sena-verde-oscuro);
  text-decoration: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.enlace-interno:hover {
  text-decoration: underline;
}

.codigo-ficha {
  font-family: monospace;
  font-size: 0.95rem;
}

.pendiente {
  color: var(--texto-secundario);
  font-style: italic;
  font-weight: 400;
  font-size: 0.8rem;
}

/* ── Aviso al instructor ── */
.aviso-fila {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.aviso-estado {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.aviso-estado.ok {
  color: var(--sena-verde-oscuro);
}

.aviso-estado.pendiente-aviso {
  color: #8a6d00;
}

[data-theme="dark"] .aviso-estado.pendiente-aviso { color: #fdc300; }

.btn-reenviar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--sena-verde);
  border: none;
  border-radius: 8px;
  padding: 0.55rem 1rem;
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--sena-blanco);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reenviar:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
  transform: translateY(-1px);
}

.btn-reenviar:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ── Stepper de seguimiento ── */
.stepper {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0;
}

.paso {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
  text-align: center;
}

/* Conector entre pasos */
.paso:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 16px;
  left: calc(50% + 20px);
  width: calc(100% - 40px);
  height: 2px;
  background: var(--borde);
}

.paso.completado:not(:last-child)::after {
  background: var(--sena-verde);
}

.paso-marcador {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--borde);
  background: var(--fondo-tarjetas);
  color: var(--texto-secundario);
  font-weight: 800;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 1;
}

.paso.completado .paso-marcador {
  background: var(--sena-verde);
  border-color: var(--sena-verde);
  color: var(--sena-blanco);
}

.paso-marcador:hover {
  border-color: var(--sena-verde);
  transform: scale(1.08);
}

.paso-etiqueta {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
  line-height: 1.2;
}

.paso.completado .paso-etiqueta {
  color: var(--sena-verde-oscuro);
}

/* ── Gestión rápida (Pendiente → Publicada) ── */
.gestion-rapida {
  border-left: 4px solid var(--sena-verde);
}

.gestion-texto {
  margin: 0 0 0.8rem;
  font-size: 0.82rem;
  color: var(--texto-secundario);
  line-height: 1.5;
}

.gestion-campos {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.gestion-campo {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 160px;
}

.gestion-input {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 700;
  font-family: monospace;
  color: var(--texto-principal);
  outline: none;
}

.gestion-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

.btn-publicar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--sena-verde);
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--sena-blanco);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-publicar:hover:not(:disabled) {
  background: var(--sena-verde-oscuro);
  transform: translateY(-1px);
}

.btn-publicar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Resultados de inscritos (Excel del administrador) ── */
.resultados-inscritos {
  border-left: 4px solid var(--sena-azul-oscuro);
}

.btn-adjuntar-resultados {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(57, 169, 0, 0.06);
  border: 1.5px dashed var(--sena-verde);
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-size: 0.8rem;
  font-weight: 800;
  font-family: inherit;
  color: var(--sena-verde-oscuro);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-adjuntar-resultados:hover:not(:disabled) {
  background: rgba(57, 169, 0, 0.12);
}

.btn-adjuntar-resultados:disabled {
  opacity: 0.6;
  cursor: progress;
}

.input-oculto {
  display: none;
}

.adjunto-icono.resultado {
  background: rgba(0, 50, 77, 0.08);
  color: var(--sena-azul-oscuro);
}

/* ── Adjuntos del instructor con vista previa ── */
.adjuntos {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 0.8rem;
}

.adjunto {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 10px;
  overflow: hidden;
}

.adjunto.abierto {
  border-color: var(--sena-verde);
}

.adjunto-fila {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.6rem 0.8rem;
  flex-wrap: wrap;
}

.adjunto-icono {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde-oscuro);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.adjunto-datos {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 140px;
}

.adjunto-etiqueta {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

.adjunto-nombre {
  font-size: 0.72rem;
  font-family: monospace;
  color: var(--texto-secundario);
  overflow-wrap: anywhere;
}

.adjunto-acciones {
  display: flex;
  gap: 8px;
}

.btn-adjunto {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.4rem 0.7rem;
  font-size: 0.74rem;
  font-weight: 800;
  font-family: inherit;
  color: var(--texto-principal);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-adjunto:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
}

.previa {
  border-top: 1px solid var(--borde);
  background: var(--fondo-app);
  padding: 0.8rem;
}

.previa-nota {
  margin: 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
}

.previa-imagen {
  display: block;
  max-width: 100%;
  max-height: 420px;
  margin: 0 auto;
  border-radius: 8px;
}

.previa-pdf {
  display: block;
  width: 100%;
  height: 420px;
  border: none;
  border-radius: 8px;
  background: var(--fondo-tarjetas);
}

.previa-texto {
  margin: 0;
  max-height: 320px;
  overflow: auto;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--texto-principal);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

/* ── Documentos ── */
.documentos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.doc-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.5rem 0.8rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sena-azul-oscuro);
  text-decoration: none;
  transition: all 0.2s ease;
}

.doc-chip:not(.doc-vacio):hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  transform: translateY(-2px);
}

.doc-vacio {
  color: var(--texto-secundario);
  cursor: default;
  opacity: 0.75;
}

.icono-salida {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}

.observaciones {
  margin: 0;
  font-size: 0.85rem;
  color: var(--texto-principal);
  line-height: 1.5;
}

/* ── Botones del footer ── */
.btn-secundario,
.btn-eliminar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  padding: 0.65rem 1.2rem;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secundario {
  background: var(--sena-verde);
  border: none;
  color: var(--sena-blanco);
}

.btn-secundario:hover {
  background: var(--sena-verde-oscuro);
}

.btn-eliminar {
  background: transparent;
  border: 1px solid rgba(229, 62, 62, 0.4);
  color: #e53e3e;
}

.btn-eliminar:hover {
  background: rgba(229, 62, 62, 0.1);
}

@media (max-width: 600px) {
  .stepper {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  .paso {
    flex-basis: 45%;
  }
  .paso:not(:last-child)::after {
    display: none;
  }
}
</style>
