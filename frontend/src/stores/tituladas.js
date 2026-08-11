// src/stores/tituladas.js
// ─────────────────────────────────────────────────────────────────────────────
// Store del módulo de Fichas Tituladas y Asignación de Ambientes.
//
// ✔ SIN datos mock: toda la información viene del backend FastAPI
//   (/api/tituladas/*), que calcula horas, % de programación y disponibilidad.
// ✔ Las validaciones de negocio (cruces de ficha/instructor/ambiente, contrato
//   vencido, período lectivo) son responsabilidad del backend (HTTP 409);
//   el store solo traduce el error para la UI.
// ─────────────────────────────────────────────────────────────────────────────
import { defineStore } from 'pinia';
import { tituladasService } from '@/services/tituladasService';

// Jornadas institucionales: bloques fijos de 6 horas
export const JORNADAS_TITULADAS = [
  { valor: 'Mañana', horario: '6:00 – 12:00' },
  { valor: 'Tarde', horario: '12:00 – 18:00' },
  { valor: 'Noche', horario: '18:00 – 24:00' },
];

// Colores institucionales de los tipos de competencia (leyenda del diagnóstico)
export const COLORES_TIPO_COMPETENCIA = {
  'Técnica': '#39A900',     // verde SENA: el corazón del programa
  'Básica': '#2980B9',      // azul
  'Transversal': '#E67E22', // naranja
  'Inducción': '#8E44AD',   // morado
};

// Metas institucionales (el backend las confirma en /indicadores)
export const META_PROGRAMACION = 70; // % ideal del programa a programar
export const META_TECNICA = 60;      // % mínimo de horas técnicas

// Niveles de formación titulada (catálogo de programas)
export const NIVELES_FORMACION = ['Operario', 'Auxiliar', 'Técnico', 'Tecnólogo'];

// Tipos de competencia del diagnóstico (mismo orden que el backend)
export const TIPOS_COMPETENCIA = ['Técnica', 'Básica', 'Transversal', 'Inducción'];

/** Horario legible de una jornada ("Mañana" → "6:00 – 12:00"). */
export const horarioJornada = (jornada) =>
  JORNADAS_TITULADAS.find((j) => j.valor === jornada)?.horario || '';

/** Fecha ISO → DD/MM/YYYY para mostrar en pantalla. */
export const formatearFecha = (iso) => {
  if (!iso) return '—';
  const [anio, mes, dia] = iso.split('-');
  return `${dia}/${mes}/${anio}`;
};

export const useTituladasStore = defineStore('tituladas', {
  state: () => ({
    fichas: [],
    indicadores: null,
    instructores: [],
    ambientes: [],
    programas: [],
    // Detalle abierto (diagnóstico + asignaciones del calendario)
    fichaActual: null,
    // Estado de UI
    cargando: false,
    cargandoDetalle: false,
    errorConexion: null,
    modoDemo: false,
    _inicializado: false,
  }),

  getters: {
    /** Valores únicos para poblar el filtro de sedes de la vista. */
    sedes(state) {
      return [...new Set(state.fichas.map((f) => f.sede).filter(Boolean))].sort();
    },
  },

  actions: {
    /** Carga inicial completa (idempotente: solo la primera vez). */
    async initStore() {
      if (this._inicializado) return;
      this._inicializado = true;
      await this.cargarTodo();
    },

    /** Recarga fichas, indicadores y catálogos desde el backend. */
    async cargarTodo() {
      this.cargando = true;
      this.errorConexion = null;
      try {
        const [fichas, indicadores, instructores, ambientes, programas] = await Promise.all([
          tituladasService.getFichas(),
          tituladasService.getIndicadores(),
          tituladasService.getInstructores(),
          tituladasService.getAmbientes(),
          tituladasService.getProgramas(),
        ]);
        this.fichas = fichas;
        this.indicadores = indicadores;
        this.instructores = instructores;
        this.ambientes = ambientes;
        this.programas = programas;
        this.modoDemo = !!indicadores?.modo_demo;
      } catch (e) {
        this.errorConexion = e.message;
      } finally {
        this.cargando = false;
      }
    },

    /** Abre el detalle de una ficha (diagnóstico + calendario). */
    async cargarDetalle(fichaId) {
      this.cargandoDetalle = true;
      this.errorConexion = null;
      try {
        this.fichaActual = await tituladasService.getFicha(fichaId);
        return { success: true };
      } catch (e) {
        if (e.esConexion) this.errorConexion = e.message;
        return { success: false, error: e.message, noEncontrada: e.status === 404 };
      } finally {
        this.cargandoDetalle = false;
      }
    },

    /** Consulta el semáforo de instructores y ambientes para un rango. */
    async consultarDisponibilidad({ fichaId, fechaInicio, fechaFin, excluirAsignacion = null }) {
      try {
        const datos = await tituladasService.getDisponibilidad({
          fichaId, fechaInicio, fechaFin, excluirAsignacion,
        });
        return { success: true, datos };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },

    /** Tras crear/editar/eliminar se refresca TODO sin recargar la página:
     *  el calendario de la ficha, el listado y la carga de los instructores. */
    async _refrescarTrasCambio(fichaId) {
      await Promise.all([
        this.cargarDetalle(fichaId),
        this.cargarTodo(),
      ]);
    },

    async crearAsignacion(datos) {
      try {
        await tituladasService.createAsignacion(datos);
        await this._refrescarTrasCambio(datos.ficha_id);
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    async actualizarAsignacion(id, datos, fichaId) {
      try {
        await tituladasService.updateAsignacion(id, datos);
        await this._refrescarTrasCambio(fichaId);
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    async eliminarAsignacion(id, fichaId) {
      try {
        await tituladasService.deleteAsignacion(id);
        await this._refrescarTrasCambio(fichaId);
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },

    /** Alta de una ficha desde el catálogo de programas. Devuelve la ficha creada. */
    async crearFicha(datos) {
      try {
        const ficha = await tituladasService.createFicha(datos);
        await this.cargarTodo();
        return { success: true, ficha };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    /** Reemplaza la matriz de competencias (diagnóstico) de la ficha abierta. */
    async actualizarDiagnostico(fichaId, competencias) {
      try {
        this.fichaActual = await tituladasService.updateDiagnostico(fichaId, competencias);
        await this.cargarTodo();
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    /** Registra un programa en el catálogo. */
    async crearPrograma(datos) {
      try {
        const programa = await tituladasService.createPrograma(datos);
        this.programas.push(programa);
        return { success: true, programa };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    /** Sube un archivo de respaldo a la ficha abierta (el detalle se refresca). */
    async subirArchivo(fichaId, archivo) {
      try {
        await tituladasService.subirArchivoFicha(fichaId, archivo);
        await this.cargarDetalle(fichaId);
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },

    async eliminarArchivo(fichaId, archivoId) {
      try {
        await tituladasService.deleteArchivoFicha(fichaId, archivoId);
        await this.cargarDetalle(fichaId);
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },
  },
});
