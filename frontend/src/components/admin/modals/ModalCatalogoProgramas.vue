<template>
  <div class="modal-catalogo">
    <BaseModal
      :show="show"
      title="CATÁLOGO DE PROGRAMAS DE FORMACIÓN"
      :closeOnBackdrop="false"
      @update:show="$emit('update:show', $event)"
      @close="$emit('close')"
    >
      <div class="cuerpo">
        <p class="contexto">
          Cada programa registra su versión, nivel y matriz de competencias. Al crear una ficha,
          su <strong>diagnóstico se genera desde este catálogo</strong> (lo alimenta quien sube
          los programas nuevos, sin volver a digitar la matriz en cada ficha).
        </p>

        <!-- Programas registrados -->
        <section class="seccion">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-folder-open" /> Programas registrados
            <span class="conteo">{{ store.programas.length }}</span>
          </h4>
          <ul v-if="store.programas.length" class="lista-programas">
            <li v-for="p in store.programas" :key="p.id" class="programa-fila">
              <div class="programa-info">
                <span class="programa-nombre">{{ p.nombre }}</span>
                <span class="programa-datos">
                  Versión {{ p.version }} · {{ p.nivel }} · {{ p.total_horas }} h ·
                  {{ p.competencias.length }} competencias
                </span>
              </div>
              <button
                class="btn-mini"
                type="button"
                :title="verId === p.id ? 'Ocultar competencias' : 'Ver competencias'"
                @click="verId = verId === p.id ? '' : p.id"
              >
                <font-awesome-icon :icon="verId === p.id ? 'fa-solid fa-chevron-down' : 'fa-solid fa-eye'" />
              </button>
              <ul v-if="verId === p.id" class="vista-previa">
                <li v-for="(c, i) in p.competencias" :key="i">
                  <span class="punto-color" :style="{ background: colorTipo(c.tipo) }"></span>
                  {{ c.nombre }} <small>({{ c.tipo }} · {{ c.horas }} h)</small>
                </li>
              </ul>
            </li>
          </ul>
          <p v-else class="ayuda">Aún no hay programas en el catálogo.</p>
        </section>

        <!-- Registrar un programa nuevo -->
        <section class="seccion seccion-nueva">
          <h4 class="seccion-titulo">
            <font-awesome-icon icon="fa-solid fa-plus" /> Registrar un programa nuevo
          </h4>
          <div class="rejilla">
            <label class="campo campo-ancho">
              <span>Nombre del programa *</span>
              <input v-model.trim="form.nombre" type="text" class="form-input"
                     placeholder="Ej: Gestión Ambiental" />
            </label>
            <label class="campo">
              <span>Versión *</span>
              <input v-model.trim="form.version" type="text" class="form-input" placeholder="Ej: 1" />
            </label>
            <label class="campo">
              <span>Nivel *</span>
              <select v-model="form.nivel" class="form-input">
                <option value="" disabled>Seleccione...</option>
                <option v-for="n in NIVELES_FORMACION" :key="n" :value="n">{{ n }}</option>
              </select>
            </label>
          </div>

          <EditorCompetencias v-model="form.competencias" />

          <p v-if="error" class="banner banner-error">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" /> {{ error }}
          </p>
        </section>
      </div>

      <template #footer>
        <button class="btn-cancelar" :disabled="guardando" @click="$emit('close')">Cerrar</button>
        <button class="btn-guardar" :disabled="guardando" @click="guardar">
          <font-awesome-icon v-if="guardando" :icon="['fas', 'circle-notch']" spin />
          <font-awesome-icon v-else icon="fa-solid fa-check" />
          Guardar programa
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
// Catálogo de programas de formación: nombre + versión + nivel + matriz de
// competencias. Es la fuente del diagnóstico de las fichas nuevas.
import { reactive, ref, watch } from 'vue';
import { useToast } from 'vue-toastification';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import EditorCompetencias from '@/components/admin/EditorCompetencias.vue';
import {
  useTituladasStore,
  NIVELES_FORMACION,
  COLORES_TIPO_COMPETENCIA,
} from '@/stores/tituladas';

const props = defineProps({
  show: { type: Boolean, required: true },
});
const emit = defineEmits(['update:show', 'close']);

const store = useTituladasStore();
const toast = useToast();

const formVacio = () => ({
  nombre: '',
  version: '',
  nivel: '',
  competencias: [{ id: null, nombre: 'Inducción', tipo: 'Inducción', horas: 30 }],
});

