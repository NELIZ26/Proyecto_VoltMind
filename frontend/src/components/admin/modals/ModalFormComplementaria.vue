<template>
  <BaseModal
    :show="show"
    :title="esEdicion ? 'Editar solicitud complementaria' : 'Nueva solicitud complementaria'"
    class="modal-form-comp"
    @update:show="$emit('update:show', $event)"
    @close="$emit('close')"
  >
    <form class="form-comp" @submit.prevent="guardar">
      <!-- Solicitante -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-user-tie" /> SOLICITANTE</legend>
        <div class="fila">
          <label class="campo campo-doble">
            <span>Nombre completo del instructor *</span>
            <input v-model.trim="form.nombre_instructor" type="text" class="form-input" required minlength="3" placeholder="Ej: Carlos Díaz" />
          </label>
        </div>
        <div class="fila">
          <label class="campo">
            <span>Correo institucional</span>
            <input v-model.trim="form.correo_instructor" type="email" class="form-input" placeholder="nombre@sena.edu.co" />
          </label>
          <label class="campo">
            <span>Celular</span>
            <input v-model.trim="form.celular_instructor" type="tel" class="form-input" placeholder="3XX XXX XXXX" />
          </label>
        </div>
      </fieldset>

      <!-- Programa -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-graduation-cap" /> PROGRAMA</legend>
        <div class="fila">
          <label class="campo campo-doble">
            <span>Nombre del programa *</span>
            <input v-model.trim="form.nombre_programa" type="text" class="form-input" required minlength="3" placeholder="Ej: Excel Básico para el Registro de Información" />
          </label>
        </div>
        <div class="fila">
          <label class="campo">
            <span>Código *</span>
            <input v-model.trim="form.codigo_programa" type="text" class="form-input" required placeholder="Ej: 12310114" />
          </label>
          <label class="campo">
            <span>Versión</span>
            <input v-model.trim="form.version_programa" type="text" class="form-input" placeholder="1" />
          </label>
          <label class="campo">
            <span>Duración (horas)</span>
            <input v-model.number="form.duracion_horas" type="number" class="form-input" min="0" max="880" />
          </label>
        </div>
      </fieldset>

      <!-- Fechas -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-calendar-days" /> FECHAS</legend>
        <div class="fila">
          <label class="campo">
            <span>Inicio de inscripciones</span>
            <input v-model="form.fecha_inicio_inscripcion" type="date" class="form-input" />
          </label>
          <label class="campo">
            <span>Cierre de inscripciones</span>
            <input v-model="form.fecha_cierre_inscripcion" type="date" class="form-input" />
          </label>
        </div>
        <div class="fila">
          <label class="campo">
            <span>Inicio de formación</span>
            <input v-model="form.fecha_inicio_formacion" type="date" class="form-input" />
          </label>
          <label class="campo">
            <span>Fin de formación</span>
            <input v-model="form.fecha_fin_formacion" type="date" class="form-input" />
          </label>
        </div>
      </fieldset>

      <!-- Logística -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-location-dot" /> LOGÍSTICA</legend>
        <div class="fila">
          <label class="campo">
            <span>Jornada</span>
            <select v-model="form.jornada" class="form-input">
              <option value="">Sin definir</option>
              <option v-for="j in JORNADAS" :key="j" :value="j">{{ j }}</option>
            </select>
          </label>
          <label class="campo">
            <span>Municipio</span>
            <input v-model.trim="form.municipio" type="text" class="form-input" placeholder="Ej: Puerto Asís" list="municipios-putumayo" />
            <datalist id="municipios-putumayo">
              <option v-for="m in MUNICIPIOS_PUTUMAYO" :key="m" :value="m" />
            </datalist>
          </label>
        </div>
        <div class="fila">
          <label class="campo campo-doble">
            <span>Lugar de ejecución</span>
            <input v-model.trim="form.lugar_ejecucion" type="text" class="form-input" placeholder="Ej: Alcaldía de Puerto Asís — Sala de sistemas" />
          </label>
        </div>
      </fieldset>

      <!-- Documentos -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-paperclip" /> DOCUMENTOS (ENLACES)</legend>
        <div class="fila">
          <label class="campo">
            <span>Carta de la empresa</span>
            <input v-model.trim="form.enlace_carta_empresa" type="url" class="form-input" placeholder="https://..." />
          </label>
          <label class="campo">
            <span>Formato de solicitud</span>
            <input v-model.trim="form.enlace_formato_solicitud" type="url" class="form-input" placeholder="https://..." />
          </label>
        </div>
        <div class="fila">
          <label class="campo">
            <span>Matriz de la ficha</span>
            <input v-model.trim="form.enlace_matriz_ficha" type="url" class="form-input" placeholder="https://..." />
          </label>
          <label class="campo">
            <span>Archivo plano</span>
            <input v-model.trim="form.enlace_archivo_plano" type="url" class="form-input" placeholder="https://..." />
          </label>
          <label class="campo">
            <span>Lista de matriculados</span>
            <input v-model.trim="form.enlace_lista_matriculados" type="url" class="form-input" placeholder="https://..." />
          </label>
        </div>
        <div class="fila">
          <label class="campo campo-doble">
            <span>Otros PDF (un enlace por línea)</span>
            <textarea v-model="pdfsTexto" class="form-input" rows="2" placeholder="https://...&#10;https://..."></textarea>
          </label>
        </div>
      </fieldset>

      <!-- Seguimiento -->
      <fieldset class="grupo">
        <legend><font-awesome-icon icon="fa-solid fa-list-check" /> SEGUIMIENTO</legend>
        <div class="fila">
          <label class="campo">
            <span>Código de empresa</span>
            <input v-model.trim="form.codigo_empresa" type="text" class="form-input" placeholder="Ej: EMP-9014521" />
          </label>
          <label class="campo">
            <span>Código de ficha</span>
            <input v-model.trim="form.codigo_ficha" type="text" class="form-input" placeholder="Se asigna al publicar" />
          </label>
          <label class="campo">
            <span>Inscritos</span>
            <input v-model.number="form.cantidad_inscritos" type="number" class="form-input" min="0" max="500" />
          </label>
        </div>
        <div class="fila">
          <label class="campo">
            <span>Estado *</span>
            <select v-model="form.estado" class="form-input" required>
              <option v-for="e in ESTADOS_TABLERO" :key="e" :value="e">{{ e }}</option>
            </select>
          </label>
          <div class="campo checks-seguimiento">
            <span>Pasos completados</span>
            <div class="checks">
              <label v-for="paso in PASOS_SEGUIMIENTO" :key="paso.campo" class="check">
                <input v-model="form[paso.campo]" type="checkbox" />
                {{ paso.etiqueta }}
              </label>
            </div>
          </div>
        </div>
        <div class="fila">
          <label class="campo campo-doble">
            <span>Observaciones</span>
            <textarea v-model.trim="form.observaciones" class="form-input" rows="2" maxlength="1000" placeholder="Notas de seguimiento visibles para todo el equipo"></textarea>
          </label>
        </div>
      </fieldset>
    </form>

    <template #footer>
      <button type="button" class="btn-cancelar" @click="$emit('update:show', false)">Cancelar</button>
      <button type="button" class="btn-guardar" @click="guardar">
        <font-awesome-icon icon="fa-solid fa-save" />
        {{ esEdicion ? 'Guardar cambios' : 'Crear solicitud' }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useToast } from 'vue-toastification';
