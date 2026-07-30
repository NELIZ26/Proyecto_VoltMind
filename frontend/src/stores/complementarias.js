// src/stores/complementarias.js
// ─────────────────────────────────────────────────────────────────────────────
// Store del módulo de Fichas Complementarias (coordinador SENA).
//
// ✔ SIN datos mock: toda la información viene del backend FastAPI
//   (/api/complementarias/*), que decide entre Dataverse y modo demo.
// ✔ Las validaciones de negocio (fechas, ficha duplicada) son responsabilidad
//   del backend (HTTP 409/422); el store solo traduce el error para la UI.
// ─────────────────────────────────────────────────────────────────────────────
import { defineStore } from 'pinia';
import { complementariasService } from '@/services/complementariasService';

// Orden institucional del tablero: Pendiente → Publicada → En Ejecución → Cancelada
// ("Pendiente" = solicitud enviada por el instructor, aún sin gestión del admin)
export const ESTADOS_TABLERO = ['Pendiente', 'Publicada', 'En Ejecución', 'Cancelada'];

// Pasos del checklist de seguimiento (mismo orden que la matriz de Excel)
export const PASOS_SEGUIMIENTO = [
  { campo: 'publicacion', etiqueta: 'Publicación' },
  { campo: 'asignar_ficha', etiqueta: 'Asignación de ficha' },
  { campo: 'gestion_ficha', etiqueta: 'Gestión de ficha' },
  { campo: 'proceso_matricula', etiqueta: 'Proceso de matrícula' },
];

// Opciones institucionales compartidas por los selects/datalists del módulo
export const JORNADAS = ['Mañana', 'Tarde', 'Noche', 'Mixta'];
export const MUNICIPIOS_PUTUMAYO = [
  'Puerto Asís', 'Mocoa', 'Orito', 'Sibundoy',
  'Puerto Leguízamo', 'Valle del Guamuez', 'Puerto Caicedo', 'Villagarzón',
];

// Etiquetas de los archivos que sube el instructor (modal admin y ficha del instructor)
export const ETIQUETAS_ARCHIVO = {
  matriz: 'Matriz de la ficha',
  plano: 'Archivo plano de aprendices',
  adicional: 'Documento adicional',
};

/** Clase CSS del badge de estado (tarjetas del tablero y ficha del instructor). */
export const claseEstado = (estado) => {
  if (estado === 'Pendiente') return 'status-yellow';
  if (estado === 'Publicada') return 'status-blue';
  if (estado === 'En Ejecución') return 'status-green';
  if (estado === 'Cancelada') return 'status-red';
  return 'status-gray';
};

/** Cuántos pasos del checklist de seguimiento están completados. */
export const pasosCompletados = (solicitud) =>
  PASOS_SEGUIMIENTO.filter((p) => solicitud[p.campo]).length;

/** Rango "inicio → fin"; `vacio` es el texto cuando no hay ninguna fecha. */
export const formatearRango = (inicio, fin, vacio = 'Sin fechas') =>
  !inicio && !fin ? vacio : `${inicio || '—'} → ${fin || '—'}`;

export const useComplementariasStore = defineStore('complementarias', {
  state: () => ({
    solicitudes: [],
    indicadores: null,
    // Estado de UI
    cargando: false,
    errorConexion: null,
    modoDemo: false,
    _inicializado: false,
  }),

  getters: {
    /** Valores únicos para poblar los filtros de la vista. */
    municipios(state) {
      return [...new Set(state.solicitudes.map((s) => s.municipio).filter(Boolean))].sort();
    },
    instructores(state) {
      return [...new Set(state.solicitudes.map((s) => s.nombre_instructor).filter(Boolean))].sort();
    },
  },

  actions: {
    /** Carga inicial completa (idempotente: solo la primera vez). */
    async initStore() {
      if (this._inicializado) return;
      this._inicializado = true;
      await this.cargarTodo();
    },

    /** Recarga solicitudes e indicadores desde el backend. */
    async cargarTodo() {
      this.cargando = true;
      this.errorConexion = null;
      try {
        const [solicitudes, indicadores] = await Promise.all([
          complementariasService.getSolicitudes(),
          complementariasService.getIndicadores(),
        ]);
        this.solicitudes = solicitudes;
        this.indicadores = indicadores;
        this.modoDemo = !!indicadores?.modo_demo;
      } catch (e) {
        this.errorConexion = e.message;
      } finally {
        this.cargando = false;
      }
    },

    async crearSolicitud(datos) {
      try {
        await complementariasService.createSolicitud(datos);
        await this.cargarTodo();
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    async actualizarSolicitud(id, datos) {
      try {
        await complementariasService.updateSolicitud(id, datos);
        await this.cargarTodo();
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message, esConflicto: !!e.esConflicto };
      }
    },

    /** Adjunta el Excel de resultados de inscritos (flujo del administrador). */
    async subirResultados(id, archivo) {
      try {
        await complementariasService.subirResultados(id, archivo);
        await this.cargarTodo();
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },

    /** Reenvía el aviso de publicación al instructor y refresca la marca `notificado`. */
    async reenviarAviso(id) {
      try {
        const respuesta = await complementariasService.reenviarAviso(id);
        await this.cargarTodo();
        return { success: true, mensaje: respuesta.mensaje || 'Aviso reenviado al instructor.' };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },

    async eliminarSolicitud(id) {
      try {
        await complementariasService.deleteSolicitud(id);
        this.solicitudes = this.solicitudes.filter((s) => s.id !== id);
        await this.cargarTodo();
        return { success: true };
      } catch (e) {
        return { success: false, error: e.message };
      }
    },
  },
});