const form = reactive(formVacio());
const verId = ref('');
const error = ref('');
const guardando = ref(false);

watch(
  () => props.show,
  (abierto) => {
    if (!abierto) return;
    Object.assign(form, formVacio());
    verId.value = '';
    error.value = '';
  }
);

const colorTipo = (tipo) => COLORES_TIPO_COMPETENCIA[tipo] || 'var(--borde)';

async function guardar() {
  error.value = '';
  if (!form.nombre || form.nombre.length < 3) return (error.value = 'Escriba el nombre del programa.');
  if (!form.version) return (error.value = 'Indique la versión del programa.');
  if (!form.nivel) return (error.value = 'Seleccione el nivel de formación.');
  if (!form.competencias.length) return (error.value = 'Agregue las competencias del programa.');
  const invalida = form.competencias.find(
    (c) => !c.nombre || c.nombre.length < 3 || !c.horas || c.horas < 1
  );
  if (invalida) {
    error.value = 'Cada competencia necesita un nombre (mínimo 3 letras) y horas mayores a cero.';
    return;
  }

  guardando.value = true;
  const resultado = await store.crearPrograma({
    nombre: form.nombre,
    version: form.version,
    nivel: form.nivel,
    competencias: form.competencias.map(({ nombre, tipo, horas }) => ({ nombre, tipo, horas })),
  });
  guardando.value = false;

  if (resultado.success) {
    toast.success(`Programa "${resultado.programa.nombre}" agregado al catálogo.`);
    Object.assign(form, formVacio());
  } else {
    error.value = resultado.error;
  }
}
</script>

<style scoped>
.modal-catalogo :deep(.modal-container) {
  max-width: 780px;
}

.cuerpo {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.contexto {
  margin: 0;
  font-size: 0.8rem;
  color: var(--texto-secundario);
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-left: 4px solid var(--sena-verde);
  border-radius: 10px;
  padding: 0.7rem 1rem;
}

.seccion {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.seccion-nueva {
  border-top: 1px dashed var(--borde);
  padding-top: 1rem;
}

.seccion-titulo {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: var(--texto-principal);
  display: flex;
  align-items: center;
  gap: 8px;
}

.seccion-titulo svg { color: var(--sena-verde); }

.conteo {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 6px;
  padding: 1px 8px;
  font-size: 0.7rem;
}

.lista-programas {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 240px;
  overflow-y: auto;
}

.programa-fila {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 0.6rem 0.9rem;
}

.programa-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.programa-nombre { font-size: 0.8rem; font-weight: 700; }
.programa-datos { font-size: 0.7rem; color: var(--texto-secundario); }

.btn-mini {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  width: 30px;
  height: 30px;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-mini:hover { border-color: var(--sena-verde); color: var(--sena-verde); }

.vista-previa {
  grid-column: 1 / -1;
  list-style: none;
  margin: 0;
  padding: 0.5rem 0 0;
  border-top: 1px dashed var(--borde);
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.74rem;
}

.vista-previa li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.vista-previa small { color: var(--texto-secundario); font-weight: 500; }

.punto-color {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.15);
}

.ayuda {
  margin: 0;
  font-size: 0.74rem;
  color: var(--texto-secundario);
  font-style: italic;
  border: 1px dashed var(--borde);
  border-radius: 10px;
  padding: 0.7rem 1rem;
}

.rejilla {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 12px;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.campo-ancho { min-width: 0; }

.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.83rem;
  outline: none;
  box-sizing: border-box;
  width: 100%;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

select.form-input { cursor: pointer; }

.banner {
  margin: 0;
  border-radius: 10px;
  padding: 0.7rem 1rem;
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.banner-error {
  background: rgba(229, 62, 62, 0.1);
  border: 1px solid rgba(229, 62, 62, 0.4);
  color: #c53030;
}

[data-theme="dark"] .banner-error { color: #fc8181; }

.btn-guardar {
  background: var(--sena-verde);
  color: var(--sena-blanco);
  border: none;
  padding: 0.7rem 1.4rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-guardar:hover:not(:disabled) { background: var(--sena-verde-oscuro); }

.btn-cancelar {
  background: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancelar:hover:not(:disabled) { border-color: var(--texto-secundario); }

.btn-guardar:disabled,
.btn-cancelar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .rejilla { grid-template-columns: 1fr; }
}
</style>