import BaseModal from '@/components/admin/modals/BaseModal.vue';
import {
  ESTADOS_TABLERO,
  PASOS_SEGUIMIENTO,
  JORNADAS,
  MUNICIPIOS_PUTUMAYO,
} from '@/stores/complementarias';

const props = defineProps({
  show: { type: Boolean, required: true },
  // Solicitud a editar; null para crear una nueva
  solicitudData: { type: Object, default: null },
});

const emit = defineEmits(['update:show', 'close', 'save']);
const toast = useToast();

const formVacio = () => ({
  nombre_instructor: '',
  correo_instructor: '',
  celular_instructor: '',
  codigo_programa: '',
  version_programa: '1',
  nombre_programa: '',
  duracion_horas: 40,
  fecha_inicio_inscripcion: '',
  fecha_cierre_inscripcion: '',
  fecha_inicio_formacion: '',
  fecha_fin_formacion: '',
  jornada: '',
  municipio: '',
  lugar_ejecucion: '',
  enlace_carta_empresa: '',
  enlace_formato_solicitud: '',
  enlace_matriz_ficha: '',
  enlace_archivo_plano: '',
  enlaces_pdf: [],
  codigo_empresa: '',
  codigo_ficha: '',
  publicacion: false,
  asignar_ficha: false,
  gestion_ficha: false,
  proceso_matricula: false,
  estado: 'Publicada',
  enlace_lista_matriculados: '',
  observaciones: '',
  cantidad_inscritos: 0,
});

const form = ref(formVacio());
const pdfsTexto = ref('');

const esEdicion = computed(() => !!props.solicitudData);

// Al abrir: precargar la solicitud a editar o limpiar el formulario
watch(
  () => props.show,
  (visible) => {
    if (!visible) return;
    if (props.solicitudData) {
      form.value = { ...formVacio(), ...props.solicitudData };
      pdfsTexto.value = (props.solicitudData.enlaces_pdf || []).join('\n');
    } else {
      form.value = formVacio();
      pdfsTexto.value = '';
    }
  }
);

const guardar = () => {
  if (!form.value.nombre_instructor || form.value.nombre_instructor.length < 3) {
    toast.error('Ingrese el nombre completo del instructor solicitante.');
    return;
  }
  if (!form.value.nombre_programa || form.value.nombre_programa.length < 3) {
    toast.error('Ingrese el nombre del programa de formación.');
    return;
  }
  if (!form.value.codigo_programa) {
    toast.error('Ingrese el código del programa (Sofía Plus).');
    return;
  }

  const { id, fecha_creacion, ...datos } = form.value;
  datos.enlaces_pdf = pdfsTexto.value
    .split('\n')
    .map((u) => u.trim())
    .filter(Boolean);
  datos.duracion_horas = Number(datos.duracion_horas) || 0;
  datos.cantidad_inscritos = Number(datos.cantidad_inscritos) || 0;

  emit('save', datos);
};
</script>

<style scoped>
/* Formulario amplio: dos columnas de campos */
.modal-form-comp :deep(.modal-container) {
  max-width: 760px;
}

.form-comp {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.grupo {
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 1rem 1.25rem 1.25rem;
  margin: 0;
  background: var(--fondo-app);
}

.grupo legend {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--texto-secundario);
  padding: 0 0.5rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.fila {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.fila:last-child {
  margin-bottom: 0;
}

.campo {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.campo-doble {
  flex-basis: 100%;
}

.campo > span {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.form-input {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 2px rgba(57, 169, 0, 0.2);
}

textarea.form-input {
  resize: vertical;
}

.checks-seguimiento {
  flex: 2;
}

.checks {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  padding-top: 4px;
}

.check {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--texto-principal);
  cursor: pointer;
}

.check input {
  accent-color: var(--sena-verde);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* Botones del footer */
.btn-cancelar,
.btn-guardar {
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

.btn-cancelar {
  background: transparent;
  border: 1px solid var(--borde);
  color: var(--texto-secundario);
}

.btn-cancelar:hover {
  background: var(--fondo-app);
}

.btn-guardar {
  background: var(--sena-verde);
  border: none;
  color: var(--sena-blanco);
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.2);
}

.btn-guardar:hover {
  background: var(--sena-verde-oscuro);
}
</style>
